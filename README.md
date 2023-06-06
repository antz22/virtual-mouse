# VirtualMouse

VirtualMouse is a program that lets you control your computer / GUI using only hand gestures.

## Controls

- Cursor
Move the right index finger to control the cursor.

- Left click
Pinch right middle finger and thumb.

- Right click
Pinch left middle finger and thumb.

- Hold click
Press left thumb down, like pressing a button. Drag cursor to select content, then lift left thumb.

- Scroll
Pinch left index finger and thumb, and drag up / down to scroll up / down.

## Tools

VirtualMouse was built using OpenCV, Mediapipe, and Pyautogui.

OpenCV is used to open the webcam and process each live video frame. Mediapipe is used to process the image, detect hands, and draw the hand landmarks. Pyautogui is used to execute the necessary commands to the GUI or computer screen.