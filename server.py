"""
server.py — High-Performance Dual-Platform Web Backend for DAKSH BATTLE.
Serves the Three.js 3D WebGL battle royale client and provides secure REST APIs
for authentication, account management, weapon catalogs, and match reporting.

Usage:
    python server.py [port]
    Default port: 8080 (http://localhost:8080)
"""
import sys
import os
import json
import mimetypes
from http.server import ThreadingHTTPServer, SimpleHTTPRequestHandler
from urllib.parse import urlparse, parse_qs

# Import existing core modules
import settings
from auth_manager import auth_manager, validate_username
from weapons import WEAPON_CATALOG

ROOT_DIR = os.path.dirname(os.path.abspath(__file__))
WEB_DIR = os.path.join(ROOT_DIR, "web")
ASSETS_DIR = os.path.join(ROOT_DIR, "assets")

class DakshBattleHTTPHandler(SimpleHTTPRequestHandler):
    """Custom request handler supporting static assets and DAKSH BATTLE REST APIs."""

    def end_headers(self):
        # Enable CORS and disable caching for active game assets
        self.send_header("Access-Control-Allow-Origin", "*")
        self.send_header("Access-Control-Allow-Methods", "GET, POST, OPTIONS")
        self.send_header("Access-Control-Allow-Headers", "Content-Type, Authorization")
        self.send_header("Cache-Control", "no-cache, no-store, must-revalidate")
        super().end_headers()

    def do_OPTIONS(self):
        self.send_response(200)
        self.end_headers()

    def do_GET(self):
        parsed = urlparse(self.path)
        path = parsed.path

        # REST API endpoints
        if path == "/api/status":
            self.send_json_response(200, {
                "status": "online",
                "game": settings.GAME_NAME,
                "tagline": settings.TAGLINE,
                "version": settings.VERSION,
            })
            return

        if path == "/api/auth/google/status":
            self.send_json_response(200, {
                "configured": auth_manager.is_google_configured(),
                "status_message": auth_manager.get_google_auth_status()
            })
            return

        if path == "/api/profile":
            prof = auth_manager.current_user or auth_manager.login_as_guest()
            self.send_json_response(200, {"success": True, "profile": prof})
            return

        if path == "/api/weapons":
            # Return serialized weapon definitions
            weapons_data = {wid: dict(w) for wid, w in WEAPON_CATALOG.items()}
            self.send_json_response(200, {"weapons": weapons_data})
            return

        # Static files routing
        if path in ("/", "/index.html"):
            self.serve_file(os.path.join(WEB_DIR, "index.html"), "text/html")
            return

        if path.startswith("/assets/"):
            rel_asset = path[len("/assets/"):]
            file_path = os.path.join(ASSETS_DIR, rel_asset)
            if os.path.exists(file_path) and os.path.isfile(file_path):
                mime, _ = mimetypes.guess_type(file_path)
                self.serve_file(file_path, mime or "application/octet-stream")
                return
            else:
                self.send_error(404, f"Asset not found: {path}")
                return

        # Serve static web files
        clean_path = path.lstrip("/")
        if clean_path.startswith("web/"):
            clean_path = clean_path[len("web/"):]
        web_file = os.path.join(WEB_DIR, clean_path)
        if os.path.exists(web_file) and os.path.isfile(web_file):
            mime, _ = mimetypes.guess_type(web_file)
            self.serve_file(web_file, mime or "text/plain")
            return

        self.send_error(404, f"Path not found: {path}")

    def do_POST(self):
        parsed = urlparse(self.path)
        path = parsed.path

        content_length = int(self.headers.get("Content-Length", 0))
        body = self.rfile.read(content_length).decode("utf-8") if content_length > 0 else "{}"
        
        try:
            data = json.loads(body) if body else {}
        except json.JSONDecodeError:
            self.send_json_response(400, {"success": False, "error": "Invalid JSON format"})
            return

        # API Handlers
        if path == "/api/register":
            username = data.get("username", "")
            password = data.get("password", "")
            ok, msg, prof = auth_manager.register(username, password)
            if ok:
                self.send_json_response(200, {"success": True, "message": msg, "profile": prof})
            else:
                self.send_json_response(400, {"success": False, "error": msg})
            return

        if path == "/api/login":
            username = data.get("username", "")
            password = data.get("password", "")
            ok, msg, prof = auth_manager.login(username, password)
            if ok:
                self.send_json_response(200, {"success": True, "message": msg, "profile": prof})
            else:
                self.send_json_response(401, {"success": False, "error": msg})
            return

        if path == "/api/guest":
            guest_id = data.get("guest_id")
            prof = auth_manager.login_as_guest(guest_id)
            self.send_json_response(200, {"success": True, "profile": prof})
            return

        if path == "/api/logout":
            auth_manager.logout()
            self.send_json_response(200, {"success": True, "message": "Logged out successfully"})
            return

        if path == "/api/profile/save":
            if auth_manager.current_user:
                # Update allowed fields
                allowed_fields = [
                    "selected_character", "selected_weapon", "equipped_weapons",
                    "equipped_emotes", "settings"
                ]
                for f in allowed_fields:
                    if f in data:
                        auth_manager.current_user[f] = data[f]
                auth_manager.save_current_profile()
                self.send_json_response(200, {"success": True, "profile": auth_manager.current_user})
            else:
                self.send_json_response(401, {"success": False, "error": "Not authenticated"})
            return

        if path == "/api/match/record":
            won = bool(data.get("won", False))
            kills = int(data.get("kills", 0))
            score = int(data.get("score", 0))
            duration = int(data.get("duration", 0))
            
            result = auth_manager.record_match(won, kills, score, duration)
            self.send_json_response(200, {"success": True, "result": result, "profile": auth_manager.current_user})
            return

        self.send_error(404, f"API endpoint not found: {path}")

    def serve_file(self, file_path, content_type):
        try:
            with open(file_path, "rb") as f:
                content = f.read()
            self.send_response(200)
            self.send_header("Content-Type", content_type)
            self.send_header("Content-Length", str(len(content)))
            self.end_headers()
            self.wfile.write(content)
        except Exception as e:
            self.send_error(500, f"Error serving file: {e}")

    def send_json_response(self, code: int, data: dict):
        body = json.dumps(data, indent=2).encode("utf-8")
        self.send_response(code)
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)

def run_server(port: int = 8080):
    try:
        import uvicorn
        print("=" * 65)
        print("  ★  DAKSH BATTLE FASTAPI + THREE.JS SERVER  ★")
        print(f"  High-performance Battle Royale Engine Online at:")
        print(f"  👉  http://localhost:{port}/")
        print(f"  Static client directory: {WEB_DIR}")
        print("=" * 65)
        uvicorn.run("app:app", host="0.0.0.0", port=port, log_level="info")
        return
    except ImportError:
        pass

    server_address = ("0.0.0.0", port)
    httpd = ThreadingHTTPServer(server_address, DakshBattleHTTPHandler)
    print("=" * 65)
    print(f"  ★  DAKSH BATTLE WEB SERVER (Standard HTTP)  ★")
    print(f"  Battle Royale Engine Online at:")
    print(f"  👉  http://localhost:{port}/")
    print(f"  Serving client: {WEB_DIR}")
    print(f"  Serving assets: {ASSETS_DIR}")
    print("=" * 65)
    try:
        httpd.serve_forever()
    except KeyboardInterrupt:
        print("\nShutting down DAKSH BATTLE Web Server...")
        httpd.shutdown()

if __name__ == "__main__":
    port = int(sys.argv[1]) if len(sys.argv) > 1 else 8080
    run_server(port)
