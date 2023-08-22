import cv2
import Hand as htm
import random as rand
import math
import time

# Set screen dimensions
camera_width, camera_height = 640, 480
cap = cv2.VideoCapture(0)
cap.set(3, camera_width)
cap.set(4, camera_height)

detector = htm.HandDetector(detectionCon=0.7)

def circle_coordinates(number_of_circles):
    positions = []
    for _ in range(number_of_circles):
        center_x = rand.randint(0, camera_width)
        center_y = rand.randint(0, camera_height)
        positions.append((center_x, center_y))
    return positions

def distance(p1, p2):
    return math.sqrt((p2[0] - p1[0])**2 + (p2[1] - p1[1])**2)

def random_color():
    return (rand.randint(100, 255), rand.randint(0, 155), rand.randint(100, 255))

num_circles = rand.randint(0, 9)
circle_positions = circle_coordinates(num_circles)
circle_speeds = [(rand.randint(-2, 2), rand.randint(-2, 2)) for _ in range(num_circles)]
circle_colors = [random_color() for _ in range(num_circles)]

score = 0
start_time = time.time()
game_duration = 20  

game_over = False

while True:
    current_time = time.time()
    elapsed_time = current_time - start_time

    if elapsed_time >= game_duration:
        game_over = True

    success, img = cap.read()
    img = detector.findHands(img)
    lmList = detector.findPosition(img, draw=False)

    if not game_over:
        if lmList and len(circle_positions) > 0:
            index_finger_tip = lmList[8][1], lmList[8][2]
            circles_to_remove = []

            for i, circle_pos in enumerate(circle_positions):
                circle_center = circle_pos
                dist = distance(index_finger_tip, circle_center)

                if dist < 25:
                    circles_to_remove.append(i)
                    score += 5

            for index in reversed(circles_to_remove):
                circle_positions.pop(index)
                circle_speeds.pop(index)
                circle_colors.pop(index)

                num_new_circles = rand.randint(1, 3)  
                new_circle_positions = circle_coordinates(num_new_circles)
                new_circle_speeds = [(rand.randint(-2, 2), rand.randint(-2, 2)) for _ in range(num_new_circles)]
                new_circle_colors = [random_color() for _ in range(num_new_circles)]
                circle_positions.extend(new_circle_positions)
                circle_speeds.extend(new_circle_speeds)
                circle_colors.extend(new_circle_colors)

        for i, circle_pos in enumerate(circle_positions):
            center_x, center_y = circle_pos
            speed_x, speed_y = circle_speeds[i]

            center_x += speed_x
            center_y += speed_y

            if center_x < 0 or center_x > camera_width:
                speed_x = -speed_x
            if center_y < 0 or center_y > camera_height:
                speed_y = -speed_y

            circle_positions[i] = (center_x, center_y)
            radius = 25
            color = circle_colors[i]
            thickness = -1
            cv2.circle(img, (center_x, center_y), radius, color, thickness)

        cv2.putText(img, f"Score: {score}", (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2)
        cv2.putText(img, f"Time left: {int(game_duration - elapsed_time)}", (10, 70), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2)
    else:
        text = "Game Over"
        text_size = cv2.getTextSize(text, cv2.FONT_HERSHEY_SIMPLEX, 2, 4)[0]
        text_x = (camera_width - text_size[0]) // 2
        text_y = (camera_height + text_size[1]) // 2
        cv2.putText(img, text, (text_x, text_y), cv2.FONT_HERSHEY_SIMPLEX, 2, (0, 0, 255), 4)

        score_text = f"Your Score: {score}"
        score_text_size = cv2.getTextSize(score_text, cv2.FONT_HERSHEY_SIMPLEX, 1, 2)[0]
        score_text_x = (camera_width - score_text_size[0]) // 2
        score_text_y = text_y + text_size[1] + 20
        cv2.putText(img, score_text, (score_text_x, score_text_y), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 255), 2)

    cv2.imshow("Img", img)
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

cap.release()
cv2.destroyAllWindows()
