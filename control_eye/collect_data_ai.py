import cv2
import mediapipe as mp
import numpy as np
import os
import time

# 1. إعدادات المجلد والترقيم التلقائي
folder = 'eye_dataset'
if not os.path.exists(folder):
    os.makedirs(folder)

# البحث عن آخر رقم صورة موجود عشان نكمل عليه
existing_files = [f for f in os.listdir(folder) if f.startswith("img_")]
last_count = max([int(f.split('_')[1]) for f in existing_files]) if existing_files else -1
count = last_count + 1

# 2. إعداد Mediapipe
mp_face_mesh = mp.solutions.face_mesh
face_mesh = mp_face_mesh.FaceMesh(refine_landmarks=True)

# 3. إعداد الشاشة (Fullscreen)
cv2.namedWindow("Collection", cv2.WND_PROP_FULLSCREEN)
cv2.setWindowProperty("Collection", cv2.WND_PROP_FULLSCREEN, cv2.WINDOW_FULLSCREEN)

cap = cv2.VideoCapture(0)
# دقة الكاميرا (تأكد إنها عالية لو أمكن)
cap.set(3, 1280)
cap.set(4, 720)

# الحصول على أبعاد الشاشة الحقيقية
screen_w = 1920 
screen_h = 1080 

max_images_to_add = 500 
target_total = count + max_images_to_add

print(f"بدء التجميع من الصورة رقم {count}. اتبع النقطة بتركيز...")

# متغيرات حركة النقطة السلسة
dot_x, dot_y = screen_w // 2, screen_h // 2
speed_x, speed_y = 10, 10

while count < target_total:
    success, frame = cap.read()
    if not success: break
    
    frame = cv2.flip(frame, 1)
    h, w, _ = frame.shape
    
    # تحريك النقطة بأسلوب "الكرة الارتدادية" لتغطية الشاشة ببطء وسلاسة
    dot_x += speed_x
    dot_y += speed_y
    
    if dot_x <= 50 or dot_x >= screen_w - 50: speed_x *= -1
    if dot_y <= 50 or dot_y >= screen_h - 50: speed_y *= -1

    # إنشاء شاشة سوداء تماماً للنقطة
    bg = np.zeros((screen_h, screen_w, 3), dtype=np.uint8)
    cv2.circle(bg, (dot_x, dot_y), 20, (255, 255, 255), -1) # النقطة البيضاء
    cv2.putText(bg, f"Progress: {count}/{target_total} (Added: {count-(last_count+1)})", 
                (50, 50), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2)
    
    cv2.imshow("Collection", bg)
    
    # معالجة العين
    results = face_mesh.process(cv2.cvtColor(frame, cv2.COLOR_BGR2RGB))
    
    if results.multi_face_landmarks:
        # نقطة القزحية
        pt = results.multi_face_landmarks[0].landmark[468]
        ex, ey = int(pt.x * w), int(pt.y * h)
        
        # قص منطقة العين 64x64
        y1, y2 = max(0, ey-32), min(h, ey+32)
        x1, x2 = max(0, ex-32), min(w, ex+32)
        roi = frame[y1:y2, x1:x2]
        
        if roi.shape[0] == 64 and roi.shape[1] == 64:
            # حفظ الصورة بتوسيم إحداثيات الشاشة (dot_x, dot_y)
            img_name = f"{folder}/img_{count}_{dot_x}_{dot_y}.jpg"
            cv2.imwrite(img_name, cv2.cvtColor(roi, cv2.COLOR_BGR2GRAY))
            count += 1

    # مخرج الطوارئ
    if cv2.waitKey(1) & 0xFF == 27: break

cap.release()
cv2.destroyAllWindows()
print(f"تم الانتهاء! إجمالي الصور في الفولدر الآن: {count}")