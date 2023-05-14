from utils import dist
from hand_coord import HandCoord
import pyautogui
import cv2
import mediapipe as mp
import time



class VirtualMouse:
    def __init__(self):
        self.frame_clicks = 0
        self.frame_pinches = 0
        self.pinch_up = False
        self.pinch_down = False
        self.mouse_down = False
        self.prev_landmarks = []

        self.size_x, self.size_y = pyautogui.size()

        self.capture = cv2.VideoCapture(0)
        self.capture.set(3, 2000)
        self.capture.set(4, 1600)

        pyautogui.FAILSAFE = False

        self.mp_hands = mp.solutions.hands
        self.mp_draw = mp.solutions.drawing_utils
        self.hands = self.mp_hands.Hands(min_detection_confidence=0.5,
                                         min_tracking_confidence=0.5)

    def start(self):
        while self.capture.isOpened():

            ret, frame = self.capture.read()
            frame = cv2.resize(frame, (2000, 1600))
            image = cv2.cvtColor(cv2.flip(frame, 1), cv2.COLOR_BGR2RGB)

            image.flags.writeable = False
            results = self.hands.process(image)
            image.flags.writeable = True

            image = cv2.cvtColor(image, cv2.COLOR_RGB2BGR)
            if results.multi_hand_landmarks:
                for hand_landmarks in results.multi_hand_landmarks:
                    self.mp_draw.draw_landmarks(image, hand_landmarks, self.mp_hands.HAND_CONNECTIONS)

                num_hands = len(results.multi_hand_landmarks)
                right_landmarks = results.multi_hand_landmarks[num_hands - 1].landmark

                position = [right_landmarks[HandCoord.INDEX_FINGER_TIP].x, right_landmarks[HandCoord.INDEX_FINGER_TIP].y]
                pyautogui.moveTo(position[0]*(1.5)*self.size_x-0.25*self.size_x, position[1]*(1.6)*self.size_y-0.25*self.size_y)

                if num_hands > 1:
                    left_landmarks = results.multi_hand_landmarks[0].landmark
                    # if dist(left_landmarks[THUMB_TIP], left_landmarks[INDEX_FINGER_TIP]) < 0.035:
                    #     pyautogui.rightClick()

                    if dist(left_landmarks[HandCoord.INDEX_FINGER_TIP], left_landmarks[HandCoord.THUMB_TIP]) < 0.04:
                        if frame_pinches >= 5:
                            if pinch_up:
                                pyautogui.scroll(120)
                            elif pinch_down:
                                pyautogui.scroll(-120)
                                
                        elif frame_pinches < 2:

                            if prev_landmarks[0].landmark[HandCoord.THUMB_TIP].y < left_landmarks[HandCoord.THUMB_TIP].y:
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


                if dist(right_landmarks[HandCoord.MIDDLE_FINGER_TIP], right_landmarks[HandCoord.THUMB_TIP]) < 0.03 and right_landmarks[HandCoord.MIDDLE_FINGER_TIP].y < right_landmarks[HandCoord.THUMB_TIP].y:
                    frame_clicks += 1
                    print(dist(right_landmarks[HandCoord.MIDDLE_FINGER_TIP], right_landmarks[HandCoord.THUMB_TIP]))

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

        self.capture.release()
        cv2.destroyAllWindows()


