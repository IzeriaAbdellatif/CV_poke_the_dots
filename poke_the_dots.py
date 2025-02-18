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

# Function to generate random circle positions
def circle_coordinates(number_of_circles):
    positions = []
    for _ in range(number_of_circles):
        center_x = rand.randint(50, camera_width - 50)
        center_y = rand.randint(50, camera_height - 50)
        positions.append((center_x, center_y))
    return positions

# Function to compute Euclidean distance
def distance(p1, p2):
    return math.sqrt((p2[0] - p1[0])**2 + (p2[1] - p1[1])**2)

# Function to generate random colors
def random_color():
    return (rand.randint(100, 255), rand.randint(0, 155), rand.randint(100, 255))

# Game variables
game_state = "waiting"  # Can be "waiting", "running", or "game_over"
num_circles = rand.randint(5, 9)
circle_positions = []
circle_speeds = []
circle_colors = []
score = 0
start_time = 0
game_duration = 20

# Function to initialize the game
def reset_game():
    global score, start_time, circle_positions, circle_speeds, circle_colors, game_state
    score = 0
    start_time = time.time()
    num_circles = rand.randint(5, 9)
    circle_positions = circle_coordinates(num_circles)
    circle_speeds = [(rand.randint(-2, 2), rand.randint(-2, 2)) for _ in range(num_circles)]
    circle_colors = [random_color() for _ in range(num_circles)]
    game_state = "running"

# Main loop
while True:
    success, img = cap.read()
    if not success:
        continue

    img = detector.findHands(img)
    lmList = detector.findPosition(img, draw=False)

    # Show start menu
    if game_state == "waiting":
        img[:] = (0, 0, 0)  # Black background
        cv2.putText(img, "  Press 'S' to Start", (150, 200), cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 255, 255), 2)
        cv2.putText(img, "  Press 'E' to Exit", (150, 250), cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 255, 255), 2)

    # Game logic when running
    elif game_state == "running":
        elapsed_time = time.time() - start_time
        if elapsed_time >= game_duration:
            game_state = "game_over"

        if lmList:
            index_finger_tip = lmList[8][1], lmList[8][2]
            circles_to_remove = []

            for i, circle_pos in enumerate(circle_positions):
                if distance(index_finger_tip, circle_pos) < 25:
                    circles_to_remove.append(i)
                    score += 5

            for index in reversed(circles_to_remove):
                circle_positions.pop(index)
                circle_speeds.pop(index)
                circle_colors.pop(index)

                new_circles = circle_coordinates(rand.randint(1, 3))
                new_speeds = [(rand.randint(-2, 2), rand.randint(-2, 2)) for _ in range(len(new_circles))]
                new_colors = [random_color() for _ in range(len(new_circles))]

                circle_positions.extend(new_circles)
                circle_speeds.extend(new_speeds)
                circle_colors.extend(new_colors)

        for i, (x, y) in enumerate(circle_positions):
            dx, dy = circle_speeds[i]
            x += dx
            y += dy

            if x < 0 or x > camera_width:
                dx = -dx
            if y < 0 or y > camera_height:
                dy = -dy

            circle_positions[i] = (x, y)
            circle_speeds[i] = (dx, dy)
            cv2.circle(img, (x, y), 25, circle_colors[i], -1)

        cv2.putText(img, f"Score: {score}", (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2)
        cv2.putText(img, f"Time left: {int(game_duration - elapsed_time)}s", (10, 70), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2)

    # Game over screen
    elif game_state == "game_over":
        img[:] = (0, 0, 0)  # Black background
        cv2.putText(img, "Game Over", (170, 200), cv2.FONT_HERSHEY_SIMPLEX, 2, (0, 0, 255), 3)
        cv2.putText(img, f"Your Score: {score}", (200, 260), cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 255, 255), 2)
        cv2.putText(img, "Press 'R' to Replay", (200, 320), cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 255, 255), 2)
        cv2.putText(img, "Press  'E' to  Exit", (200, 360), cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 255, 255), 2)

    cv2.imshow("Poke the Dots", img)

    key = cv2.waitKey(1) & 0xFF
    if (key == ord("s") or key == ord("S")) and game_state == "waiting":
        reset_game()
    elif (key == ord("r") or key == ord("R")) and game_state == "game_over":
        reset_game()
    elif (key == ord("e") or key == ord("E")):
        break

cap.release()
cv2.destroyAllWindows()
