import cv2
import time
from ultralytics import YOLO
from pydobot import Dobot

PORT = '/dev/tty.usbmodem389438CC04312'

FIXED_PICK_X = 261.3
FIXED_PICK_Y = 6.9

Z_SAFE = 20.0
Z_PICK = -58.1
Z_PLACE = -55.0

SCAN_POS_X, SCAN_POS_Y, SCAN_POS_Z = 200.0, 0.0, Z_SAFE

PALLET_A = {'x': 288.4, 'y': -104.2, 'z': Z_PLACE} # Food
PALLET_B = {'x': 296.6, 'y': 94.1,   'z': Z_PLACE} # Vehicle

FOOD_CLASSES = ['apple', 'banana', 'pizza']
VEHICLE_CLASSES = ['car', 'bicycle', 'airplane']

try:
    print(f"conecting")
    device = Dobot(port=PORT)
    print("connected")
except Exception as e:
    print(f"fail")
    exit()

def move_wait(x, y, z, timeout=5.0):
    device.move_to(x, y, z)
    start_time = time.time()
    
    while time.time() - start_time < timeout:
        try:
            p = device.get_pose().position
            dist = ((p.x - x)**2 + (p.y - y)**2 + (p.z - z)**2)**0.5
            if dist < 5.0:  
                return True
        except:
            pass 
        time.sleep(0.1)
    return False

model = YOLO('yolov8s.pt')
cap = cv2.VideoCapture(0)

def get_target_pallet(label):
    if label in FOOD_CLASSES: return PALLET_A, "Food"
    if label in VEHICLE_CLASSES: return PALLET_B, "Vehicle"
    return None, None

try:
    print("start")
    move_wait(SCAN_POS_X, SCAN_POS_Y, SCAN_POS_Z)
    
    need_flush = True 

    while True:
        if need_flush:
            print("scaning")
            time.sleep(0.5)
            for _ in range(5): cap.read() 
            need_flush = False

        ret, frame = cap.read()
        if not ret: break

        h, w = frame.shape[:2]
        cv2.line(frame, (w//2, 0), (w//2, h), (0, 255, 0), 1)
        cv2.line(frame, (0, h//2), (w, h//2), (0, 255, 0), 1)

        cv2.imshow('Lab 3 Fixed Pick', frame)
        if cv2.waitKey(1) & 0xFF == ord('q'): break

        results = model(frame, conf=0.4, verbose=False)
        r = results[0]

        if r.boxes is not None and len(r.boxes) > 0:
            box = r.boxes[0]
            label = r.names[int(box.cls[0])]
            pallet, p_name = get_target_pallet(label)
            
            if pallet:
                print(f"got {label} ->")

                # --- 静态序列动作 ---
                move_wait(FIXED_PICK_X, FIXED_PICK_Y, Z_SAFE)
                move_wait(FIXED_PICK_X, FIXED_PICK_Y, Z_PICK)
                
                device.suck(True)
                time.sleep(1.0) 
                
                move_wait(FIXED_PICK_X, FIXED_PICK_Y, Z_SAFE)
                print(f"   to {p_name}")
                move_wait(pallet['x'], pallet['y'], Z_SAFE)
                move_wait(pallet['x'], pallet['y'], pallet['z'])
                
                device.suck(False)
                time.sleep(0.5)
                move_wait(pallet['x'], pallet['y'], Z_SAFE)
                
                print("more..")
                move_wait(SCAN_POS_X, SCAN_POS_Y, SCAN_POS_Z)
                need_flush = True 

finally:
    if 'device' in locals():
        device.suck(False)
        device.close()
    if 'cap' in locals():
        cap.release()
    cv2.destroyAllWindows()
