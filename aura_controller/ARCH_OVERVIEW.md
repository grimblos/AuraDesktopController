# Aura: Architectural Overview

## System Philosophy
Aura is designed as a distributed multi-process system to ensure that CPU-intensive tasks (Gesture/Voice recognition) do not block the user interface or impact real-time gaming performance.

## Core Components

### 1. Main Process (GUI & Orchestrator)
- **Role**: Manages the lifecycle of subprocesses, handles user configuration, and visualizes status.
- **Technology**: `CustomTkinter`.
- **Communication**: Uses `multiprocessing.Queue` to receive events from engines and send control signals (Start/Stop).

### 2. Voice Engine (Subprocess)
- **Role**: Monitors audio stream for the Wake Word and recognizes commands.
- **Technology**: `Vosk` (Offline STT).
- **Output**: String-based triggers (e.g., `"MUTE_MIC"`, `"VOLUME_UP"`).

### 3. Gesture Engine (Subprocess)
- **Role**: Captures webcam frames and detects hand landmarks.
- **Technology**: `MediaPipe`, `OpenCV`.
- **Optimization**: Frames are processed at a capped FPS (e.g., 20) and reduced resolution (480p) to minimize resource usage.
- **Output**: Categorized gesture triggers (e.g., `"THUMBS_UP"`, `"PALM_OPEN"`).

### 4. Automation Manager
- **Role**: Maps incoming triggers to actual Windows actions.
- **Integration**: Supports direct hotkey emulation and **AutoHotkey (AHK)** script execution.
- **Input**: Unified event queue from both Voice and Gesture engines.

## Data Flow
1. **Detection**: Voice/Gesture engine detects a trigger.
2. **Event Dispatch**: Engine pushes a standardized event object to the `Main Queue`.
3. **Processing**: Main process receives the event and checks the user-defined mappings.
4. **Execution**: Automation Manager executes the corresponding AHK script or hotkey.

## Extension Points
- **Dynamic Gestures**: The `Gesture Engine` can be updated to include a temporal buffer for movement analysis.
- **New Engines**: Additional sensors (e.g., Tobii Eye Tracking) can be added as new subprocesses following the same queue protocol.
