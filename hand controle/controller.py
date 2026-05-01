import pyautogui

class Controller:
    prev_hand = None
    right_clicked = False
    left_clicked = False
    double_clicked = False

    hand_Landmarks = None  # خليها كده عشان متطابقة مع اللي هتكتبه في app.py

    little_finger_down = None
    little_finger_up = None
    index_finger_down = None
    index_finger_up = None
    middle_finger_down = None
    middle_finger_up = None
    ring_finger_down = None
    ring_finger_up = None

    Thump_finger_down = None 
    Thump_finger_up = None

    all_fingers_down = None
    all_fingers_up = None

    index_finger_within_Thumb_finger = None
    middle_finger_within_Thumb_finger = None
    little_finger_within_Thumb_finger = None
    ring_finger_within_Thumb_finger = None

    screen_width, screen_height = pyautogui.size()

    # =========================
    def update_fingers_status(self):
        # Bonus: Add a condition to check if hand_Landmarks exists or not
        if Controller.hand_Landmarks is None:
            return
        
        lm = Controller.hand_Landmarks.landmark

        Controller.little_finger_down = lm[20].y > lm[17].y
        Controller.little_finger_up = lm[20].y < lm[17].y

        Controller.index_finger_down = lm[8].y > lm[5].y
        Controller.index_finger_up = lm[8].y < lm[5].y

        Controller.middle_finger_down = lm[12].y > lm[9].y
        Controller.middle_finger_up = lm[12].y < lm[9].y

        Controller.ring_finger_down = lm[16].y > lm[13].y
        Controller.ring_finger_up = lm[16].y < lm[13].y

        Controller.Thump_finger_down = lm[4].y > lm[13].y
        Controller.Thump_finger_up = lm[4].y < lm[13].y

        Controller.all_fingers_down = (
            Controller.index_finger_down and
            Controller.middle_finger_down and
            Controller.ring_finger_down and
            Controller.little_finger_down
        )

        Controller.all_fingers_up = (
            Controller.index_finger_up and
            Controller.middle_finger_up and
            Controller.ring_finger_up and
            Controller.little_finger_up
        )

        Controller.index_finger_within_Thumb_finger = lm[8].y > lm[4].y and lm[8].y < lm[2].y
        Controller.middle_finger_within_Thumb_finger = lm[12].y > lm[4].y and lm[12].y < lm[2].y
        Controller.little_finger_within_Thumb_finger = lm[20].y > lm[4].y and lm[20].y < lm[2].y
        Controller.ring_finger_within_Thumb_finger = lm[16].y > lm[4].y and lm[16].y < lm[2].y

    # =========================
    def get_position(self, hand_x, hand_y):
        old_x, old_y = pyautogui.position()

        current_x = int(hand_x * Controller.screen_width)
        current_y = int(hand_y * Controller.screen_height)

        Controller.prev_hand = (
            (current_x, current_y)
            if Controller.prev_hand is None
            else Controller.prev_hand
        )

        delta_x = current_x - Controller.prev_hand[0]
        delta_y = current_y - Controller.prev_hand[1]

        Controller.prev_hand = [current_x, current_y]

        current_x = old_x + delta_x
        current_y = old_y + delta_y

        threshold = 5

        current_x = max(threshold, min(current_x, Controller.screen_width - threshold))
        current_y = max(threshold, min(current_y, Controller.screen_height - threshold))

        return current_x, current_y

    # =========================
    def cursor_moving(self):
        if Controller.hand_Landmarks is None:
            return
            
        point = 9
        x = Controller.hand_Landmarks.landmark[point].x
        y = Controller.hand_Landmarks.landmark[point].y

        x, y = Controller.get_position(Controller, x, y)

        cursor_freezed = Controller.all_fingers_up and Controller.Thump_finger_down

        if not cursor_freezed:
            pyautogui.moveTo(x, y, duration=0)

    # =========================
    def detect_scrolling(self):
        if Controller.hand_Landmarks is None:
            return
            
        if Controller.little_finger_up and Controller.index_finger_down and Controller.middle_finger_down and Controller.ring_finger_down:
            pyautogui.scroll(120)
            print("Scrolling UP")

        if Controller.index_finger_up and Controller.middle_finger_down and Controller.ring_finger_down and Controller.little_finger_down:
            pyautogui.scroll(-120)
            print("Scrolling DOWN")

    # =========================
    def detect_zoomming(self):
        if Controller.hand_Landmarks is None:
            return
            
        zoom_pose = Controller.index_finger_up and Controller.middle_finger_up and Controller.ring_finger_down and Controller.little_finger_down

        window = 0.05
        lm = Controller.hand_Landmarks.landmark

        index_touches_middle = abs(lm[8].x - lm[12].x) <= window

        if zoom_pose and index_touches_middle:
            pyautogui.keyDown('ctrl')
            pyautogui.scroll(-50)
            pyautogui.keyUp('ctrl')
            print("Zoom Out")

        if zoom_pose and not index_touches_middle:
            pyautogui.keyDown('ctrl')
            pyautogui.scroll(50)
            pyautogui.keyUp('ctrl')
            print("Zoom In")

    # =========================
    def detect_clicking(self):
        if Controller.hand_Landmarks is None:
            return
            
        lm = Controller.hand_Landmarks.landmark

        left_click = (
            Controller.index_finger_within_Thumb_finger and
            Controller.middle_finger_up and
            Controller.ring_finger_up and
            Controller.little_finger_up
        )

        if not Controller.left_clicked and left_click:
            pyautogui.click()
            Controller.left_clicked = True
            print("Left Click")
        elif not Controller.index_finger_within_Thumb_finger:
            Controller.left_clicked = False

        right_click = (
            Controller.middle_finger_within_Thumb_finger and
            Controller.index_finger_up and
            Controller.ring_finger_up and
            Controller.little_finger_up
        )

        if not Controller.right_clicked and right_click:
            pyautogui.rightClick()
            Controller.right_clicked = True
            print("Right Click")
        elif not Controller.middle_finger_within_Thumb_finger:
            Controller.right_clicked = False

        double_click = (
            Controller.ring_finger_within_Thumb_finger and
            Controller.index_finger_up and
            Controller.middle_finger_up and
            Controller.little_finger_up
        )

        if not Controller.double_clicked and double_click:
            pyautogui.doubleClick()
            Controller.double_clicked = True
            print("Double Click")
        elif not Controller.ring_finger_within_Thumb_finger:
            Controller.double_clicked = False