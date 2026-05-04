"""
Aura Gesture Engine
Uses MediaPipe Tasks API to detect hands and classify gestures.
"""

import cv2
import time
import mediapipe as mp
from mediapipe.tasks import python as mp_python
from mediapipe.tasks.python import vision
from multiprocessing import Queue

class GestureEngine:
    def __init__(self, camera_id=0, fps_cap=20):
        self.camera_id = camera_id
        self.fps_cap = fps_cap
        
        # Initialize MediaPipe Hand Landmarker Task
        base_options = mp_python.BaseOptions(model_asset_path='models/hand_landmarker.task')
        options = vision.HandLandmarkerOptions(base_options=base_options, num_hands=1)
        self.detector = vision.HandLandmarker.create_from_options(options)
        
        self.show_preview = False

    def process_frame(self, frame):
        # Convert BGR to RGB
        rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        mp_image = mp.Image(image_format=mp.ImageFormat.SRGB, data=rgb_frame)
        detection_result = self.detector.detect(mp_image)
        return detection_result

    def classify_gesture(self, results):
        if not results or not results.hand_landmarks:
            return None
            
        landmarks = results.hand_landmarks[0]
        handedness = results.handedness[0][0].category_name  # "Left" or "Right"
        
        # Fingers: [Thumb, Index, Middle, Ring, Pinky]
        fingers_up = [False, False, False, False, False]
        
        # Thumb: compare x coordinates based on handedness
        # Note: MediaPipe image coords are mirrored. "Left" hand in image is actually right hand of user if mirrored.
        if handedness == "Right":
            if landmarks[4].x < landmarks[3].x: fingers_up[0] = True
        else:
            if landmarks[4].x > landmarks[3].x: fingers_up[0] = True
            
        # Other fingers: compare tip y to pip y
        tips = [8, 12, 16, 20]
        for i, tip in enumerate(tips):
            if landmarks[tip].y < landmarks[tip - 2].y:
                fingers_up[i+1] = True
                
        count = sum(fingers_up)
        
        # Classification
        if count == 5: return "PALM_OPEN"
        if count == 0: return "FIST"
        
        # POINTING: Only Index is up
        if fingers_up == [False, True, False, False, False]: 
            return "POINTING"
            
        # PEACE_SIGN: Index and Middle are up
        if fingers_up == [False, True, True, False, False]:
            return "PEACE_SIGN"
            
        # THUMBS_UP: Only Thumb is up
        if fingers_up == [True, False, False, False, False]:
            return "THUMBS_UP"
            
        # ROCK_ON: Index and Pinky up (thumb can be in or out)
        if fingers_up[1] and fingers_up[4] and not fingers_up[2] and not fingers_up[3]:
            return "ROCK_ON"
            
        return None

    def run(self, event_queue: Queue, control_queue: Queue = None, frame_source=None, show_preview=False):
        cap = cv2.VideoCapture(self.camera_id) if frame_source is None else None
        
        self.show_preview = show_preview
        self.is_active = True
        
        # Debounce State
        last_detected_gesture = None
        gesture_streak = 0
        streak_threshold = 2 
        last_trigger_time = 0
        cooldown = 0.3 
        
        last_frame_time = time.time()
        
        while True:
            # 1. Check for Control Messages
            if control_queue and not control_queue.empty():
                msg = control_queue.get()
                if msg.get("target") == "gesture":
                    if msg.get("action") == "toggle_preview":
                        self.show_preview = msg.get("value", False)
                        if not self.show_preview:
                            cv2.destroyAllWindows()

            # 2. Capture Frame
            if cap:
                ret, frame = cap.read()
                if not ret: break
            else:
                if frame_source:
                    frame = frame_source.get()
                else:
                    break

            if time.time() - last_frame_time < 1.0 / self.fps_cap:
                continue
            last_frame_time = time.time()

            results = self.process_frame(frame)
            gesture = self.classify_gesture(results)
            
            # --- Preview Window ---
            if self.show_preview:
                preview_frame = frame.copy()
                if results and results.hand_landmarks:
                    for hand_landmarks in results.hand_landmarks:
                        for lm in hand_landmarks:
                            h, w, c = preview_frame.shape
                            cx, cy = int(lm.x * w), int(lm.y * h)
                            cv2.circle(preview_frame, (cx, cy), 5, (255, 0, 255), cv2.FILLED)
                
                cv2.imshow("Aura Camera Preview", preview_frame)
                if cv2.waitKey(1) & 0xFF == ord('q'):
                    break

            # --- Debounce & Cooldown Logic ---
            if gesture and gesture == last_detected_gesture:
                gesture_streak += 1
            else:
                gesture_streak = 0
                last_detected_gesture = gesture

            if gesture_streak >= streak_threshold:
                current_time = time.time()
                if current_time - last_trigger_time > cooldown:
                    event_queue.put({"engine": "gesture", "label": gesture})
                    last_trigger_time = current_time
                    gesture_streak = 0 
        
        if cap: cap.release()
        cv2.destroyAllWindows()
