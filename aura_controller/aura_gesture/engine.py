"""
Aura Gesture Engine
Handles webcam capture and hand landmark detection using MediaPipe.
"""

import cv2
import mediapipe as mp
from multiprocessing import Queue
import time

class GestureEngine:
    def __init__(self, camera_id: int = 0, fps_cap: int = 20, min_confidence: float = 0.7):
        """
        Initialize the gesture engine with camera settings and performance caps.
        """
        self.camera_id = camera_id
        self.fps_cap = fps_cap
        self.min_confidence = min_confidence
        
        # Initialize MediaPipe Hands
        self.mp_hands = mp.solutions.hands
        self.hands = self.mp_hands.Hands(
            static_image_mode=False,
            max_num_hands=1,
            min_detection_confidence=min_confidence,
            min_tracking_confidence=min_confidence
        )
        self.mp_draw = mp.solutions.drawing_utils

    def process_frame(self, frame):
        """
        Run MediaPipe inference on a single frame and return landmarks.
        """
        rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        results = self.hands.process(rgb_frame)
        return results

    def classify_gesture(self, hand_landmarks):
        """
        Analyze landmark coordinates to identify a specific static gesture.
        Basic implementation: Counts raised fingers.
        """
        if not hand_landmarks:
            return None

        landmarks = hand_landmarks.landmark
        
        # Simple Logic: Finger Counting (as a placeholder for more complex static gestures)
        # TODO: A more capable model can implement complex static gesture recognition 
        # (e.g., 'OK' sign, 'Peace' sign, 'Rock on') using geometric angle analysis.
        
        tips = [8, 12, 16, 20]
        fingers_up = []
        
        # Thumb (Simple check: is tip to the left/right of the IP joint?)
        if landmarks[4].x < landmarks[3].x:
            fingers_up.append(1)
            
        # Other fingers (Is tip higher than the PIP joint?)
        for tip in tips:
            if landmarks[tip].y < landmarks[tip - 2].y:
                fingers_up.append(1)
                
        count = sum(fingers_up)
        
        if count == 5: return "PALM_OPEN"
        if count == 0: return "FIST"
        if count == 1 and landmarks[8].y < landmarks[6].y: return "POINTING"
        
        return None

    def run(self, event_queue: Queue, frame_source=None):
        """
        Main loop for camera capture and processing.
        Pushes detected gesture labels to the event_queue.
        """
        # If frame_source is None, we use local camera. 
        # If it's a queue/stream, we are in Remote Mode.
        cap = cv2.VideoCapture(self.camera_id) if frame_source is None else None
        
        last_time = time.time()
        
        while True:
            if cap:
                ret, frame = cap.read()
                if not ret: break
            else:
                frame = frame_source.get() # Get frame from networking module
            
            # FPS Capping
            if time.time() - last_time < 1.0 / self.fps_cap:
                continue
            last_time = time.time()

            results = self.process_frame(frame)
            if results.multi_hand_landmarks:
                for hand_lms in results.multi_hand_landmarks:
                    gesture = self.classify_gesture(hand_lms)
                    if gesture:
                        event_queue.put({"engine": "gesture", "label": gesture})
            
            # TODO: Advanced models can implement Temporal Analysis here 
            # (e.g., tracking the hand's centroid movement over 10 frames to detect swipes).
