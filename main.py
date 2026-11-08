"""
main.py — Entry point for DAKSH BATTLE.
A polished 3D desktop battle-royale game inspired by Free Fire.

Controls:
---------
WASD        Move
Mouse       Aim / Rotate Camera
Left Click  Fire weapon (paint/energy tags)
Space       Jump
Shift       Sprint
E           Interact
Escape      Pause / Return to Lobby
"""
import sys
import math
import pyglet
from pyglet.window import key, mouse
from pyglet.gl import *

import settings
import assets_manager
from profile import player_profile
from renderer  import setup_gl, set_viewport
from math3d    import Vec3
from arena     import Arena
from camera_controller import CameraController
from game_manager import (GameManager, ROUND_ACTIVE, ROUND_WAITING,
                           ROUND_PAUSED, ROUND_VICTORY, ROUND_DEFEAT)
from ui        import (UIManager, SCREEN_SPLASH, SCREEN_LOGIN, SCREEN_LOBBY,
                       SCREEN_PLAYING, SCREEN_PAUSED, SCREEN_SETTINGS,
                       SCREEN_CONTROLS, SCREEN_VICTORY, SCREEN_DEFEAT)


def main():
    # ── Window Setup ──────────────────────────────────────────────────────────
    W, H = settings.WINDOW_WIDTH, settings.WINDOW_HEIGHT

    # Explicit OpenGL 2.1 compatibility context
    gl_config = pyglet.gl.Config(
        major_version=2,
        minor_version=1,
        double_buffer=True,
        depth_size=24,
    )
    window = pyglet.window.Window(
        width=W, height=H,
        caption=f"{settings.WINDOW_TITLE} — {settings.TAGLINE}",
        resizable=True,
        config=gl_config,
    )
    try:
        screen = pyglet.canvas.get_display().get_default_screen()
        window.set_location(
            (screen.width  - W) // 2,
            (screen.height - H) // 2,
        )
    except Exception:
        pass

    # ── GL & Assets Init ──────────────────────────────────────────────────────
    setup_gl(W, H)
    assets_manager.preload_all()

    # ── Core Game Systems ─────────────────────────────────────────────────────
    arena  = Arena(seed=42)
    camera = CameraController()
    gm     = GameManager(arena)
    ui     = UIManager(W, H)

    # ── Input & Session State ─────────────────────────────────────────────────
    keys_held: dict = {
        'w': False, 'a': False, 's': False, 'd': False,
        'space': False, 'shift': False, 'e': False,
        '1': False, '2': False, '3': False, 'r': False, 'b': False,
    }
    shoot_requested   = [False]
    mouse_locked      = [False]
    _mouse_dx         = [0.0]
    _mouse_dy         = [0.0]
    game_state        = [None]
    settings_origin   = [SCREEN_LOBBY]
    current_fps_cap   = [settings.runtime.get("fps_cap", 60)]

    def lock_mouse(lock: bool):
        mouse_locked[0] = lock
        try:
            window.set_exclusive_mouse(lock)
        except Exception:
            pass

    # ── UI Action Router ──────────────────────────────────────────────────────
    def handle_action(action: str | None):
        if action is None:
            return

        if action == 'tap_continue':
            ui.screen = SCREEN_LOGIN
            lock_mouse(False)

        elif action in ('login_guest', 'login_google'):
            ui.screen = SCREEN_LOBBY
            lock_mouse(False)

        elif action == 'play':
            gm.restart()
            ui.screen = SCREEN_PLAYING
            lock_mouse(True)

        elif action == 'lobby':
            gm.restart()
            ui.screen = SCREEN_LOBBY
            lock_mouse(False)

        elif action == 'logout':
            player_profile.logout()
            ui.screen = SCREEN_LOGIN
            lock_mouse(False)

        elif action == 'resume':
            ui.screen = SCREEN_PLAYING
            gm.round_state = ROUND_ACTIVE
            lock_mouse(True)

        elif action == 'restart':
            gm.restart()
            ui.screen = SCREEN_PLAYING
            lock_mouse(True)

        elif action == 'quit':
            pyglet.app.exit()

        elif action == 'open_settings':
            settings_origin[0] = ui.screen
            ui.active_modal = 'settings'

        elif action == 'open_store':
            ui.active_modal = 'store'

        elif action == 'open_character':
            ui.active_modal = 'character'

        elif action == 'open_loadout':
            ui.active_modal = 'loadout'

        elif action == 'open_friends':
            ui.active_modal = 'friends'

        elif action == 'open_mail':
            ui.active_modal = 'mail'

        elif action == 'close_modal':
            ui.active_modal = None

    # ── Window Events ─────────────────────────────────────────────────────────

    @window.event
    def on_text(text):
        ui.on_text(text)

    @window.event
    def on_key_press(symbol, modifiers):
        ui.on_key_press_input(symbol, modifiers)

        ks_map = {
            key.W: 'w', key.A: 'a', key.S: 's', key.D: 'd',
            key.SPACE: 'space',
            key.LSHIFT: 'shift', key.RSHIFT: 'shift',
            key.E: 'e',
            key._1: '1', key._2: '2', key._3: '3',
            key.R: 'r', key.B: 'b',
        }
        if symbol in ks_map:
            keys_held[ks_map[symbol]] = True

        if symbol == key.ESCAPE:
            if ui.active_modal:
                ui.active_modal = None
            elif ui.screen == SCREEN_PLAYING:
                ui.screen = SCREEN_PAUSED
                gm.round_state = ROUND_PAUSED
                lock_mouse(False)
            elif ui.screen == SCREEN_PAUSED:
                ui.screen = SCREEN_PLAYING
                gm.round_state = ROUND_ACTIVE
                lock_mouse(True)
            elif ui.screen == SCREEN_SETTINGS:
                ui.screen = SCREEN_LOBBY

    @window.event
    def on_key_release(symbol, modifiers):
        ks_map = {
            key.W: 'w', key.A: 'a', key.S: 's', key.D: 'd',
            key.SPACE: 'space',
            key.LSHIFT: 'shift', key.RSHIFT: 'shift',
            key.E: 'e',
            key._1: '1', key._2: '2', key._3: '3',
            key.R: 'r', key.B: 'b',
        }
        if symbol in ks_map:
            keys_held[ks_map[symbol]] = False

    @window.event
    def on_mouse_press(x, y, btn, modifiers):
        if (ui.screen == SCREEN_PLAYING and
                btn == mouse.LEFT and mouse_locked[0]):
            shoot_requested[0] = True

        action = ui.on_mouse_press(x, y)
        handle_action(action)

    @window.event
    def on_mouse_release(x, y, btn, modifiers):
        if btn == mouse.LEFT:
            shoot_requested[0] = False
        ui._sens_bar.on_release()
        ui._vol_bar.on_release()

    @window.event
    def on_mouse_motion(x, y, dx, dy):
        ui.on_mouse_motion(x, y)
        if mouse_locked[0] and ui.screen == SCREEN_PLAYING:
            _mouse_dx[0] += dx
            _mouse_dy[0] += dy

    @window.event
    def on_mouse_drag(x, y, dx, dy, buttons, modifiers):
        ui.on_mouse_drag(x, y)
        if mouse_locked[0] and ui.screen == SCREEN_PLAYING:
            _mouse_dx[0] += dx
            _mouse_dy[0] += dy

    @window.event
    def on_resize(width, height):
        set_viewport(width, height)
        ui.resize(width, height)

    # ── Main Update Loop ──────────────────────────────────────────────────────
    def update(dt):
        new_cap = settings.runtime.get("fps_cap", 60)
        if new_cap != current_fps_cap[0]:
            schedule_fps()

        clamped_dt = min(dt, 0.05)

        if ui.screen == SCREEN_PLAYING:
            gs = gm.update(
                clamped_dt,
                keys_held,
                camera,
                shoot_requested[0],
                _mouse_dx[0],
                _mouse_dy[0],
            )
            game_state[0] = gs
            _mouse_dx[0] = 0.0
            _mouse_dy[0] = 0.0

            rs = gs.get('round_state')
            if rs == ROUND_VICTORY and ui.screen == SCREEN_PLAYING:
                ui.screen = SCREEN_VICTORY
                lock_mouse(False)
            elif rs == ROUND_DEFEAT and ui.screen == SCREEN_PLAYING:
                ui.screen = SCREEN_DEFEAT
                lock_mouse(False)

        elif ui.screen == SCREEN_PAUSED:
            camera.update(gm.player.pos, clamped_dt)

    # ── Render Frame ──────────────────────────────────────────────────────────
    @window.event
    def on_draw():
        window.clear()
        if ui.screen in (SCREEN_PLAYING, SCREEN_PAUSED,
                          SCREEN_VICTORY, SCREEN_DEFEAT):
            gm.draw_world(camera)
        ui.draw(game_state[0])

    def schedule_fps():
        cap = settings.runtime.get("fps_cap", 60)
        pyglet.clock.unschedule(update)
        if cap == 0:
            pyglet.clock.schedule(update)
        else:
            pyglet.clock.schedule_interval(update, 1.0 / max(15, cap))
        current_fps_cap[0] = cap

    schedule_fps()

    print("=" * 65)
    print("  ★  DAKSH BATTLE  ★  — PLAY • FIGHT • SURVIVE")
    print("  Inspired by Free Fire | High-Octane 3D Battle Royale Prototype")
    print("  Controls:  WASD = Move       |  Mouse = Aim")
    print("             L-Click = Fire    |  Space = Jump")
    print("             Shift = Sprint    |  ESC = Pause / Resume")
    print("=" * 65)

    pyglet.app.run()


if __name__ == '__main__':
    main()
