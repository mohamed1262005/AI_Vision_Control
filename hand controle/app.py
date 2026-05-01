import cv2
import mediapipe as mp
from controller import Controller

cap = cv2.VideoCapture(0)

def run_loop(cap, Controller):
    hands = mp.solutions.hands.Hands()
    mp_draw = mp.solutions.drawing_utils

    while True:
        success, img = cap.read()
        if not success:
            break
            
        img = cv2.flip(img, 1)
        imgRGB = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
        results = hands.process(imgRGB)

        if results.multi_hand_landmarks:
            Controller.hand_Landmarks = results.multi_hand_landmarks[0]  # استخدم نفس الاسم hand_Landmarks

            mp_draw.draw_landmarks(
                img,
                Controller.hand_Landmarks,
                mp.solutions.hands.HAND_CONNECTIONS
            )

            Controller.update_fingers_status(Controller)  # مرر Controller
            Controller.cursor_moving(Controller)
            Controller.detect_scrolling(Controller)
            Controller.detect_zoomming(Controller)
            Controller.detect_clicking(Controller)

        cv2.imshow("Hand Tracker", img)

        if cv2.waitKey(5) & 0xFF == 27:
            break

run_loop(cap, Controller)