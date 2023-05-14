import cv2
import mediapipe as mp
import time
import pyautogui

def dist(p1, p2):
    return pow(pow(p2.x - p1.x, 2) + pow(p2.y - p1.y, 2), 0.5)

WRIST = 0
THUMB_TIP = 4
INDEX_FINGER_PIP = 6
INDEX_FINGER_TIP = 8
MIDDLE_FINGER_MCP = 9
MIDDLE_FINGER_PIP = 10
MIDDLE_FINGER_TIP = 12
RING_FINGER_MCP = 13
RING_FINGER_PIP = 14
RING_FINGER_TIP = 16
PINKY_MCP = 17
PINKY_PIP = 18
PINKY_TIP = 20

capture = cv2.VideoCapture(0)
capture.set(3, 640)
capture.set(4, 480)

mp_hands = mp.solutions.hands
hands = mp_hands.Hands(min_detection_confidence=0.5,
                      min_tracking_confidence=0.5)
mp_draw = mp.solutions.drawing_utils

previousTime = 0
currentTime = 0

frame_clicks = 0
frame_pinches = 0
pinch_up = False
pinch_down = False
mouse_down = False
prev_landmarks = []

size_x, size_y = pyautogui.size()

while capture.isOpened():
    ret, frame = capture.read()
    frame = cv2.resize(frame, (2000, 1600))
    image = cv2.cvtColor(cv2.flip(frame, 1), cv2.COLOR_BGR2RGB)

    image.flags.writeable = False
    results = hands.process(image)
    image.flags.writeable = True

    image = cv2.cvtColor(image, cv2.COLOR_RGB2BGR)
    if results.multi_hand_landmarks:
        for hand_landmarks in results.multi_hand_landmarks:
            mp_draw.draw_landmarks(image, hand_landmarks, mp_hands.HAND_CONNECTIONS)

        num_hands = len(results.multi_hand_landmarks)
        right_landmarks = results.multi_hand_landmarks[num_hands - 1].landmark

        position = [right_landmarks[INDEX_FINGER_TIP].x, right_landmarks[INDEX_FINGER_TIP].y]
        pyautogui.moveTo(position[0]*(1.5)*size_x-0.25*size_x, position[1]*(1.6)*size_y-0.25*size_y)

        if num_hands > 1:
            left_landmarks = results.multi_hand_landmarks[0].landmark
            # if dist(left_landmarks[THUMB_TIP], left_landmarks[INDEX_FINGER_TIP]) < 0.035:
            #     pyautogui.rightClick()

            if dist(left_landmarks[INDEX_FINGER_TIP], left_landmarks[THUMB_TIP]) < 0.04:
                if frame_pinches >= 5:
                    if pinch_up:
                        pyautogui.scroll(120)
                    elif pinch_down:
                        pyautogui.scroll(-120)
                        
                elif frame_pinches < 2:

                    if prev_landmarks[0].landmark[THUMB_TIP].y < left_landmarks[THUMB_TIP].y:
                        pinch_down = True
                        pinch_up = False
                    else:
                        pinch_up = True
                        pinch_down = False

                frame_pinches += 1

            else:
                frame_pinches = 0
                pinch_up = False
                pinch_down = False


        if dist(right_landmarks[MIDDLE_FINGER_TIP], right_landmarks[THUMB_TIP]) < 0.03 and right_landmarks[MIDDLE_FINGER_TIP].y < right_landmarks[THUMB_TIP].y:
            frame_clicks += 1
            print(dist(right_landmarks[MIDDLE_FINGER_TIP], right_landmarks[THUMB_TIP]))

            # if frame_clicks > 2:
            #     if not mouse_down:
            #         mouse_down = True
            #         pyautogui.mouseDown()
            #     else:
            #         mouse_down = False
            #         frame_clicks = 0
            #         pyautogui.mouseUp()
            # elif mouse_down:
            #     mouse_down = False
            #     frame_clicks = 0
            #     pyautogui.mouseUp()
            # else:
            if frame_clicks == 1:
                pyautogui.click()

        else:
            frame_clicks = 0

        prev_landmarks = results.multi_hand_landmarks

    currentTime = time.time()
    fps = 1 / (currentTime - previousTime)
    previousTime = currentTime

    cv2.putText(image, str(int(fps)), (10, 70), cv2.FONT_HERSHEY_PLAIN, 3, (255, 0, 255), 3)

    cv2.imshow("Image", image)

    if cv2.waitKey(5) & 0xFF == ord('q'):
        break

capture.release()
cv2.destroyAllWindows()

