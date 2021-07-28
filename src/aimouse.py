import cv2
import numpy as np
import handtrackingmodule as htm
import time
import pyautogui as pgui

W_CAM, H_CAM = 640, 480

pTime = 0
cap = cv2.VideoCapture(0)
cap.set(3, W_CAM)
cap.set(4, H_CAM)
detector = htm.handDetector()

while True:
    try:
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
        # 5. convert coordinates(from cam to screen)
        # 6. smoothen
        # 7. move the pointer
        # 8. index and middle finger: click
        # 9. distance between index and middle
        # 10. if distance < ?: click
        # 11. frame rate
        cTime = time.time()
        fps = 1 / (cTime - pTime)
        pTime = cTime
        cv2.putText(img, f'fps:{str(int(fps))}', (20, 50), cv2.FONT_HERSHEY_DUPLEX, 1, (255, 0, 0))
        # 12. display
        cv2.imshow('image', img)
        cv2.waitKey(1)
    except KeyboardInterrupt:
        raise Exception('Exit by user')
