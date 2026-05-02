"""
Aura: The Main Orchestrator
This script initializes the GUI and manages the lifecycle of the Voice and Gesture processes.
"""

import multiprocessing
import threading
import sys
import time
from aura_core.config_manager import ConfigManager
from aura_core.networking import AuraNetworking, AuraDiscovery
from aura_core.command_router import CommandRouter
from aura_automation.manager import AutomationManager
from aura_gui.app import AuraApp

def run_gesture_process(config, event_queue, control_queue):
    """Initializes and runs the Gesture Engine in its own process."""
    from aura_gesture.engine import GestureEngine
    engine = GestureEngine(
        camera_id=config["engines"]["gesture"]["camera_id"],
        fps_cap=config["engines"]["gesture"]["fps_cap"]
    )
    show_preview = config["engines"]["gesture"].get("show_preview", False)
    engine.run(event_queue, control_queue=control_queue, show_preview=show_preview)

def run_voice_process(config, event_queue, control_queue):
    """Initializes and runs the Voice Engine in its own process."""
    from aura_voice.engine import VoiceEngine
    engine = VoiceEngine(
        model_path=config["engines"]["voice"]["model_path"],
        wake_word=config["engines"]["voice"]["wake_word"]
    )
    engine.run(event_queue, control_queue=control_queue)

def run_local_engines(config, event_queue, control_queue):
    """Starts engines as local subprocesses."""
    # Start in separate processes - we pass the config, not the engine instance
    p1 = multiprocessing.Process(target=run_gesture_process, args=(config, event_queue, control_queue))
    p2 = multiprocessing.Process(target=run_voice_process, args=(config, event_queue, control_queue))
    p1.start()
    p2.start()
    return [p1, p2]

def main():
    """
    Entry point for the Aura application.
    Initializes components based on the configuration mode.
    """
    # 1. Load Configuration
    cfg_manager = ConfigManager()
    config = cfg_manager.config
    mode = config.get("mode", "local")
    
    # 2. Initialize Queues
    event_queue = multiprocessing.Queue()    # Engine Triggers -> Main
    control_queue = multiprocessing.Queue()  # Main -> Engines
    
    print(f"Initializing Aura in [{mode.upper()}] mode...")

    # 3. Initialize Automation & Routing
    auto_mgr = AutomationManager(config.get("mappings", {}))
    router = CommandRouter(auto_mgr, control_queue)

    # 4. Mode-specific Initialization
    active_processes = []
    
    if mode == "local":
        active_processes = run_local_engines(config, event_queue, control_queue)
        
    elif mode == "remote_client":
        # TODO: Implement local capture threads that feed networking streamer
        net = AuraNetworking(config)
        discovery = AuraDiscovery()
        server_ip = discovery.find_server()
        if server_ip:
            config["server"]["ip"] = server_ip
            # net.start_streamer(video_q, audio_q, event_queue.put)
        pass
        
    elif mode == "remote_server":
        # TODO: Implement remote server host that feeds local engines
        discovery = AuraDiscovery()
        discovery.advertise()
        pass

    # 5. Start GUI
    app = AuraApp(event_queue, control_queue)
    
    # 6. Event Processing Loop (Threaded so it doesn't block GUI)
    def event_processor():
        while True:
            if not event_queue.empty():
                event = event_queue.get()
                trigger_label = event.get("label")
                app.update_log(f"Detected: {trigger_label}")
                router.route(trigger_label)
            time.sleep(0.01)

    threading.Thread(target=event_processor, daemon=True).start()
    
    app.run()

    # Cleanup
    for p in active_processes:
        p.terminate()

if __name__ == "__main__":
    # Ensure multiprocessing works correctly when bundled as an EXE
    multiprocessing.freeze_support()
    main()
