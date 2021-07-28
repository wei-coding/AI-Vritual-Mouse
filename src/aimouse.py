import cv2
import numpy as np
import handtrackingmodule as htm
import time
import pyautogui as pgui
import threading

W_CAM, H_CAM = 640, 480
FRAME_R = 100

pTime = 0
cap = cv2.VideoCapture(0)
cap.set(cv2.CAP_PROP_FRAME_WIDTH, W_CAM)
cap.set(cv2.CAP_PROP_FRAME_HEIGHT, H_CAM)
x4, y4 = 0, 0
detector = htm.handDetector(0.5, 0.5)
W_SCR, H_SCR = pgui.size()
print(W_SCR, H_SCR)

class MouseController(threading.Thread):
    def __init__(self):
        threading.Thread.__init__(self)
        self.x, self.y = pgui.position()

    def run(self):
        while True:
            try:
                pgui.moveTo(self.x, self.y, duration=0.01)
            except KeyboardInterrupt:
                break

mouse = MouseController()
mouse.start()

while True:
    # 1. capture the image, find hand lm
    success, img = cap.read()
    img = cv2.flip(img, 1)
    img = detector.find_hands(img)
    lm_list, bbox = detector.find_positions(img)

    # 2. get tips of index(食) and middle finger
    if len(lm_list) != 0:
        x1, y1 = lm_list[8][1:]
        x2, y2 = lm_list[12][1:]

        # 3. check which fingers are up
        fingers = detector.fingers_up()
        print(fingers)
        # 4. if index finger: move the pointer
        if fingers[1] and not fingers[2]:
            # 5. convert coordinates(from cam to screen)
            cv2.rectangle(img, (FRAME_R, FRAME_R), (W_CAM - FRAME_R, H_CAM - FRAME_R), (255, 0, 255), 2)
            x3 = np.interp(x1, (FRAME_R, W_CAM - FRAME_R), (0, W_SCR))
            y3 = np.interp(y1, (FRAME_R, H_CAM - FRAME_R), (0, H_SCR))
            # 6. smoothen
            x4 = x3 * 0.8 + x4 * 0.2
            y4 = y3 * 0.8 + y4 * 0.2
            # 7. move the pointer
            # pgui.moveTo(x4, y4)
            mouse.x = x4
            mouse.y = y4
            cv2.circle(img, (x1, y1), 15, (255, 0, 255), cv2.FILLED)
        # 8. index and middle finger: click
        elif fingers[1] and fingers[2] and not (fingers[0] and fingers[3] and fingers[4]):
            # 9. distance between index and middle
            distance, img, _ = detector.find_distance(8, 12, img)
            print(distance)
            # 10. if distance < ?: click
            if distance < 30:
                pgui.leftClick(interval=0.01)
    # 11. frame rate
    cTime = time.time()
    fps = 1 / (cTime - pTime)
    pTime = cTime
    cv2.putText(img, f'fps:{str(int(fps))}', (20, 50), cv2.FONT_HERSHEY_PLAIN, 3, (255, 0, 0))
    # 12. display
    cv2.imshow('image', img)
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break
        
