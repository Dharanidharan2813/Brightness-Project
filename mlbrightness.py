import cv2
import time
import math
import numpy as np
import mediapipe as mp
import screen_brightness_control as sbc

cap = cv2.VideoCapture(0)
cap.set(3, 640)
cap.set(4, 480)

mpHands = mp.solutions.hands
hands = mpHands.Hands()
mpDraw = mp.solutions.drawing_utils

pTime, cTime = 0, 0

brightness, brightnessBar, brightnessPer = 0, 0, 0

while True:
    success, img = cap.read()
    if not success:
        break

    imgRGB = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
    results = hands.process(imgRGB)

    if results.multi_hand_landmarks:
        for handLms in results.multi_hand_landmarks:
            lmList = []
            for id, lm in enumerate(handLms.landmark):
                h, w, c = img.shape
                cx, cy = int(lm.x * w), int(lm.y * h)
                lmList.append([id, cx, cy])

            if lmList:
                x1, y1 = lmList[4][1], lmList[4][2]
                x2, y2 = lmList[8][1], lmList[8][2]
                cx, cy = (x1 + x2) // 2, (y1 + y2) // 2

                cv2.circle(img, (x1, y1), 10, (0, 255, 0), cv2.FILLED)
                cv2.circle(img, (x2, y2), 10, (0, 255, 0), cv2.FILLED)
                cv2.line(img, (x1, y1), (x2, y2), (0, 255, 0), 3)
                cv2.circle(img, (cx, cy), 10, (0, 255, 0), cv2.FILLED)

                length = math.hypot(x2 - x1, y2 - y1)

                brightnessBar = np.interp(length, [50, 150], [400, 150])
                brightnessPer = np.interp(length, [50, 150], [0, 100])
                brightness = np.interp(length, [50, 150], [0, 100])

                sbc.set_brightness(int(brightness))

                cv2.rectangle(img, (50, 150), (85, 400), (0, 255, 0), 3)
                cv2.rectangle(img, (50, int(brightnessBar)), (85, 400), (0, 255, 0), cv2.FILLED)
                cv2.putText(img, f'{int(brightnessPer)} %', (40, 450), cv2.FONT_HERSHEY_PLAIN, 3, (0, 255, 0), 2)

                if length < 50:
                    cv2.circle(img, (cx, cy), 10, (0, 255, 255), cv2.FILLED)

            mpDraw.draw_landmarks(img, handLms, mpHands.HAND_CONNECTIONS)

    cTime = time.time()
    fps = int(1 // (cTime - pTime)) if cTime - pTime > 0 else 0
    pTime = cTime
    cv2.putText(img, f'FPS: {fps}', (40, 70), cv2.FONT_HERSHEY_PLAIN, 3, (0, 0, 0), 2)

    cv2.imshow('Image', img)

    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

cap.release()
cv2.destroyAllWindows()
