import cv2
import time
import numpy as np
import Hand as htm
import math
import subprocess

camera_width, camera_height = 640, 480

cap = cv2.VideoCapture(0)
cap.set(3, camera_width)
cap.set(4, camera_height)

prev_time = 0

detector = htm.HandDetector(detectionCon=0.7)

def set_volume(volume):
    subprocess.run(["osascript", "-e", f'set volume output volume {volume}'])

def get_volume():
    result = subprocess.run(["osascript", "-e", 'output volume of (get volume settings)'], capture_output=True, text=True)
    return int(result.stdout.strip())

min_vol = 0
max_vol = 100
curr_vol = get_volume()


while True:
    success, img = cap.read()
    img = detector.findHands(img)
    lmList = detector.findPosition(img, draw=False)
    if len(lmList) != 0:
        # print(lmList[4], lmList[8]) # getting x,y pointer and middle finger tip values

        x1, y1 = lmList[4][1], lmList[4][2]
        x2, y2 = lmList[8][1], lmList[8][2]
        cx, cy = (x1 + x2)//2, (y1+y2)//2

        cv2.circle(img, (x1, y1), 15, (255, 0, 255), cv2.FILLED)
        cv2.circle(img, (x2, y2), 15, (255, 0, 255), cv2.FILLED)
        cv2.line(img, (x1, y1), (x2, y2), (255, 0, 255), 3)
        cv2.circle(img, (cx, cy), 15, (255, 0, 255), cv2.FILLED)

        length = math.hypot(x2-x1, y2-y1)
        if length < 50:
            cv2.circle(img, (cx, cy), 15, (0, 255, 0), cv2.FILLED)

        
        vol = np.interp(length, [50, 300], [min_vol, max_vol])
            
        set_volume(vol)


    curr_time = time.time()
    fps = 1/(curr_time - prev_time)
    prev_time = curr_time


    cv2.putText(img, f'FPS: {int(fps)}', (40, 50), 
                cv2.FONT_HERSHEY_COMPLEX, 1, (255, 0, 255), 3)

    cv2.imshow("Img", img)
    cv2.waitKey(1)