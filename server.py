import http.server
import socketserver
import threading
from pyngrok import ngrok
import os

class LocalVideoServer:
    def __init__(self, port=8000, directory="videos/pending"):
        self.port = port
        self.directory = directory
        self.public_url = None
        self.server = None
        self.thread = None
        
    def start(self, authtoken=None):
        """Lokal serverni va Ngrok tunnelni ishga tushiradi"""
        if not os.path.exists(self.directory):
            os.makedirs(self.directory)
            
        # HTTP Server yaratish
        class Handler(http.server.SimpleHTTPRequestHandler):
            def __init__(self, *args, **kwargs):
                super().__init__(*args, directory="videos/pending", **kwargs)
                
        self.server = socketserver.TCPServer(("", self.port), Handler)
        
        # Serverni orqa fonga (thread) yuborish
        self.thread = threading.Thread(target=self.server.serve_forever, daemon=True)
        self.thread.start()
        
        # Ngrok tunnel ochish
        if authtoken:
            ngrok.set_auth_token(authtoken)
            
        tunnel = ngrok.connect(self.port)
        self.public_url = tunnel.public_url
        print(f"[Server] Lokal server ishga tushdi: http://localhost:{self.port}")
        print(f"[Server] Ochiq URL yaratildi (Ngrok): {self.public_url}")
        
    def stop(self):
        """Serverni va tunnelni to'xtatadi"""
        if self.server:
            self.server.shutdown()
        ngrok.kill()
        print(f"[Server] Server to'xtatildi.")
