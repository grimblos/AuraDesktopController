# Module Spec: Aura Automation Manager

## Responsibility
Translating abstract triggers into concrete system actions, specifically focusing on AutoHotkey (AHK) and Windows API calls.

## Interface
- **Input**: Trigger labels (from Voice/Gesture).
- **Configuration**: Mapping file (YAML/JSON) linking triggers to actions.

## Key Functions
- `execute_action(trigger_id)`: Looks up the mapping and dispatches the action.
- `run_ahk_script(script_path)`: Spawns an AHK process to execute a macro.
- `simulate_hotkey(keys)`: Uses `win32api` or `pyautogui` for simple keyboard simulation.

## Dependencies
- `subprocess`: For running external AHK files.
- `pyautogui` or `pynput`: For direct input simulation.

## Extension Points
- Support for Python scripts as actions.
- Support for MIDI or OSC output for creative workflows.
