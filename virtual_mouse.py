from utils import dist
from hand_coord import HandCoord
import pyautogui
import cv2
import mediapipe as mp
import time



class VirtualMouse:
    """
    Python class to control user GUI based on user hand controls, processed by the opencv and mediapipe libraries
    """
    def __init__(self):
        self.frame_clicks = 0
        self.frame_pinches = 0
        self.pinch_up = False
        self.pinch_down = False
        self.mouse_down = False
        self.prev_landmarks = []

        self.size_x, self.size_y = pyautogui.size()

        self.capture = cv2.VideoCapture(0)
        self.capture.set(3, 3000)
        self.capture.set(4, 1600)

        pyautogui.FAILSAFE = False

        self.mp_hands = mp.solutions.hands
        self.mp_draw = mp.solutions.drawing_utils
        self.hands = self.mp_hands.Hands(min_detection_confidence=0.5,
                                         min_tracking_confidence=0.5)

    def start(self):
        # configure frame from video feed
        ret, frame = self.capture.read()
        # frame = cv2.resize(frame, (2000, 1600))
        image = cv2.cvtColor(cv2.flip(frame, 1), cv2.COLOR_BGR2RGB)

        # process mapping of hands from frame
        image.flags.writeable = False
        results = self.hands.process(image)
        image.flags.writeable = True
        image = cv2.cvtColor(image, cv2.COLOR_RGB2BGR)
        return image, results


    def track_cursor(self, right_landmarks):
        # find x and y coords of tip of index finger
        position = [right_landmarks[HandCoord.INDEX_FINGER_TIP].x, right_landmarks[HandCoord.INDEX_FINGER_TIP].y]

        # move cursor to the x and y coords - extra range of motion added to increase sensitivity
        pyautogui.moveTo(position[0]*(1.5)*self.size_x-0.25*self.size_x, position[1]*(1.6)*self.size_y-0.25*self.size_y)

    def track_left_click(self, right_landmarks):

        # if the right hand's middle finger and thumb are 
        # touching and the middle finger is above the thumb
        if dist(right_landmarks[HandCoord.MIDDLE_FINGER_TIP], right_landmarks[HandCoord.THUMB_TIP]) < 0.03 and right_landmarks[HandCoord.MIDDLE_FINGER_TIP].y < right_landmarks[HandCoord.THUMB_TIP].y:
            print("LEFT CLICK")
            pyautogui.click()

    def track_right_click(self, left_landmarks):

        # if the left and right hand's middle and thumb fingers are pinched
        if dist(left_landmarks[HandCoord.MIDDLE_FINGER_TIP], left_landmarks[HandCoord.THUMB_TIP]) < 0.03 and left_landmarks[HandCoord.MIDDLE_FINGER_TIP].y < left_landmarks[HandCoord.THUMB_TIP].y:
            print("RIGHT CLICK")
            pyautogui.rightClick()

    def track_hold_click(self, left_landmarks, right_landmarks):

        # if thumb is pressed against first joint of index finger
        # and thumb is higher than the index finger
        is_left_thumb_pressed = dist(left_landmarks[HandCoord.INDEX_FINGER_PIP], left_landmarks[HandCoord.THUMB_TIP]) < 0.026
        is_left_hand_closed = left_landmarks[HandCoord.INDEX_FINGER_PIP].y > left_landmarks[HandCoord.THUMB_TIP].y

        if is_left_thumb_pressed and is_left_hand_closed:

            self.frame_clicks += 1
            print(dist(left_landmarks[HandCoord.INDEX_FINGER_PIP], left_landmarks[HandCoord.THUMB_TIP]))
            print("LEFT AND RIGHT PINCH")

            if self.frame_clicks > 2 and not self.mouse_down:
                self.mouse_down = True
                pyautogui.mouseDown()

        elif self.mouse_down:
            self.mouse_down = False
            self.frame_clicks = 0
            pyautogui.mouseUp()

        else:
            self.frame_clicks = 0


    def track_scrolling(self, left_landmarks):

        # left index finger and thumb are pinched together
        if dist(left_landmarks[HandCoord.INDEX_FINGER_TIP], left_landmarks[HandCoord.THUMB_TIP]) < 0.04:

            # if pinch has been held for more than 5 frames
            if self.frame_pinches >= 5:
                if self.pinch_up:
                    pyautogui.scroll(120)
                elif self.pinch_down:
                    pyautogui.scroll(-120)
                    
            elif self.frame_pinches < 2:

                # discover if the pinch is moved up or down
                if self.prev_landmarks[0].landmark[HandCoord.THUMB_TIP].y < left_landmarks[HandCoord.THUMB_TIP].y:
                    self.pinch_down = True
                    self.pinch_up = False
                else:
                    self.pinch_up = True
                    self.pinch_down = False

            self.frame_pinches += 1

        else:
            self.frame_pinches = 0
            self.pinch_up = False
            self.pinch_down = False

    def run(self):
        previousTime = 0
        currentTime = 0

        while self.capture.isOpened():

            # process image and hand mappings from video frame
            image, results = self.start()

            if results.multi_hand_landmarks:
                # draw detected hands
                for hand_landmarks in results.multi_hand_landmarks:
                    self.mp_draw.draw_landmarks(image, hand_landmarks, self.mp_hands.HAND_CONNECTIONS)

                num_hands = len(results.multi_hand_landmarks)
                right_landmarks = results.multi_hand_landmarks[num_hands - 1].landmark

                # control position of mouse
                self.track_cursor(right_landmarks)

                # control left click
                self.track_left_click(right_landmarks)

                # if left hand exists
                if num_hands > 1:
                    left_landmarks = results.multi_hand_landmarks[0].landmark

                    # control scrolling through pinch
                    self.track_scrolling(left_landmarks)

                    # control right click
                    self.track_right_click(left_landmarks)

                    # control hold click through pinches
                    self.track_hold_click(left_landmarks, right_landmarks)

                self.prev_landmarks = results.multi_hand_landmarks

            # calculate and display fps
            currentTime = time.time()
            fps = 1 / (currentTime - previousTime)
            previousTime = currentTime
            cv2.putText(image, str(int(fps)), (10, 70), cv2.FONT_HERSHEY_PLAIN, 3, (255, 0, 255), 3)

            cv2.imshow("Image", image)

            if cv2.waitKey(5) & 0xFF == ord('q'):
                break

        self.capture.release()
        cv2.destroyAllWindows()


