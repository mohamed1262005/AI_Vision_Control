import cv2
import mediapipe as mp
import pyautogui
import time
import math

def run_face_mouse():
    
    mp_face_mesh = mp.solutions.face_mesh
    face_mesh = mp_face_mesh.FaceMesh(
        min_detection_confidence=0.7,
        min_tracking_confidence=0.7,
        refine_landmarks=True
    )
    
    
    cap = cv2.VideoCapture(0)
    cap.set(cv2.CAP_PROP_FRAME_WIDTH, 1280)
    cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 720)
    
    sw, sh = pyautogui.size()
    
    def read_frame():
        ok, img = cap.read()
        return None if not ok else cv2.flip(img, 1)
    
    def show_message(t1, t2="", d=2, c=(0,0,255)):
        st = time.time()
        while time.time() - st < d:
            img = read_frame()
            if img is None: continue
            cv2.putText(img, t1, (60,200), cv2.FONT_HERSHEY_SIMPLEX, 1, c, 3)
            if t2:
                cv2.putText(img, t2, (60,250), cv2.FONT_HERSHEY_SIMPLEX, 0.9, (0,255,255), 2)
            cv2.imshow("Calibration", img)
            cv2.waitKey(1)
    
    def get_nose_and_landmarks(img):
        r = face_mesh.process(cv2.cvtColor(img, cv2.COLOR_BGR2RGB))
        if r.multi_face_landmarks:
            lm = r.multi_face_landmarks[0]
            return lm, lm.landmark[1]
        return None, None
    
    # ========== المعايرة ==========
    pos = {"CENTER":(0.5,0.5),"LEFT":(0.1,0.5),"RIGHT":(0.9,0.5),"UP":(0.5,0.1),"DOWN":(0.5,0.9)}
    X_THRESHOLD, Y_THRESHOLD = 0.03, 0.015
    calibration_data = {}
    direction_check = {
        "LEFT":lambda x,y,cx,cy: x < cx - X_THRESHOLD,
        "RIGHT":lambda x,y,cx,cy: x > cx + X_THRESHOLD,
        "UP":lambda x,y,cx,cy: y < cy - Y_THRESHOLD,
        "DOWN":lambda x,y,cx,cy: y > cy + Y_THRESHOLD
    }
    
    for label, (tx, ty) in pos.items():
        while True:
            xs, ys = [], []
            st = time.time()
            dur = 2.5
            
            while time.time() - st < dur:
                img = read_frame()
                if img is None: continue
                h, w, _ = img.shape
                cv2.circle(img, (int(tx*w), int(ty*h)), 18, (0,0,255), -1)
                rtime = round(dur - (time.time() - st), 1)
                cv2.putText(img, f"Look at RED DOT ({label})", (40,60), 0, 1, (0,255,0), 2)
                cv2.putText(img, f"Hold... {rtime}s", (40,110), 0, 1, (255,0,0), 2)
                
                _, nose = get_nose_and_landmarks(img)
                if nose:
                    xs.append(nose.x)
                    ys.append(nose.y)
                
                cv2.imshow("Calibration", img)
                cv2.waitKey(1)
            
            if len(xs) < 10:
                show_message("Face Not Detected!", "Make sure your face is visible")
                continue
            
            ax, ay = sum(xs)/len(xs), sum(ys)/len(ys)
            
            if label == "CENTER":
                calibration_data[label] = (ax, ay)
                show_message("CENTER Saved", "", 1, (0,255,0))
                break
            
            cx, cy = calibration_data["CENTER"]
            if not direction_check[label](ax, ay, cx, cy):
                show_message(f"{label} FAILED!", "Move clearly in that direction")
                continue
            
            calibration_data[label] = (ax, ay)
            show_message(f"{label} Saved", "", 1, (0,255,0))
            break
    
    show_message("Calibration Complete", "", 2, (0,255,0))
    
 
    min_x, _ = calibration_data["LEFT"]
    max_x, _ = calibration_data["RIGHT"]
    _, min_y = calibration_data["UP"]
    _, max_y = calibration_data["DOWN"]
    

    alpha_base = 10.0
    DEAD_ZONE = 25
    x = y = sw/2
    prev = time.time()
    last_l = last_r = 0
    blink_cooldown = 0.4
    EAR_T = 0.21
    
    lcf = rcf = bcf = 0
    DOUBLE = 3
    CONF = 3
    
    while cap.isOpened():
        img = read_frame()
        if img is None: continue
        
        now = time.time()
        dt = now - prev
        prev = now
        
        lm, nose = get_nose_and_landmarks(img)
        
        if nose:
            nx = (nose.x - min_x) / (max_x - min_x)
            ny = (nose.y - min_y) / (max_y - min_y)
            nx, ny = max(0, min(1, nx)), max(0, min(1, ny))
            
            tx, ty = nx * (sw - 1), ny * (sh - 1)
            dx, dy = tx - x, ty - y
            d = math.sqrt(dx*dx + dy*dy)
            
            if d > DEAD_ZONE:
                a = 1 - math.exp(-alpha_base * dt)
                x += a * dx
                y += a * dy
            
            pyautogui.moveTo(int(x), int(y))
            
            l = lm.landmark
            le = (abs(l[160].y - l[144].y) + abs(l[158].y - l[153].y)) / (2 * abs(l[33].x - l[133].x))
            re = (abs(l[385].y - l[380].y) + abs(l[387].y - l[373].y)) / (2 * abs(l[362].x - l[263].x))
            
            if le < EAR_T and re < EAR_T:
                bcf += 1
            else:
                bcf = 0
            if bcf >= DOUBLE:
                pyautogui.doubleClick()
                bcf = 0
            
            if le < EAR_T and re > EAR_T:
                lcf += 1
            else:
                lcf = 0
            if lcf >= CONF and now - last_l > blink_cooldown:
                pyautogui.click()
                last_l = now
                lcf = 0
            
            
            if re < EAR_T and le > EAR_T:
                rcf += 1
            else:
                rcf = 0
            if rcf >= CONF and now - last_r > blink_cooldown:
                pyautogui.rightClick()
                last_r = now
                rcf = 0
        
        cv2.imshow("Face Mouse Control", img)
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break
    
    
    cap.release()
    cv2.destroyAllWindows()


if __name__ == "__main__":
    run_face_mouse()