"""
app.py — Production-Grade FastAPI Backend for DAKSH BATTLE.
Serves the 3D Three.js WebGL browser client and provides authenticated REST APIs
for player sessions, registration, weapon loadouts, and match analytics.

Run with:
    uvicorn app:app --host 0.0.0.0 --port 8080 --reload
"""
import os
import json
from typing import Optional
from fastapi import FastAPI, HTTPException, Request, Response
from fastapi.responses import FileResponse, JSONResponse
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

import settings
from auth_manager import auth_manager, validate_username
from weapons import WEAPON_CATALOG

ROOT_DIR = os.path.dirname(os.path.abspath(__file__))
WEB_DIR = os.path.join(ROOT_DIR, "web")
ASSETS_DIR = os.path.join(ROOT_DIR, "assets")

app = FastAPI(
    title=f"{settings.GAME_NAME} API Backend",
    version=settings.VERSION,
    description="High-performance dual-platform battle royale game engine backend."
)

# Enable CORS for cross-origin browser clients
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ── Pydantic Request Models ───────────────────────────────────────────────────

class AuthCredentials(BaseModel):
    username: str
    password: str

class GuestLoginRequest(BaseModel):
    guest_id: Optional[str] = "Daksh_Battle"

class ProfileSaveRequest(BaseModel):
    selected_character: Optional[str] = None
    selected_weapon: Optional[str] = None
    equipped_weapons: Optional[dict] = None
    equipped_emotes: Optional[list] = None
    settings: Optional[dict] = None

class MatchRecordRequest(BaseModel):
    won: bool
    kills: int = 0
    score: int = 0
    duration: int = 0

# ── REST API Endpoints ────────────────────────────────────────────────────────

@app.get("/api/status")
async def get_status():
    return {
        "status": "online",
        "game": settings.GAME_NAME,
        "tagline": settings.TAGLINE,
        "version": settings.VERSION,
        "backend": "FastAPI + Uvicorn",
        "dual_platform": True
    }

@app.get("/api/auth/google/status")
async def get_google_auth_status():
    return {
        "configured": auth_manager.is_google_configured(),
        "status_message": auth_manager.get_google_auth_status()
    }

@app.get("/api/profile")
async def get_profile():
    prof = auth_manager.current_user or auth_manager.login_as_guest()
    return {"success": True, "profile": prof}

@app.get("/api/weapons")
async def get_weapons():
    weapons_data = {wid: dict(w) for wid, w in WEAPON_CATALOG.items()}
    return {"weapons": weapons_data}

@app.post("/api/register")
async def register_account(creds: AuthCredentials):
    ok, msg, prof = auth_manager.register(creds.username, creds.password)
    if not ok:
        raise HTTPException(status_code=400, detail=msg)
    return {"success": True, "message": msg, "profile": prof}

@app.post("/api/login")
async def login_account(creds: AuthCredentials):
    ok, msg, prof = auth_manager.login(creds.username, creds.password)
    if not ok:
        raise HTTPException(status_code=401, detail=msg)
    return {"success": True, "message": msg, "profile": prof}

@app.post("/api/guest")
async def login_guest(req: GuestLoginRequest):
    prof = auth_manager.login_as_guest(req.guest_id)
    return {"success": True, "profile": prof}

@app.post("/api/logout")
async def logout():
    auth_manager.logout()
    return {"success": True, "message": "Logged out successfully"}

@app.post("/api/profile/save")
async def save_profile(data: ProfileSaveRequest):
    if not auth_manager.current_user:
        raise HTTPException(status_code=401, detail="Not authenticated")

    user = auth_manager.current_user
    if data.selected_character is not None:
        user["selected_character"] = data.selected_character
    if data.selected_weapon is not None:
        user["selected_weapon"] = data.selected_weapon
    if data.equipped_weapons is not None:
        user["equipped_weapons"] = data.equipped_weapons
    if data.equipped_emotes is not None:
        user["equipped_emotes"] = data.equipped_emotes
    if data.settings is not None:
        user["settings"] = data.settings

    auth_manager.save_current_profile()
    return {"success": True, "profile": user}

@app.post("/api/match/record")
async def record_match(req: MatchRecordRequest):
    result = auth_manager.record_match(req.won, req.kills, req.score, req.duration)
    return {
        "success": True,
        "result": result,
        "profile": auth_manager.current_user
    }

# ── Static File Handlers ──────────────────────────────────────────────────────

@app.get("/")
@app.get("/index.html")
async def serve_index():
    index_file = os.path.join(WEB_DIR, "index.html")
    if os.path.exists(index_file):
        return FileResponse(index_file, media_type="text/html")
    raise HTTPException(status_code=404, detail="index.html not found")

# Mount /assets static directory
if os.path.exists(ASSETS_DIR):
    app.mount("/assets", StaticFiles(directory=ASSETS_DIR), name="assets")

# Mount /web static directory
if os.path.exists(WEB_DIR):
    app.mount("/web", StaticFiles(directory=WEB_DIR), name="web")

if __name__ == "__main__":
    import uvicorn
    print("=" * 65)
    print("  ★  DAKSH BATTLE FASTAPI BACKEND  ★")
    print("  Battle Royale Web Engine Online at:")
    print("  👉  http://localhost:8080/")
    print("=" * 65)
    uvicorn.run("app:app", host="0.0.0.0", port=8080, reload=False)
