# Module Spec: Aura Gesture Engine

## Responsibility
Capturing webcam input and classifying hand gestures using landmark detection.

## Interface
- **Input**: Camera ID, Frame Rate Cap, Sensitivity Threshold.
- **Output**: `Queue` events containing detected gesture labels.

## Key Functions
- `process_frame(image)`: Extracts landmarks using MediaPipe.
- `classify_gesture(landmarks)`: Maps landmark coordinates to a static gesture (e.g., Fist, Peace, Ok).
- `run_engine(camera_id, event_queue)`: Main loop handling camera lifecycle and frame dispatch.

## Dependencies
- `mediapipe`: Hand landmark detection.
- `opencv-python`: Image processing and camera access.

## Performance Constraints
- Frame processing should be asynchronous to capture.
- Resolution should be limited to 640x480 or 800x600 for inference speed.
- Must provide a "Low Power Mode" which reduces polling frequency.
