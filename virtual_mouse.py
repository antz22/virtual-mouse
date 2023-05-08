import cv2
import mediapipe as mp
import time
import pyautogui

capture = cv2.VideoCapture(0)

mp_hands = mp.solutions.hands
hands = mp_hands.Hands(min_detection_confidence=0.5,
                      min_tracking_confidence=0.5)
mp_draw = mp.solutions.drawing_utils

previousTime = 0
currentTime = 0

size_x, size_y = pyautogui.size()

while capture.isOpened():
    ret, frame = capture.read()
    frame = cv2.resize(frame, (1500, 1200))
    image = cv2.cvtColor(cv2.flip(frame, 1), cv2.COLOR_BGR2RGB)

    image.flags.writeable = False
    results = hands.process(image)
    image.flags.writeable = True

    image = cv2.cvtColor(image, cv2.COLOR_RGB2BGR)
    if results.multi_hand_landmarks:
        for hand_landmarks in results.multi_hand_landmarks:
            mp_draw.draw_landmarks(image, hand_landmarks, mp_hands.HAND_CONNECTIONS)

        index_point = 8
        position = [results.multi_hand_landmarks[0].landmark[index_point].x ,results.multi_hand_landmarks[0].landmark[index_point].y]
        pyautogui.moveTo(position[0]*(1.4)*size_x-0.2*size_x, position[1]*(1.4)*size_y-0.2*size_y)

    currentTime = time.time()
    fps = 1 / (currentTime - previousTime)
    previousTime = currentTime

    cv2.putText(image, str(int(fps)), (10, 70), cv2.FONT_HERSHEY_PLAIN, 3, (255, 0, 255), 3)

    cv2.imshow("Image", image)

    if cv2.waitKey(5) & 0xFF == ord('q'):
        break

capture.release()
cv2.destroyAllWindows()