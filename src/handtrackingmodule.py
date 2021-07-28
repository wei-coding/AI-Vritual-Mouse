import mediapipe as mp
import cv2
import numpy as np
import math
import time

class handDetector:
    def __init__(self, detection_confidence=0.3, tracking_confidence=0.3):
        self.mp_hands = mp.solutions.hands
        self.mp_drawing = mp.solutions.drawing_utils
        self.hands = self.mp_hands.Hands(
            max_num_hands = 1,
            min_detection_confidence = detection_confidence,
            min_tracking_confidence = tracking_confidence)
        self.tip_ids = [4, 8, 12, 16, 20]
        self.results = None

    def find_hands(self, img, draw: bool=True):
        self.results = self.hands.process(img)
        if draw:
            if self.results.multi_hand_landmarks:
                for hand_lms in self.results.multi_hand_landmarks:
                    self.mp_drawing.draw_landmarks(
                        img, hand_lms, self.mp_hands.HAND_CONNECTIONS)
        return img

    def find_positions(self, img: np.ndarray, draw: bool=True):
        x_list = []
        y_list = []
        self.lm_list = []
        bbox = ()
        if self.results.multi_hand_landmarks:
            my_hand = self.results.multi_hand_landmarks[0]
            for id, lm in enumerate(my_hand.landmark):
                h, w, c = img.shape
                cx, cy = int(lm.x * w), int(lm.y * h)
                x_list.append(cx)
                y_list.append(cy)
                self.lm_list.append((id, cx, cy))
                if draw:
                    cv2.circle(img, (cx, cy), 5, (255, 0, 255), cv2.FILLED)
            xmin, xmax = min(x_list), max(x_list)
            ymin, ymax = min(y_list), max(y_list)
            bbox = (xmin, ymin, xmax, ymax)

            if draw:
                cv2.rectangle(img, (xmin - 20, ymin - 20), (xmax + 20, ymax + 20), (0, 255, 0), 2)

        return self.lm_list, bbox

    def fingers_up(self):
        fingers = []
        # Thumb
        if self.lm_list[self.tip_ids[0]][1] > self.lm_list[self.tip_ids[0] - 1][1]:
            fingers.append(1)
        else:
            fingers.append(0)

        # Fingers
        for id in range(1, 5):

            if self.lm_list[self.tip_ids[id]][2] < self.lm_list[self.tip_ids[id] - 2][2]:
                fingers.append(1)
            else:
                fingers.append(0)

        # totalFingers = fingers.count(1)

        return fingers

    def find_distance(self, p1, p2, img, draw: bool=True, r=15, t=3):
        x1, y1 = self.lm_list[p1][1:]
        x2, y2 = self.lm_list[p2][1:]
        cx, cy = (x1 + x2) // 2, (y1 + y2) // 2

        if draw:
            cv2.line(img, (x1, y1), (x2, y2), (255, 0, 255), t)
            cv2.circle(img, (x1, y1), r, (255, 0, 255), cv2.FILLED)
            cv2.circle(img, (x2, y2), r, (255, 0, 255), cv2.FILLED)
            cv2.circle(img, (cx, cy), r, (0, 0, 255), cv2.FILLED)
        length = math.hypot(x2 - x1, y2 - y1)

        return length, img, [x1, y1, x2, y2, cx, cy]

def main():
    pTime = 0
    cTime = 0
    cap = cv2.VideoCapture(0)
    detector = handDetector()
    while True:
        _, img = cap.read()
        img = cv2.flip(img, 1)
        img = detector.find_hands(img)
        lmList, bbox = detector.find_positions(img)
        if len(lmList) != 0:
            print(lmList[4])

        cTime = time.time()
        fps = 1 / (cTime - pTime)
        pTime = cTime

        cv2.putText(img, str(int(fps)), (10, 70), cv2.FONT_HERSHEY_PLAIN, 3,
                    (255, 0, 255), 3)

        cv2.imshow("Image", img)
        cv2.waitKey(1)

if __name__ == '__main__':
    main()