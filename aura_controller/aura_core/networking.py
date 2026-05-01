"""
Aura Networking Module
Handles streaming, command transmission, and encryption using a custom packet protocol.
"""

import socket
import struct
import json
import threading
import time
from typing import Callable
from zeroconf import ServiceInfo, Zeroconf, ServiceBrowser

class AuraNetworking:
    def __init__(self, config: dict):
        self.config = config
        self.host = config.get("server", {}).get("ip", "0.0.0.0")
        self.port = config.get("server", {}).get("port", 5005)
        self.is_running = False
        
        # Encryption Setup
        self.fernet = None
        if config.get("server", {}).get("encryption", {}).get("enabled", False):
            from cryptography.fernet import Fernet
            key = config["server"]["encryption"].get("secret_key")
            if key:
                self.fernet = Fernet(key.encode())

    def encrypt(self, data):
        return self.fernet.encrypt(data) if self.fernet else data

    def decrypt(self, data):
        return self.fernet.decrypt(data) if self.fernet else data

    def start_streamer(self, video_queue, audio_queue, trigger_callback):
        """Runs on the Client: Sends sensor data to the server and receives triggers."""
        self.is_running = True
        
        def _send_loop():
            with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
                s.connect((self.host, self.port))
                print(f"Connected to Aura Server at {self.host}:{self.port}")
                
                while self.is_running:
                    # Priority: Trigger check (Recv) is handled in separate thread
                    # Here we pump Video and Audio
                    try:
                        if not video_queue.empty():
                            frame_data = video_queue.get_nowait()
                            self.send_packet(s, self.TYPE_VIDEO, self.encrypt(frame_data))
                        
                        if not audio_queue.empty():
                            audio_data = audio_queue.get_nowait()
                            self.send_packet(s, self.TYPE_AUDIO, self.encrypt(audio_data))
                        
                        time.sleep(0.001) # Yield
                    except Exception as e:
                        print(f"Stream Error: {e}")
                        break

        def _recv_loop():
            with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
                s.connect((self.host, self.port)) # Separate connection for triggers? 
                # Better: Use the same socket or a duplex approach. 
                # For simplicity in this skeleton, we'll assume a single duplex socket 
                # is managed by a more robust handler.
                pass

        threading.Thread(target=_send_loop, daemon=True).start()

    def start_host(self, video_callback, audio_callback, trigger_queue):
        """Runs on the Server: Receives data, processes it, and sends back triggers."""
        self.is_running = True
        
        def _handle_client(conn, addr):
            print(f"Accepted connection from {addr}")
            with conn:
                while self.is_running:
                    p_type, payload = self.recv_packet(conn)
                    if p_type is None: break
                    
                    data = self.decrypt(payload)
                    
                    if p_type == self.TYPE_VIDEO:
                        video_callback(data)
                    elif p_type == self.TYPE_AUDIO:
                        audio_callback(data)
                    elif p_type == self.TYPE_CONTROL:
                        # Handle commands from client
                        pass

                    # Check if there are triggers to send back
                    if not trigger_queue.empty():
                        trigger = trigger_queue.get_nowait()
                        self.send_packet(conn, self.TYPE_TRIGGER, self.encrypt(trigger))

        def _server_loop():
            with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
                s.bind(("0.0.0.0", self.port))
                s.listen()
                print(f"Aura Server listening on port {self.port}...")
                while self.is_running:
                    conn, addr = s.accept()
                    threading.Thread(target=_handle_client, args=(conn, addr), daemon=True).start()

        threading.Thread(target=_server_loop, daemon=True).start()

class AuraDiscovery:
    """Handles Zeroconf mDNS advertising and scanning."""
    def __init__(self, port=5005):
        self.zeroconf = Zeroconf()
        self.port = port
        self.service_type = "_aura._tcp.local."

    def advertise(self, name="AuraServer"):
        """Runs on the Server: Broadcasts presence."""
        info = ServiceInfo(
            self.service_type,
            f"{name}.{self.service_type}",
            addresses=[socket.inet_aton("0.0.0.0")],
            port=self.port,
            properties={"version": "1.0"},
            server=f"{name}.local.",
        )
        self.zeroconf.register_service(info)
        print(f"Advertising {name} on port {self.port}...")

    def find_server(self, timeout=5.0):
        """Runs on the Client: Finds the server IP."""
        class Listener:
            def __init__(self): self.found_info = None
            def add_service(self, zc, type_, name):
                self.found_info = zc.get_service_info(type_, name)
        
        listener = Listener()
        browser = ServiceBrowser(self.zeroconf, self.service_type, listener)
        
        start_time = time.time()
        while time.time() - start_time < timeout:
            if listener.found_info:
                ip = socket.inet_ntoa(listener.found_info.addresses[0])
                print(f"Found Aura Server at {ip}")
                return ip
            time.sleep(0.5)
        
        return None
