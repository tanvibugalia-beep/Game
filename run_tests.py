"""
run_tests.py — Comprehensive Automated Test Suite for DAKSH BATTLE.
Tests all gameplay subsystems, asset loading, profile management, and UI rendering.
"""
import sys, os
sys.path.insert(0, r"c:\Users\Admin\Desktop\study\vs code\lets try")
os.chdir(r"c:\Users\Admin\Desktop\study\vs code\lets try")

import settings
import assets_manager
from profile import player_profile
from math3d import Vec3
from arena import Arena
from camera_controller import CameraController
from game_manager import GameManager, ROUND_ACTIVE
from player import Player
from bot_ai import TrainingBot, RivalBot
from projectiles import ProjectileManager, Projectile
from pickups import PickupManager, Pickup
from ui import (UIManager, SCREEN_SPLASH, SCREEN_LOGIN, SCREEN_LOBBY,
                SCREEN_PLAYING, SCREEN_PAUSED, SCREEN_VICTORY, SCREEN_DEFEAT)
from renderer import setup_gl
import pyglet

print('=== DAKSH BATTLE — Comprehensive Verification Suite ===')

# 1. Branding & Constants
assert settings.WINDOW_TITLE == "DAKSH BATTLE"
assert settings.TAGLINE == "PLAY • FIGHT • SURVIVE"
print('Branding:   OK (DAKSH BATTLE)')

# 2. Asset System
assets_manager.preload_all()
assert len(assets_manager._image_cache) >= 30
print(f'Assets:     OK ({len(assets_manager._image_cache)} assets loaded)')

# 3. Profile & Session
player_profile.login_as_guest()
assert player_profile.data['username'] == "Daksh_Battle"
assert player_profile.data['is_logged_in'] is True
res = player_profile.record_match_result(won=True, kills=4, score=60, duration_sec=140)
assert res['won'] is True
print(f'Profile:    OK (Guest login, Rank: {player_profile.data["rank_name"]})')

# 4. Arena & Map
arena = Arena(seed=42)
assert arena.ground_height(0, 0) == 0.0
assert arena.ground_height(20, 15) > 0
assert len(arena.towers) >= 4
assert arena.airship is not None
print(f'Arena:      OK ({len(arena.trees)} trees, {len(arena.towers)} towers, airship)')

# 5. Player Physics & 3D Model
cam = CameraController()
cam.apply_mouse(0, 0)
cam.update(Vec3(), 0.016)
p = Player(Vec3(0, 0, 0))
keys = {'w': True, 'a': False, 's': False, 'd': False, 'space': False, 'shift': False, 'e': False}
reqs = p.update(0.016, keys, cam.forward_dir, cam.right_dir, arena, False)
print(f'Player:     OK (pos={p.pos})')

# 6. Bots & Projectiles
bot = RivalBot(Vec3(5, 0, 5), 0, 'Medium')
dummy_p = Player(Vec3(3, 0, 3))
bot.update(0.016, dummy_p, arena)
assert bot.state in ('patrol', 'chase', 'dodge', 'retreat')
bot.take_damage(50)
assert bot.hp == 30
assert bot.state == 'dodge'
bot.take_damage(40)
assert not bot.alive

pm = ProjectileManager()
pm.spawn(Vec3(0, 1, 0), Vec3(0, 0, 1), 'player')
assert len(pm._projectiles) == 1
pm.update(0.5, arena, dummy_p, [])
print('Combat:     OK (FSM Bots, Paint/Energy Projectiles)')

# 7. Game Manager & Shrinking Zone
gm = GameManager(arena)
gm.round_state = ROUND_ACTIVE
gm._start_timer = 0
keys_gm = {k: False for k in ['w','a','s','d','space','shift','e']}
keys_gm['d'] = True
for _ in range(60):
    state = gm.update(0.016, keys_gm, cam, False, 0, 0)
assert 'round_state' in state
assert state['bots_alive'] <= gm.bot_count
print(f'GameManager: OK (Round active, {state["bots_alive"]} bots alive)')

# 8. UI Screens & Modals Rendering in OpenGL 2.1 Context
gl_config = pyglet.gl.Config(major_version=2, minor_version=1, double_buffer=True, depth_size=24)
win = pyglet.window.Window(width=settings.WINDOW_WIDTH, height=settings.WINDOW_HEIGHT, visible=False, config=gl_config)
setup_gl(settings.WINDOW_WIDTH, settings.WINDOW_HEIGHT)
ui = UIManager(settings.WINDOW_WIDTH, settings.WINDOW_HEIGHT)

# Test 3D world draw
gm.draw_world(cam)

# Test all screens
screens = [SCREEN_SPLASH, SCREEN_LOGIN, SCREEN_LOBBY, SCREEN_PLAYING, SCREEN_PAUSED, SCREEN_VICTORY, SCREEN_DEFEAT]
for s in screens:
    ui.screen = s
    ui.draw(state)

# Test all modals
modals = ['store', 'character', 'loadout', 'friends', 'mail', 'settings', 'oauth_info']
for m in modals:
    ui.screen = SCREEN_LOBBY
    ui.active_modal = m
    ui.draw(state)

win.close()
print('UI Engine:  OK (All 7 screens + 7 modals verified in GL 2.1)')

# 9. Web Server & Dual-Platform REST APIs
import threading
import urllib.request
import json
from http.server import ThreadingHTTPServer
from server import DakshBattleHTTPHandler

test_port = 8899
server = ThreadingHTTPServer(("127.0.0.1", test_port), DakshBattleHTTPHandler)
srv_thread = threading.Thread(target=server.serve_forever, daemon=True)
srv_thread.start()

base_url = f"http://127.0.0.1:{test_port}"

# Test /api/status
with urllib.request.urlopen(f"{base_url}/api/status") as res:
    assert res.status == 200
    st = json.loads(res.read().decode())
    assert st["game"] == "DAKSH BATTLE"

# Test /api/weapons
with urllib.request.urlopen(f"{base_url}/api/weapons") as res:
    assert res.status == 200
    w_data = json.loads(res.read().decode())
    assert "Crimson Blaze" in w_data["weapons"]

# Test /api/profile
with urllib.request.urlopen(f"{base_url}/api/profile") as res:
    assert res.status == 200
    p_data = json.loads(res.read().decode())
    assert p_data["success"] is True

# Test static web client serving
with urllib.request.urlopen(f"{base_url}/") as res:
    assert res.status == 200
    html = res.read().decode()
    assert "DAKSH BATTLE" in html

with urllib.request.urlopen(f"{base_url}/web/style.css") as res:
    assert res.status == 200

with urllib.request.urlopen(f"{base_url}/web/game.js") as res:
    assert res.status == 200

server.shutdown()
print('Web Engine: OK (HTTP Server, REST APIs & Three.js Web Client verified)')

print()
print('=== ALL DAKSH BATTLE TESTS PASSED SUCCESSFULLY! ===')
