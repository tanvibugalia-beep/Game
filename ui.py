"""
ui.py — Complete User Interface for DAKSH BATTLE Desktop Edition.
Inspired by the Free Fire lobby and high-octane battle-royale experience.

Screens:
  • SPLASH     — Cinematic island with glowing crown logo and 'TAP TO CONTINUE'
  • LOGIN      — Sign In & Create Account forms, Guest mode, Google OAuth info
  • LOBBY      — Free Fire battle-royale lobby:
                 - Top bar: Profile card, Level, XP bar, Demo Currencies, Social icons
                 - Left sidebar: Store, Character, Armory, Friends, Emotes, Settings, Logout
                 - Center: Standing crimson fighter & pet ninja panda
                 - Right: Rank card (Bronze to Master), Mode selector, and Big Gold [ PLAY ] button
                 - Bottom: Tier progression gallery
  • MODALS     — Store, Character, Armory (all 5 weapon categories), Friends, Mail, Emotes, Settings, OAuth Info
  • PLAYING    — Battle-royale HUD:
                 - Island minimap with player & bot blips
                 - Compass bar & Safe-zone shrink countdown banner
                 - Alive / Kills battle status
                 - Equipped weapon card with live ammo & reload progress
                 - Weapon slots [1] [2] [3]
                 - Free Fire style HP (200/200) and Armor bars
                 - Center dynamic crosshair
  • PAUSED     — ESC overlay: Resume, Graphics (Smooth/Normal/Ultra), FPS Cap, Audio, Controls, Lobby
  • VICTORY    — BOOYAH! VICTORY summary with XP, Coin, and Rank progression
  • DEFEAT     — Defeat summary and Return to Lobby button
"""
import math
import time
import pyglet
from OpenGL.GL import (
    glEnable, glDisable, glBlendFunc, glColor4f,
    GL_BLEND, GL_SRC_ALPHA, GL_ONE_MINUS_SRC_ALPHA
)
import settings
import assets_manager
from auth_manager import auth_manager
from weapons import WEAPONS, WEAPON_CATEGORIES
from renderer import draw_rect_2d, draw_rect_outline_2d, begin_2d, end_2d


# ── Text Rendering (Pyglet 2.x weight= API) ───────────────────────────────────

def draw_text(text: str, x: int, y: int, size: int = 14,
              color=(255, 255, 255, 255), bold=False, anchor_x='left'):
    """Render text with Pyglet Label using weight='bold'/'normal'."""
    weight = 'bold' if bold else 'normal'
    lbl = pyglet.text.Label(
        str(text),
        font_name='Arial',
        font_size=size,
        weight=weight,
        x=x, y=y,
        color=color,
        anchor_x=anchor_x,
    )
    lbl.draw()
    lbl.delete()


# ── Screen States ─────────────────────────────────────────────────────────────
SCREEN_SPLASH    = 'splash'
SCREEN_LOGIN     = 'login'
SCREEN_LOBBY     = 'lobby'
SCREEN_PLAYING   = 'playing'
SCREEN_PAUSED    = 'paused'
SCREEN_SETTINGS  = 'settings'
SCREEN_VICTORY   = 'victory'
SCREEN_DEFEAT    = 'defeat'
SCREEN_CONTROLS = 'controls'

# ── Interactive UI Button ─────────────────────────────────────────────────────

class Button:
    """Clickable UI button with hover animations and styled themes."""

    def __init__(self, x, y, w, h, label, size=15, style='normal', icon=None, sublabel=""):
        self.x = x
        self.y = y
        self.w = w
        self.h = h
        self.label = label
        self.size = size
        self.style = style    # 'normal', 'gold', 'crimson', 'blue', 'tab', 'close', 'active'
        self.icon = icon
        self.sublabel = sublabel
        self._hover = False

    def contains(self, mx, my):
        return self.x <= mx <= self.x + self.w and self.y <= my <= self.y + self.h

    def update_hover(self, mx, my):
        self._hover = self.contains(mx, my)

    def draw(self):
        if self.style == 'gold':
            bg = (255, 215, 60) if self._hover else (245, 185, 30)
            border = (255, 245, 160) if self._hover else (220, 150, 15)
            text_col = (20, 20, 20, 255)
        elif self.style == 'crimson':
            bg = (245, 55, 65) if self._hover else (205, 30, 40)
            border = (255, 130, 140) if self._hover else (150, 20, 25)
            text_col = (255, 255, 255, 255)
        elif self.style == 'blue':
            bg = (45, 135, 240) if self._hover else (25, 95, 185)
            border = (120, 195, 255) if self._hover else (45, 110, 190)
            text_col = (255, 255, 255, 255)
        elif self.style == 'active':
            bg = (45, 75, 120)
            border = (255, 215, 60)
            text_col = (255, 215, 60, 255)
        elif self.style == 'tab':
            bg = (38, 48, 74) if self._hover else (20, 26, 42)
            border = (255, 195, 35) if self._hover else (45, 58, 88)
            text_col = (255, 220, 90, 255) if self._hover else (210, 220, 235, 240)
        elif self.style == 'close':
            bg = (180, 40, 40) if self._hover else (120, 30, 30)
            border = (255, 100, 100) if self._hover else (180, 50, 50)
            text_col = (255, 255, 255, 255)
        else:
            bg = (36, 46, 70) if self._hover else (22, 28, 46)
            border = (80, 140, 220) if self._hover else (45, 60, 90)
            text_col = (255, 255, 255, 255)

        draw_rect_2d(self.x, self.y, self.w, self.h, bg, 0.94)
        draw_rect_outline_2d(self.x, self.y, self.w, self.h, border, 1.0)

        cx = int(self.x + self.w / 2)
        cy = int(self.y + self.h / 2 - self.size // 2)

        if self.icon:
            assets_manager.draw_image(self.icon, self.x + 8, self.y + 6, self.h - 12, self.h - 12)
            draw_text(self.label, self.x + self.h + 8, cy, self.size,
                      color=text_col, bold=True, anchor_x='left')
        else:
            draw_text(self.label, cx, cy, self.size,
                      color=text_col, bold=True, anchor_x='center')

        if self.sublabel:
            draw_text(self.sublabel, cx, self.y + 6, 10,
                      color=(text_col[0], text_col[1], text_col[2], 180), anchor_x='center')


# ── UI Manager ────────────────────────────────────────────────────────────────

class UIManager:
    """Manages all game screens, lobby, HUD, modals, and interaction states."""

    def __init__(self, width: int, height: int):
        self.W = width
        self.H = height
        self.screen = SCREEN_SPLASH
        self.active_modal = None    # None, 'store', 'character', 'armory', 'friends', 'mail', 'emotes', 'settings', 'oauth_info'
        self._mouse_x = 0
        self._mouse_y = 0

        # Login mode: 'signin' or 'register'
        self.auth_mode = 'signin'
        self.input_username = ""
        self.input_password = ""
        self.active_input = 'username'    # 'username' or 'password'
        self.auth_error = ""

        # Armory category tab
        self.armory_cat = "AR"

        # Settings Sliders
        user_settings = (auth_manager.current_user or {}).get("settings", {})
        self._sens_bar = SliderWidget(self.W//2 - 140, self.H//2 - 20, 280, 16,
                                      0.05, 0.8, user_settings.get("mouse_sens", settings.runtime["mouse_sens"]))
        self._vol_bar  = SliderWidget(self.W//2 - 140, self.H//2 - 75, 280, 16,
                                      0.0, 1.0, user_settings.get("vol_master", settings.runtime["vol_master"]))

        # Toast notifications
        self.toast_msg = ""
        self.toast_timer = 0.0

        # Animation timers
        self._start_time = time.time()
        self._pulse = 0.0

        # Build initial buttons
        self.rebuild_buttons()

    def show_toast(self, text: str, duration: float = 3.0):
        self.toast_msg = text
        self.toast_timer = duration

    def resize(self, width: int, height: int):
        self.W = width
        self.H = height
        self.rebuild_buttons()

    def rebuild_buttons(self):
        """Construct responsive button bounding boxes."""
        W, H = self.W, self.H

        # Splash
        bw, bh = 320, 56
        self.btn_splash_tap = Button(W//2 - bw//2, 80, bw, bh, ">> TAP TO CONTINUE >>", 18, style='gold')

        # Login / Register
        lw, lh = 300, 46
        lx = W//2 - lw//2
        self.btn_auth_submit = Button(lx, H//2 - 90, lw, lh, "SIGN IN", 16, style='gold')
        self.btn_auth_toggle = Button(lx, H//2 - 145, lw, 38, "Create New Account", 13, style='tab')
        self.btn_guest_login = Button(lx, H//2 - 195, lw, 38, "Continue as Guest", 14, style='blue')
        self.btn_google_info = Button(lx, H//2 - 245, lw, 36, "Google Sign-In Info", 12, style='normal')

        # Lobby Top Bar Right
        self.btn_lobby_friends = Button(W - 190, H - 46, 42, 38, "👥", 16, style='normal')
        self.btn_lobby_mail    = Button(W - 142, H - 46, 42, 38, "✉", 16, style='normal')
        self.btn_lobby_setting = Button(W - 94, H - 46, 42, 38, "⚙", 16, style='normal')
        self.btn_add_diamonds  = Button(W - 250, H - 46, 30, 38, "+", 18, style='gold')

        # Lobby Left Sidebar
        sb_w, sb_h = 138, 44
        sb_x = 18
        sb_top = H - 110
        gap = 50
        self.btn_nav_store     = Button(sb_x, sb_top - 0 * gap, sb_w, sb_h, "Store", 15, style='gold')
        self.btn_nav_character = Button(sb_x, sb_top - 1 * gap, sb_w, sb_h, "Character", 14, style='tab')
        self.btn_nav_armory    = Button(sb_x, sb_top - 2 * gap, sb_w, sb_h, "Armory", 14, style='tab')
        self.btn_nav_emotes    = Button(sb_x, sb_top - 3 * gap, sb_w, sb_h, "Emotes", 14, style='tab')
        self.btn_nav_friends   = Button(sb_x, sb_top - 4 * gap, sb_w, sb_h, "Friends", 14, style='tab')
        self.btn_nav_settings  = Button(sb_x, sb_top - 5 * gap, sb_w, sb_h, "Settings", 14, style='tab')
        self.btn_nav_logout    = Button(sb_x, sb_top - 6 * gap, sb_w, sb_h, "Logout", 14, style='crimson')

        # Lobby Right Side Play Area
        rw = 230
        rx = W - rw - 24
        cur_mode = (auth_manager.current_user or {}).get("selected_mode", "Battle Royale Classic")
        self.btn_mode_select = Button(rx, 115, rw, 46, f"{cur_mode} >", 14, style='tab')
        self.btn_lobby_play  = Button(rx, 42, rw, 64, "▶  PLAY", 26, style='gold')

        # Pause Screen (ESC)
        pw, ph = 260, 48
        px = W//2 - pw//2
        self.btn_pause_resume   = Button(px, H//2 + 90, pw, ph, "▶  RESUME", 18, style='gold')
        self.btn_pause_restart  = Button(px, H//2 + 30, pw, ph, "↺  RESTART", 16, style='normal')
        self.btn_pause_settings = Button(px, H//2 - 30, pw, ph, "⚙  SETTINGS", 16, style='normal')
        self.btn_pause_lobby    = Button(px, H//2 - 90, pw, ph, "✕  EXIT TO LOBBY", 16, style='crimson')

        # Results Screen
        self.btn_result_continue = Button(W//2 - 140, 65, 280, 52, "CONTINUE TO LOBBY", 18, style='gold')

        # Modal Close Button
        self.btn_modal_close = Button(W//2 + 280, H//2 + 205, 36, 36, "✕", 18, style='close')

        # Settings Screen Controls
        cx = W // 2
        self.btn_diff_easy   = Button(cx - 240, H//2 + 70, 140, 40, "EASY", 14, style='tab')
        self.btn_diff_medium = Button(cx - 70,  H//2 + 70, 140, 40, "MEDIUM", 14, style='gold')
        self.btn_diff_hard   = Button(cx + 100, H//2 + 70, 140, 40, "HARD", 14, style='crimson')
        self.btn_gfx_smooth  = Button(cx - 240, H//2 - 120, 140, 36, "SMOOTH", 13, style='tab')
        self.btn_gfx_normal  = Button(cx - 70,  H//2 - 120, 140, 36, "NORMAL", 13, style='gold')
        self.btn_gfx_ultra   = Button(cx + 100, H//2 - 120, 140, 36, "ULTRA", 13, style='tab')
        self.btn_fps_30      = Button(cx - 240, H//2 - 175, 95, 32, "30 FPS", 12, style='tab')
        self.btn_fps_60      = Button(cx - 125, H//2 - 175, 95, 32, "60 FPS", 12, style='gold')
        self.btn_fps_120     = Button(cx - 10,  H//2 - 175, 95, 32, "120 FPS", 12, style='tab')
        self.btn_fps_max     = Button(cx + 105, H//2 - 175, 95, 32, "MAX", 12, style='tab')
        self.btn_settings_back = Button(cx - 90, 45, 180, 44, "◀  CLOSE", 16, style='normal')

    # ── Text Input Handling for Auth ──────────────────────────────────────────

    def on_text(self, text: str):
        if self.screen == SCREEN_LOGIN and not self.active_modal:
            if text.isprintable():
                if self.active_input == 'username' and len(self.input_username) < 16:
                    self.input_username += text
                elif self.active_input == 'password' and len(self.input_password) < 24:
                    self.input_password += text

    def on_key_press_input(self, symbol, modifiers):
        if self.screen == SCREEN_LOGIN and not self.active_modal:
            if symbol == pyglet.window.key.BACKSPACE:
                if self.active_input == 'username':
                    self.input_username = self.input_username[:-1]
                else:
                    self.input_password = self.input_password[:-1]
            elif symbol == pyglet.window.key.TAB:
                self.active_input = 'password' if self.active_input == 'username' else 'username'
            elif symbol in (pyglet.window.key.RETURN, pyglet.window.key.ENTER):
                self._submit_auth()

    def _submit_auth(self):
        """Process Login or Register submission."""
        u = self.input_username.strip()
        p = self.input_password.strip()

        if self.auth_mode == 'register':
            ok, msg, prof = auth_manager.register(u, p)
            if ok:
                self.auth_error = ""
                self.screen = SCREEN_LOBBY
                self.show_toast(f"Welcome to DAKSH BATTLE, {u}! Fresh Profile Initialized.")
                self.rebuild_buttons()
                return 'login_success'
            else:
                self.auth_error = msg
        else: # signin
            ok, msg, prof = auth_manager.login(u, p)
            if ok:
                self.auth_error = ""
                self.screen = SCREEN_LOBBY
                self.show_toast(f"Welcome back, {prof['username']}!")
                self.rebuild_buttons()
                return 'login_success'
            else:
                self.auth_error = msg
        return None

    # ── Mouse Interaction ─────────────────────────────────────────────────────

    def on_mouse_motion(self, x, y):
        self._mouse_x = x
        self._mouse_y = y
        for b in self._get_active_buttons():
            b.update_hover(x, y)

    def on_mouse_drag(self, x, y):
        if self.screen == SCREEN_SETTINGS or self.active_modal == 'settings':
            self._sens_bar.on_drag(x, y)
            self._vol_bar.on_drag(x, y)
            settings.runtime["mouse_sens"] = self._sens_bar.value
            settings.runtime["vol_master"] = self._vol_bar.value
            if auth_manager.current_user:
                auth_manager.current_user["settings"]["mouse_sens"] = self._sens_bar.value
                auth_manager.current_user["settings"]["vol_master"] = self._vol_bar.value
                auth_manager.save_current_profile()

    def on_mouse_press(self, x, y) -> str | None:
        """Handle button clicks and modal navigation."""
        if self.active_modal:
            if self.btn_modal_close.contains(x, y):
                self.active_modal = None
                return 'close_modal'
            return self._handle_modal_click(x, y)

        # 1. Splash Screen
        if self.screen == SCREEN_SPLASH:
            if self.btn_splash_tap.contains(x, y):
                self.screen = SCREEN_LOGIN
                return 'tap_continue'

        # 2. Login Screen
        elif self.screen == SCREEN_LOGIN:
            # Field focus click
            W, H = self.W, self.H
            pw, ph = 440, 520
            px, py = W//2 - pw//2, H//2 - ph//2
            if px + 40 <= x <= px + pw - 40:
                if py + ph - 225 <= y <= py + ph - 185:
                    self.active_input = 'username'
                elif py + ph - 290 <= y <= py + ph - 250:
                    self.active_input = 'password'

            if self.btn_auth_submit.contains(x, y):
                return self._submit_auth()

            if self.btn_auth_toggle.contains(x, y):
                self.auth_mode = 'signin' if self.auth_mode == 'register' else 'register'
                self.btn_auth_submit.label = "CREATE ACCOUNT" if self.auth_mode == 'register' else "SIGN IN"
                self.btn_auth_toggle.label = "Already have an account? Sign In" if self.auth_mode == 'register' else "Create New Account"
                self.auth_error = ""

            if self.btn_guest_login.contains(x, y):
                auth_manager.login_as_guest()
                self.screen = SCREEN_LOBBY
                self.show_toast(f"Guest session started as {auth_manager.current_user['username']} (Local)")
                self.rebuild_buttons()
                return 'login_guest'

            if self.btn_google_info.contains(x, y):
                self.active_modal = 'oauth_info'
                return 'show_oauth_info'

        # 3. Main Lobby
        elif self.screen == SCREEN_LOBBY:
            if self.btn_lobby_play.contains(x, y):
                return 'play'

            if self.btn_nav_store.contains(x, y):
                self.active_modal = 'store'
                return 'open_store'
            if self.btn_nav_character.contains(x, y):
                self.active_modal = 'character'
                return 'open_character'
            if self.btn_nav_armory.contains(x, y):
                self.active_modal = 'armory'
                return 'open_armory'
            if self.btn_nav_emotes.contains(x, y):
                self.active_modal = 'emotes'
                return 'open_emotes'
            if self.btn_nav_friends.contains(x, y) or self.btn_lobby_friends.contains(x, y):
                self.active_modal = 'friends'
                return 'open_friends'
            if self.btn_nav_settings.contains(x, y) or self.btn_lobby_setting.contains(x, y):
                self.active_modal = 'settings'
                return 'open_settings'
            if self.btn_lobby_mail.contains(x, y):
                self.active_modal = 'mail'
                return 'open_mail'
            if self.btn_add_diamonds.contains(x, y):
                self.active_modal = 'store'
                return 'open_store'

            if self.btn_mode_select.contains(x, y):
                p = auth_manager.current_user or {}
                cur = p.get("selected_mode", "Battle Royale Classic")
                nxt = "Ranked Match" if "Classic" in cur else "Battle Royale Classic"
                p["selected_mode"] = nxt
                auth_manager.save_current_profile()
                self.btn_mode_select.label = f"{nxt} >"
                self.show_toast(f"Mode set to {nxt}")
                return 'toggle_mode'

            if self.btn_nav_logout.contains(x, y):
                auth_manager.logout()
                self.screen = SCREEN_LOGIN
                self.input_password = ""
                self.show_toast("Logged out successfully.")
                return 'logout'

        # 4. Pause Screen (ESC)
        elif self.screen == SCREEN_PAUSED:
            if self.btn_pause_resume.contains(x, y):
                return 'resume'
            if self.btn_pause_restart.contains(x, y):
                return 'restart'
            if self.btn_pause_settings.contains(x, y):
                self.active_modal = 'settings'
                return 'open_settings'
            if self.btn_pause_lobby.contains(x, y):
                self.screen = SCREEN_LOBBY
                return 'lobby'

        # 5. Results Screen
        elif self.screen in (SCREEN_VICTORY, SCREEN_DEFEAT):
            if self.btn_result_continue.contains(x, y):
                self.screen = SCREEN_LOBBY
                return 'lobby'

        # 6. Settings Screen
        elif self.screen == SCREEN_SETTINGS:
            if self.btn_settings_back.contains(x, y):
                self.screen = SCREEN_LOBBY
                return 'lobby'
            self._handle_settings_buttons(x, y)

        return None

    def _handle_modal_click(self, x, y):
        """Route clicks within active popup modals."""
        W, H = self.W, self.H

        if self.active_modal == 'settings':
            self._handle_settings_buttons(x, y)

        elif self.active_modal == 'armory':
            # Category Tab selection
            tab_names = ["ALL"] + WEAPON_CATEGORIES
            for i, cat in enumerate(tab_names):
                tx = W//2 - 270 + i * 90
                if tx <= x <= tx + 85 and H//2 + 130 <= y <= H//2 + 165:
                    self.armory_cat = cat
                    return None

            # Weapon equip click
            filtered = [w for w in WEAPONS.values() if self.armory_cat == "ALL" or w["category"] == self.armory_cat]
            for i, w in enumerate(filtered[:6]):
                col = i % 3
                row = i // 3
                cx = W//2 - 270 + col * 185
                cy = H//2 + 10 - row * 125
                if cx <= x <= cx + 175 and cy <= y <= cy + 115:
                    # Equip weapon to appropriate slot
                    p = auth_manager.current_user or {}
                    p["selected_weapon"] = w["name"]
                    eq = p.setdefault("equipped_weapons", {})
                    eq[w["category"]] = w["name"]
                    auth_manager.save_current_profile()
                    self.show_toast(f"Equipped {w['name']} ({w['category']})!")
                    return 'equip_weapon'

        elif self.active_modal == 'character':
            if W//2 - 220 <= x <= W//2 - 20 and H//2 - 120 <= y <= H//2 + 110:
                p = auth_manager.current_user or {}
                p["selected_character"] = "Daksh"
                auth_manager.save_current_profile()
                self.show_toast("Operator set to Daksh (Assault Specialist)")
            elif W//2 + 20 <= x <= W//2 + 220 and H//2 - 120 <= y <= H//2 + 110:
                p = auth_manager.current_user or {}
                p["selected_character"] = "Anya"
                auth_manager.save_current_profile()
                self.show_toast("Operator set to Anya (Shadow Agility)")

        elif self.active_modal == 'emotes':
            # Emote selection cards
            emotes = ["Wave", "Thumbs Up", "Celebration", "Dance"]
            for i, em in enumerate(emotes):
                ex = W//2 - 240 + i * 125
                ey = H//2 - 50
                if ex <= x <= ex + 115 and ey <= y <= ey + 140:
                    self.show_toast(f"Previewing Emote: {em}")
                    return 'preview_emote'

        elif self.active_modal == 'mail':
            if W//2 - 90 <= x <= W//2 + 90 and H//2 - 100 <= y <= H//2 - 55:
                p = auth_manager.current_user or {}
                if not p.get("mail_claimed"):
                    p["coins"] += 2500
                    p["diamonds"] += 50
                    p["mail_claimed"] = True
                    auth_manager.save_current_profile()
                    self.show_toast("Claimed +2,500 Coins & +50 Diamonds!")
                else:
                    self.show_toast("Daily rewards already claimed today.")

        elif self.active_modal == 'store':
            if H//2 - 120 <= y <= H//2 - 60:
                self.show_toast("Purchased tactical combat supply! (Demo)")

        elif self.active_modal == 'oauth_info':
            if W//2 - 120 <= x <= W//2 + 120 and H//2 - 180 <= y <= H//2 - 135:
                auth_manager.login_as_guest()
                self.active_modal = None
                self.screen = SCREEN_LOBBY
                self.show_toast("Continuing as Guest.")

        return None

    def _handle_settings_buttons(self, x, y):
        """Settings button handling (Difficulty, Graphics, FPS limit)."""
        self._sens_bar.on_click(x, y)
        self._vol_bar.on_click(x, y)

        p = (auth_manager.current_user or {}).setdefault("settings", {})

        if self.btn_diff_easy.contains(x, y):
            settings.runtime["difficulty"] = "Easy"
            self.show_toast("Difficulty: Easy")
        elif self.btn_diff_medium.contains(x, y):
            settings.runtime["difficulty"] = "Medium"
            self.show_toast("Difficulty: Medium")
        elif self.btn_diff_hard.contains(x, y):
            settings.runtime["difficulty"] = "Hard"
            self.show_toast("Difficulty: Hard")

        # Graphics presets
        if self.btn_gfx_smooth.contains(x, y):
            settings.runtime["graphics_preset"] = "Smooth"
            p["graphics_preset"] = "Smooth"
            auth_manager.save_current_profile()
            self.show_toast("Graphics: Smooth (High Performance)")
        elif self.btn_gfx_normal.contains(x, y):
            settings.runtime["graphics_preset"] = "Normal"
            p["graphics_preset"] = "Normal"
            auth_manager.save_current_profile()
            self.show_toast("Graphics: Normal (Balanced)")
        elif self.btn_gfx_ultra.contains(x, y):
            settings.runtime["graphics_preset"] = "Ultra"
            p["graphics_preset"] = "Ultra"
            auth_manager.save_current_profile()
            self.show_toast("Graphics: Ultra (Maximum Visual Fidelity)")

        # FPS limits
        if self.btn_fps_30.contains(x, y):
            settings.runtime["fps_cap"] = 30
            p["fps_cap"] = 30
            auth_manager.save_current_profile()
            self.show_toast("Frame Cap: 30 FPS")
        elif self.btn_fps_60.contains(x, y):
            settings.runtime["fps_cap"] = 60
            p["fps_cap"] = 60
            auth_manager.save_current_profile()
            self.show_toast("Frame Cap: 60 FPS")
        elif self.btn_fps_120.contains(x, y):
            settings.runtime["fps_cap"] = 120
            p["fps_cap"] = 120
            auth_manager.save_current_profile()
            self.show_toast("Frame Cap: 120 FPS")
        elif self.btn_fps_max.contains(x, y):
            settings.runtime["fps_cap"] = 0
            p["fps_cap"] = 0
            auth_manager.save_current_profile()
            self.show_toast("Frame Cap: Unlimited")

    def _get_active_buttons(self) -> list:
        if self.active_modal:
            return [self.btn_modal_close, self.btn_diff_easy, self.btn_diff_medium, self.btn_diff_hard,
                    self.btn_gfx_smooth, self.btn_gfx_normal, self.btn_gfx_ultra,
                    self.btn_fps_30, self.btn_fps_60, self.btn_fps_120, self.btn_fps_max]
        if self.screen == SCREEN_SPLASH:
            return [self.btn_splash_tap]
        if self.screen == SCREEN_LOGIN:
            return [self.btn_auth_submit, self.btn_auth_toggle, self.btn_guest_login, self.btn_google_info]
        if self.screen == SCREEN_LOBBY:
            return [
                self.btn_lobby_play, self.btn_mode_select,
                self.btn_nav_store, self.btn_nav_character, self.btn_nav_armory, self.btn_nav_emotes,
                self.btn_nav_friends, self.btn_nav_settings, self.btn_nav_logout,
                self.btn_lobby_friends, self.btn_lobby_mail, self.btn_lobby_setting,
                self.btn_add_diamonds
            ]
        if self.screen == SCREEN_PAUSED:
            return [self.btn_pause_resume, self.btn_pause_restart, self.btn_pause_settings, self.btn_pause_lobby]
        if self.screen in (SCREEN_VICTORY, SCREEN_DEFEAT):
            return [self.btn_result_continue]
        if self.screen == SCREEN_SETTINGS:
            return [self.btn_diff_easy, self.btn_diff_medium, self.btn_diff_hard,
                    self.btn_gfx_smooth, self.btn_gfx_normal, self.btn_gfx_ultra,
                    self.btn_fps_30, self.btn_fps_60, self.btn_fps_120, self.btn_fps_max,
                    self.btn_settings_back]
        return []

    # ── Main Render Entry Point ───────────────────────────────────────────────

    def draw(self, game_state: dict | None = None):
        begin_2d(self.W, self.H)
        self._pulse = 0.5 + 0.5 * math.sin((time.time() - self._start_time) * 3.5)

        if self.screen == SCREEN_SPLASH:
            self._draw_splash()
        elif self.screen == SCREEN_LOGIN:
            self._draw_login()
        elif self.screen == SCREEN_LOBBY:
            self._draw_lobby()
        elif self.screen == SCREEN_PLAYING:
            if game_state:
                self._draw_hud(game_state)
        elif self.screen == SCREEN_PAUSED:
            if game_state:
                self._draw_hud(game_state)
            self._draw_pause()
        elif self.screen == SCREEN_VICTORY:
            self._draw_results(True, game_state)
        elif self.screen == SCREEN_DEFEAT:
            self._draw_results(False, game_state)
        elif self.screen == SCREEN_SETTINGS:
            self._draw_settings_page()

        # Render Active Popup Modals on top
        if self.active_modal:
            self._draw_active_modal()

        # Toast Messages
        self._draw_toast()

        end_2d()

    # ── Screen: Splash ────────────────────────────────────────────────────────

    def _draw_splash(self):
        W, H = self.W, self.H
        assets_manager.draw_image('splash_background', 0, 0, W, H)
        draw_rect_2d(0, 0, W, H, (10, 12, 22), 0.35)

        # Floating glowing DAKSH BATTLE logo
        logo_w, logo_h = 420, 210
        logo_y = H//2 + 40 + int(math.sin(time.time() * 2) * 8)
        assets_manager.draw_image('logo_splash', W//2 - logo_w//2, logo_y, logo_w, logo_h)

        draw_text("PLAY  •  FIGHT  •  SURVIVE", W//2, logo_y - 28, 20,
                  color=(255, 215, 60, 255), bold=True, anchor_x='center')

        self.btn_splash_tap.draw()
        draw_text("DAKSH BATTLE v2.5  •  Desktop & Web Edition", 18, 16, 12,
                  color=(180, 195, 220, 180))

    # ── Screen: Login & Account Creation ──────────────────────────────────────

    def _draw_login(self):
        W, H = self.W, self.H
        assets_manager.draw_image('login_background', 0, 0, W, H)

        pw, ph = 440, 520
        px, py = W//2 - pw//2, H//2 - ph//2
        draw_rect_2d(px, py, pw, ph, (14, 18, 30), 0.92)
        draw_rect_outline_2d(px, py, pw, ph, (225, 40, 50), 1.0)

        # Game Logo
        assets_manager.draw_image('game_logo', W//2 - 110, py + ph - 120, 220, 110)

        title = "CREATE NEW ACCOUNT" if self.auth_mode == 'register' else "OPERATOR SIGN IN"
        draw_text(title, W//2, py + ph - 140, 16, color=(255, 215, 60, 255), bold=True, anchor_x='center')

        # Username Input Box
        draw_text("Username:", px + 40, py + ph - 170, 12, color=(200, 215, 235, 230))
        u_border = (255, 215, 60) if self.active_input == 'username' else (50, 70, 100)
        draw_rect_2d(px + 40, py + ph - 215, pw - 80, 38, (22, 28, 46), 0.95)
        draw_rect_outline_2d(px + 40, py + ph - 215, pw - 80, 38, u_border, 1.2)
        u_text = self.input_username if self.input_username else ("Enter username..." if self.active_input != 'username' else "")
        draw_text(u_text, px + 52, py + ph - 203, 14,
                  color=(255, 255, 255, 255) if self.input_username else (120, 140, 170, 180))

        # Password Input Box
        draw_text("Password:", px + 40, py + ph - 235, 12, color=(200, 215, 235, 230))
        p_border = (255, 215, 60) if self.active_input == 'password' else (50, 70, 100)
        draw_rect_2d(px + 40, py + ph - 280, pw - 80, 38, (22, 28, 46), 0.95)
        draw_rect_outline_2d(px + 40, py + ph - 280, pw - 80, 38, p_border, 1.2)
        masked_pwd = "•" * len(self.input_password)
        p_text = masked_pwd if masked_pwd else ("Enter password..." if self.active_input != 'password' else "")
        draw_text(p_text, px + 52, py + ph - 268, 14,
                  color=(255, 255, 255, 255) if self.input_password else (120, 140, 170, 180))

        # Error / Notification message
        if self.auth_error:
            draw_text(self.auth_error, W//2, py + ph - 305, 11, color=(255, 80, 80, 255), bold=True, anchor_x='center')

        # Buttons
        self.btn_auth_submit.draw()
        self.btn_auth_toggle.draw()
        self.btn_guest_login.draw()
        self.btn_google_info.draw()

    # ── Screen: Main Lobby ────────────────────────────────────────────────────

    def _draw_lobby(self):
        W, H = self.W, self.H
        # 1. Fullscreen Background
        assets_manager.draw_image('lobby_background', 0, 0, W, H)

        # 2. Top Navigation Bar
        top_h = 58
        top_y = H - top_h
        draw_rect_2d(0, top_y, W, top_h, (12, 16, 28), 0.92)
        draw_rect_outline_2d(0, top_y, W, top_h, (35, 45, 75), 0.9)

        p = auth_manager.current_user or {}
        # Profile Card
        prof_x = 18
        prof_y = top_y + 6
        assets_manager.draw_image('avatar_default', prof_x, prof_y, 46, 46)
        draw_rect_outline_2d(prof_x, prof_y, 46, 46, (255, 215, 60), 1.0)

        username_display = p.get("username", "Guest_01")
        if p.get("is_guest"):
            username_display += " (Guest)"

        draw_text(username_display, prof_x + 56, prof_y + 24, 15, color=(255, 255, 255, 255), bold=True)
        draw_text(f"Lv. {p.get('level', 1)}", prof_x + 56, prof_y + 6, 12, color=(255, 215, 60, 255), bold=True)

        # XP Bar
        xp_w = 110
        draw_rect_2d(prof_x + 115, prof_y + 7, xp_w, 8, (30, 35, 50), 1.0)
        xp_frac = min(1.0, p.get('xp', 0) / max(1, p.get('xp_next', 1000)))
        draw_rect_2d(prof_x + 115, prof_y + 7, int(xp_w * xp_frac), 8, (35, 180, 255), 1.0)

        # Currencies
        coin_x = prof_x + 245
        draw_rect_2d(coin_x, prof_y + 6, 140, 34, (20, 26, 42), 0.9)
        draw_rect_outline_2d(coin_x, prof_y + 6, 140, 34, (255, 195, 30), 0.8)
        draw_text("🪙", coin_x + 8, prof_y + 12, 14)
        draw_text(f"{p.get('coins', 500):,}", coin_x + 32, prof_y + 14, 13, color=(255, 225, 100, 255), bold=True)

        dia_x = coin_x + 150
        draw_rect_2d(dia_x, prof_y + 6, 120, 34, (20, 26, 42), 0.9)
        draw_rect_outline_2d(dia_x, prof_y + 6, 120, 34, (35, 180, 255), 0.8)
        draw_text("💎", dia_x + 8, prof_y + 12, 14)
        draw_text(f"{p.get('diamonds', 0):,}", dia_x + 32, prof_y + 14, 13, color=(120, 220, 255, 255), bold=True)

        self.btn_add_diamonds.x = dia_x + 125
        self.btn_add_diamonds.y = prof_y + 4
        self.btn_add_diamonds.draw()

        self.btn_lobby_friends.draw()
        self.btn_lobby_mail.draw()
        self.btn_lobby_setting.draw()

        # 3. Left Action Menu
        self.btn_nav_store.draw()
        self.btn_nav_character.draw()
        self.btn_nav_armory.draw()
        self.btn_nav_emotes.draw()
        self.btn_nav_friends.draw()
        self.btn_nav_settings.draw()
        self.btn_nav_logout.draw()

        # 4. Center Standing Character Showcase & Pet (with idle breathing animation)
        idle_bob = math.sin(time.time() * 2.0) * 4.0
        char_w, char_h = 240, 420
        char_x = W//2 - char_w//2
        char_y = int(70 + idle_bob)
        assets_manager.draw_image('player_character', char_x, char_y, char_w, char_h)

        # Pet Panda companion (bobbing)
        assets_manager.draw_image('pet_panda', char_x + char_w - 60, char_y + 10, 90, 160)

        cur_char = p.get("selected_character", "Daksh")
        cur_weap = p.get("selected_weapon", "Crimson Blaze")
        draw_text(f"OPERATOR: {cur_char.upper()}  •  {cur_weap.upper()}",
                  W//2 - 20, char_y + 25, 13, color=(255, 215, 60, 240), bold=True, anchor_x='center')

        # 5. Right Area: Rank Card, Mode Selector, Big Gold PLAY Button
        rw = 230
        rx = W - rw - 24

        rank_y = 175
        draw_rect_2d(rx, rank_y, rw, 75, (16, 22, 38), 0.88)
        draw_rect_outline_2d(rx, rank_y, rw, 75, (140, 80, 240), 0.9)
        rank_name = p.get("rank_name", "Bronze")
        rank_icon = f"rank_{rank_name.split()[0].lower()}"
        assets_manager.draw_image(rank_icon, rx + 10, rank_y + 8, 58, 58)
        draw_text(rank_name, rx + 76, rank_y + 42, 16, color=(210, 170, 255, 255), bold=True)
        draw_text(f"★ {p.get('rank_score', 0):,} RP", rx + 76, rank_y + 20, 14, color=(255, 215, 60, 255), bold=True)

        self.btn_mode_select.draw()
        self.btn_lobby_play.draw()

        # 6. Bottom Rank Tier Gallery
        draw_rect_2d(180, 10, W - 430, 44, (12, 16, 28), 0.85)
        draw_rect_outline_2d(180, 10, W - 430, 44, (35, 45, 75), 0.8)
        tiers = ['bronze', 'silver', 'gold', 'platinum', 'diamond', 'heroic', 'master']
        bw = (W - 460) // len(tiers)
        for i, tname in enumerate(tiers):
            bx = 195 + i * bw
            assets_manager.draw_image(f'rank_{tname}', bx, 12, 38, 38)

    # ── Screen: In-Game Battle Royale HUD ─────────────────────────────────────

    def _draw_hud(self, gs: dict):
        W, H = self.W, self.H

        # 1. Top Left Tactical Minimap
        map_size = 135
        map_x, map_y = 18, H - map_size - 18
        assets_manager.draw_image('game_map', map_x, map_y, map_size, map_size)
        draw_rect_outline_2d(map_x, map_y, map_size, map_size, (255, 195, 30), 1.0)

        # Player & Bot Blips
        arena_half = settings.ARENA_HALF
        scale = map_size / (arena_half * 2)
        px, pz = gs.get('player_pos', (0, 0))
        mpx = map_x + int((px + arena_half) * scale)
        mpz = map_y + int((pz + arena_half) * scale)
        draw_rect_2d(mpx - 3, mpz - 3, 7, 7, (35, 230, 255), 1.0)

        for bx, bz in gs.get('bots_pos', []):
            mbx = map_x + int((bx + arena_half) * scale)
            mbz = map_y + int((bz + arena_half) * scale)
            draw_rect_2d(mbx - 2, mbz - 2, 5, 5, (255, 80, 40), 1.0)

        # 2. Compass Bar & Safe Zone Timer
        bar_w = 340
        bar_x = W//2 - bar_w//2
        draw_rect_2d(bar_x, H - 38, bar_w, 32, (12, 16, 28), 0.82)
        draw_rect_outline_2d(bar_x, H - 38, bar_w, 32, (45, 55, 85), 0.8)
        draw_text("NW   330   345    N    15    30   NE", W//2, H - 28, 11,
                  color=(200, 215, 235, 220), bold=True, anchor_x='center')

        t_left = int(gs.get('round_time', 0))
        shrink_mm, shrink_ss = t_left // 60, t_left % 60
        sz_color = (255, 75, 75, 255) if t_left < 30 else (255, 220, 80, 255)
        draw_rect_2d(W//2 - 130, H - 70, 260, 26, (14, 18, 32), 0.85)
        draw_rect_outline_2d(W//2 - 130, H - 70, 260, 26, (220, 45, 50), 0.9)
        draw_text(f"⏳ Safe Zone will shrink in {shrink_mm:02d}:{shrink_ss:02d}", W//2, H - 64, 12,
                  color=sz_color, bold=True, anchor_x='center')

        # 3. Top Right Battle Status (Alive / Kills)
        status_x, status_y = W - 180, H - 48
        draw_rect_2d(status_x, status_y, 160, 38, (12, 16, 28), 0.85)
        draw_rect_outline_2d(status_x, status_y, 160, 38, (45, 55, 85), 0.9)
        alive_cnt = 1 + gs.get('bots_alive', 0)
        draw_text(f"👤 {alive_cnt}", status_x + 20, status_y + 12, 15, color=(35, 220, 255, 255), bold=True)
        draw_text(f"💀 {gs.get('player_kills', 0)}", status_x + 100, status_y + 12, 15, color=(255, 70, 60, 255), bold=True)

        # 4. Center Crosshair
        cx, cy = W//2, H//2
        draw_rect_2d(cx - 1, cy - 10, 2, 8, (255, 255, 255), 0.85)
        draw_rect_2d(cx - 1, cy + 3,  2, 8, (255, 255, 255), 0.85)
        draw_rect_2d(cx - 10, cy - 1, 8, 2, (255, 255, 255), 0.85)
        draw_rect_2d(cx + 3,  cy - 1, 8, 2, (255, 255, 255), 0.85)
        draw_rect_2d(cx - 1, cy - 1, 3, 3, (255, 215, 60), 1.0)

        # 5. Bottom Center Health & Armor Bars
        hp_w = 260
        hp_x, hp_y = W//2 - hp_w//2, 28
        draw_rect_2d(hp_x, hp_y + 18, hp_w, 14, (16, 24, 40), 0.9)
        shield_val = gs.get('player_shield', 0)
        shield_frac = min(1.0, shield_val / settings.PLAYER_MAX_SHIELD)
        draw_rect_2d(hp_x, hp_y + 18, int(hp_w * shield_frac), 14, (35, 175, 255), 1.0)
        draw_rect_outline_2d(hp_x, hp_y + 18, hp_w, 14, (60, 110, 180), 0.9)
        draw_text(f"ARMOR {int(shield_val)}", hp_x + 6, hp_y + 20, 10, color=(220, 240, 255, 230), bold=True)

        draw_rect_2d(hp_x, hp_y, hp_w, 16, (25, 15, 15), 0.9)
        hp_val = gs.get('player_hp', 0)
        hp_frac = min(1.0, hp_val / settings.PLAYER_MAX_HP)
        hp_color = (45, 220, 80) if hp_frac > 0.45 else (235, 50, 50)
        draw_rect_2d(hp_x, hp_y, int(hp_w * hp_frac), 16, hp_color, 1.0)
        draw_rect_outline_2d(hp_x, hp_y, hp_w, 16, (50, 120, 60), 0.9)
        draw_text(f"HP {int(hp_val)} / {settings.PLAYER_MAX_HP}", hp_x + hp_w//2, hp_y + 2, 11,
                  color=(255, 255, 255, 240), bold=True, anchor_x='center')

        # 6. Bottom Right Equipped Weapon Card with Live Ammo & Reloading
        weap_w, weap_h = 220, 78
        weap_x, weap_y = W - weap_w - 20, 20
        draw_rect_2d(weap_x, weap_y, weap_w, weap_h, (14, 18, 30), 0.90)
        draw_rect_outline_2d(weap_x, weap_y, weap_w, weap_h, (220, 45, 50), 0.9)

        w_name = gs.get('weapon_name', 'Crimson Blaze')
        w_icon = gs.get('weapon_icon', 'weapon_crimson_blaze')
        ammo_in = gs.get('ammo_in_mag', 30)
        ammo_res = gs.get('ammo_reserve', 120)
        is_reloading = gs.get('is_reloading', False)

        assets_manager.draw_image(w_icon, weap_x + 8, weap_y + 14, 75, 48)
        draw_text(w_name, weap_x + 90, weap_y + 54, 12, color=(255, 215, 60, 255), bold=True)

        if is_reloading:
            draw_text("RELOADING...", weap_x + 90, weap_y + 32, 13, color=(255, 180, 40, 255), bold=True)
            prog = gs.get('reload_progress', 0.5)
            draw_rect_2d(weap_x + 90, weap_y + 16, 115, 8, (40, 50, 70), 0.9)
            draw_rect_2d(weap_x + 90, weap_y + 16, int(115 * prog), 8, (255, 195, 30), 1.0)
        else:
            draw_text(f"{ammo_in} / {ammo_res}", weap_x + 90, weap_y + 30, 16, color=(255, 255, 255, 255), bold=True)
            draw_text("[R] Reload", weap_x + 90, weap_y + 14, 10, color=(140, 165, 195, 200))

        # 7. Weapon Slots Pills (1, 2, 3) above weapon card
        slots = gs.get('weapon_slots', ['AR', 'SMG', 'Pistol'])
        act_slot = gs.get('active_slot', 0)
        for i, sname in enumerate(slots):
            sx = weap_x + i * 74
            sy = weap_y + weap_h + 8
            is_active = (i == act_slot)
            bg = (45, 75, 120) if is_active else (20, 26, 42)
            bcol = (255, 215, 60) if is_active else (45, 60, 90)
            draw_rect_2d(sx, sy, 70, 24, bg, 0.9)
            draw_rect_outline_2d(sx, sy, 70, 24, bcol, 1.0)
            draw_text(f"[{i+1}] {sname[:6]}", sx + 35, sy + 6, 10,
                      color=(255, 215, 60, 255) if is_active else (200, 210, 230, 220), bold=True, anchor_x='center')

        # 8. Active Emote Banner
        cur_em = gs.get('current_emote')
        if cur_em:
            draw_rect_2d(W//2 - 90, H//2 - 90, 180, 32, (18, 24, 42), 0.88)
            draw_rect_outline_2d(W//2 - 90, H//2 - 90, 180, 32, (255, 215, 60), 1.0)
            draw_text(f"★ EMOTE: {cur_em.upper()}", W//2, H//2 - 80, 12, color=(255, 215, 60, 255), bold=True, anchor_x='center')

        # 9. Controls Reminder (Bottom Left)
        draw_text("WASD: Move  •  Mouse: Aim  •  L-Click: Fire  •  R: Reload  •  1/2/3: Guns  •  B: Emote  •  ESC: Pause",
                  18, 12, 11, color=(160, 175, 200, 180))

    # ── Screen: Pause Overlay (ESC) ───────────────────────────────────────────

    def _draw_pause(self):
        W, H = self.W, self.H
        draw_rect_2d(0, 0, W, H, (8, 10, 18), 0.82)
        draw_text("MATCH PAUSED", W//2, H//2 + 160, 36, color=(255, 215, 60, 255), bold=True, anchor_x='center')

        self.btn_pause_resume.draw()
        self.btn_pause_restart.draw()
        self.btn_pause_settings.draw()
        self.btn_pause_lobby.draw()

    # ── Screen: Results ───────────────────────────────────────────────────────

    def _draw_results(self, victory: bool, gs: dict | None):
        W, H = self.W, self.H
        bg_col = (10, 35, 18) if victory else (35, 12, 16)
        draw_rect_2d(0, 0, W, H, bg_col, 0.88)

        card_w, card_h = 520, 420
        cx, cy = W//2 - card_w//2, H//2 - card_h//2 + 25
        draw_rect_2d(cx, cy, card_w, card_h, (16, 20, 34), 0.94)
        border_col = (255, 215, 60) if victory else (225, 40, 50)
        draw_rect_outline_2d(cx, cy, card_w, card_h, border_col, 1.0)

        if victory:
            draw_text("★ BOOYAH! ★", W//2, cy + card_h - 60, 44, color=(255, 215, 60, 255), bold=True, anchor_x='center')
            draw_text("VICTORY - YOU OUTLASTED EVERYONE", W//2, cy + card_h - 90, 16, color=(200, 255, 210, 220), bold=True, anchor_x='center')
        else:
            draw_text("DEFEATED", W//2, cy + card_h - 60, 44, color=(240, 45, 55, 255), bold=True, anchor_x='center')
            draw_text("BETTER LUCK NEXT TIME", W//2, cy + card_h - 90, 16, color=(255, 180, 180, 220), bold=True, anchor_x='center')

        summary = gs.get('match_summary') if gs else None
        kills = gs.get('player_kills', 0) if gs else 0
        score = gs.get('player_score', 0) if gs else 0

        sy = cy + card_h - 145
        draw_text(f"KILLS: {kills}", cx + 50, sy, 18, color=(255, 255, 255, 255), bold=True)
        draw_text(f"SCORE: {score} PTS", cx + 280, sy, 18, color=(255, 215, 60, 255), bold=True)

        if summary:
            draw_text(f"+{summary.get('xp_gain', 200)} EXP EARNED", cx + 50, sy - 40, 16, color=(35, 180, 255, 255), bold=True)
            draw_text(f"+{summary.get('coin_gain', 300)} DEMO COINS", cx + 280, sy - 40, 16, color=(255, 225, 80, 255), bold=True)
            draw_text(f"RANK RP: +{summary.get('rank_gain', 35)}", cx + 50, sy - 80, 16, color=(200, 150, 255, 255), bold=True)

        r_name = (auth_manager.current_user or {}).get("rank_name", "Bronze")
        draw_text(f"CURRENT TIER: {r_name.upper()}", cx + 280, sy - 80, 16, color=(255, 215, 60, 255), bold=True)

        self.btn_result_continue.draw()

    # ── Screen: Settings Page ─────────────────────────────────────────────────

    def _draw_settings_page(self):
        W, H = self.W, self.H
        draw_rect_2d(0, 0, W, H, (14, 18, 30), 0.96)
        draw_text("SYSTEM SETTINGS", W//2, H - 70, 32, color=(255, 215, 60, 255), bold=True, anchor_x='center')

        draw_text("BOT DIFFICULTY", W//2, H//2 + 110, 16, color=(255, 255, 255, 255), bold=True, anchor_x='center')
        self.btn_diff_easy.draw()
        self.btn_diff_medium.draw()
        self.btn_diff_hard.draw()

        draw_text("GRAPHICS QUALITY", W//2, H//2 - 80, 15, color=(255, 255, 255, 255), bold=True, anchor_x='center')
        self.btn_gfx_smooth.draw()
        self.btn_gfx_normal.draw()
        self.btn_gfx_ultra.draw()

        draw_text("FRAME RATE CAP", W//2, H//2 - 145, 15, color=(255, 255, 255, 255), bold=True, anchor_x='center')
        self.btn_fps_30.draw()
        self.btn_fps_60.draw()
        self.btn_fps_120.draw()
        self.btn_fps_max.draw()

        self.btn_settings_back.draw()

    # ── Modals & Popups ───────────────────────────────────────────────────────

    def _draw_active_modal(self):
        W, H = self.W, self.H
        draw_rect_2d(0, 0, W, H, (0, 0, 0), 0.72)

        mw, mh = 660, 480
        mx, my = W//2 - mw//2, H//2 - mh//2
        draw_rect_2d(mx, my, mw, mh, (16, 22, 38), 0.96)
        draw_rect_outline_2d(mx, my, mw, mh, (225, 40, 50), 1.0)

        self.btn_modal_close.x = mx + mw - 46
        self.btn_modal_close.y = my + mh - 46
        self.btn_modal_close.draw()

        if self.active_modal == 'armory':
            self._draw_armory_modal(mx, my, mw, mh)
        elif self.active_modal == 'store':
            self._draw_store_modal(mx, my, mw, mh)
        elif self.active_modal == 'character':
            self._draw_character_modal(mx, my, mw, mh)
        elif self.active_modal == 'emotes':
            self._draw_emotes_modal(mx, my, mw, mh)
        elif self.active_modal == 'friends':
            self._draw_friends_modal(mx, my, mw, mh)
        elif self.active_modal == 'mail':
            self._draw_mail_modal(mx, my, mw, mh)
        elif self.active_modal == 'settings':
            self._draw_settings_modal(mx, my, mw, mh)
        elif self.active_modal == 'oauth_info':
            self._draw_oauth_modal(mx, my, mw, mh)

    def _draw_armory_modal(self, mx, my, mw, mh):
        """Complete Weapon Armory Modal displaying all 5 categories with stats."""
        draw_text("WEAPON ARMORY", mx + 30, my + mh - 40, 22, color=(255, 215, 60, 255), bold=True)
        draw_text("Inspect, compare and equip weapons across all combat categories", mx + 30, my + mh - 62, 12, color=(160, 175, 205, 200))

        # Category Tabs: [ALL] [AR] [SMG] [Shotgun] [Pistol] [Sniper]
        tab_names = ["ALL"] + WEAPON_CATEGORIES
        for i, cat in enumerate(tab_names):
            tx = mx + 30 + i * 90
            ty = my + mh - 105
            is_active = (self.armory_cat == cat)
            bg = (45, 75, 120) if is_active else (22, 28, 44)
            bcol = (255, 215, 60) if is_active else (45, 60, 90)
            draw_rect_2d(tx, ty, 85, 30, bg, 0.95)
            draw_rect_outline_2d(tx, ty, 85, 30, bcol, 1.0)
            draw_text(cat, tx + 42, ty + 8, 11,
                      color=(255, 215, 60, 255) if is_active else (210, 220, 240, 220), bold=True, anchor_x='center')

        # Filtered weapons
        filtered = [w for w in WEAPONS.values() if self.armory_cat == "ALL" or w["category"] == self.armory_cat]
        p = auth_manager.current_user or {}
        cur_weap = p.get("selected_weapon", "Crimson Blaze")

        for i, w in enumerate(filtered[:6]):
            col = i % 3
            row = i // 3
            cx = mx + 30 + col * 200
            cy = my + mh - 235 - row * 125
            is_eq = (w["name"] == cur_weap)

            bcol = (255, 215, 60) if is_eq else (45, 65, 105)
            draw_rect_2d(cx, cy, 190, 115, (22, 30, 52), 0.92)
            draw_rect_outline_2d(cx, cy, 190, 115, bcol, 1.2)

            assets_manager.draw_image(w.get("icon", "weapon_crimson_blaze"), cx + 12, cy + 50, 75, 48)
            draw_text(w["name"], cx + 92, cy + 85, 12, color=(255, 255, 255, 255), bold=True)
            draw_text(f"Category: {w['category']}", cx + 92, cy + 68, 10, color=(255, 215, 60, 220))

            # Stats row
            draw_text(f"DMG: {w['damage']}  |  MAG: {w['mag_size']}", cx + 12, cy + 30, 10, color=(180, 200, 230, 220))
            draw_text(f"RANGE: {int(w['range'])}m", cx + 12, cy + 14, 10, color=(140, 165, 195, 200))

            draw_text("EQUIPPED" if is_eq else "CLICK TO EQUIP", cx + 125, cy + 14, 10,
                      color=(255, 215, 60, 255) if is_eq else (35, 180, 255, 255), bold=True, anchor_x='center')

    def _draw_emotes_modal(self, mx, my, mw, mh):
        draw_text("EMOTE COLLECTION", mx + 30, my + mh - 40, 22, color=(255, 215, 60, 255), bold=True)
        draw_text("Select and preview battle-royale victory and celebration emotes (B key in match)", mx + 30, my + mh - 62, 12, color=(160, 175, 205, 200))

        emotes = [
            ("Wave", "Friendly hand wave greeting", "👋", mx + 40),
            ("Thumbs Up", "Approved & ready for battle", "👍", mx + 185),
            ("Celebration", "Triumphant victory jump cheer", "🏆", mx + 330),
            ("Dance", "High-energy rhythmic side-step", "💃", mx + 475),
        ]
        for name, desc, emoji, ex in emotes:
            draw_rect_2d(ex, my + 130, 130, 180, (22, 30, 52), 0.9)
            draw_rect_outline_2d(ex, my + 130, 130, 180, (255, 215, 60), 1.0)
            draw_text(emoji, ex + 65, my + 230, 42, anchor_x='center')
            draw_text(name, ex + 65, my + 190, 15, color=(255, 255, 255, 255), bold=True, anchor_x='center')
            draw_text(desc, ex + 65, my + 150, 9, color=(170, 185, 210, 200), anchor_x='center')
            draw_rect_2d(ex + 15, my + 138, 100, 22, (225, 40, 50), 0.9)
            draw_text("EQUIPPED", ex + 65, my + 143, 10, color=(255, 255, 255, 255), bold=True, anchor_x='center')

    def _draw_store_modal(self, mx, my, mw, mh):
        draw_text("DAKSH BATTLE STORE", mx + 30, my + mh - 40, 22, color=(255, 215, 60, 255), bold=True)
        draw_text("Unlock tactical supply crates and weapons with your earned coins", mx + 30, my + mh - 62, 12, color=(160, 175, 205, 200))

        crates = [
            ('item_crate_bronze', 'TACTICAL CRATE', '500 Coins', mx + 35),
            ('item_crate_tech', 'CYBER ELITE BOX', '1,500 Coins', mx + 235),
            ('item_crate_gold', 'ROYAL GOLD CHEST', '50 Diamonds', mx + 435),
        ]
        for icon, title, price, cx in crates:
            draw_rect_2d(cx, my + 100, 180, 240, (22, 30, 52), 0.9)
            draw_rect_outline_2d(cx, my + 100, 180, 240, (45, 65, 105), 0.9)
            assets_manager.draw_image(icon, cx + 45, my + 195, 90, 90)
            draw_text(title, cx + 90, my + 160, 13, color=(255, 255, 255, 255), bold=True, anchor_x='center')
            draw_text(price, cx + 90, my + 135, 14, color=(255, 215, 60, 255), bold=True, anchor_x='center')
            draw_rect_2d(cx + 25, my + 108, 130, 24, (225, 40, 50), 0.9)
            draw_text("OPEN CRATE", cx + 90, my + 114, 11, color=(255, 255, 255, 255), bold=True, anchor_x='center')

    def _draw_character_modal(self, mx, my, mw, mh):
        draw_text("OPERATOR SELECTION", mx + 30, my + mh - 40, 22, color=(255, 215, 60, 255), bold=True)
        draw_text("Choose your combatant for the battlefield", mx + 30, my + mh - 62, 12, color=(160, 175, 205, 200))

        p = auth_manager.current_user or {}
        cur = p.get("selected_character", "Daksh")

        # Daksh Card
        c1_sel = (cur == "Daksh")
        b1 = (255, 215, 60) if c1_sel else (50, 70, 110)
        draw_rect_2d(mx + 60, my + 70, 230, 290, (22, 30, 52), 0.9)
        draw_rect_outline_2d(mx + 60, my + 70, 230, 290, b1, 1.2)
        assets_manager.draw_image('char_male', mx + 80, my + 155, 190, 185)
        draw_text("DAKSH", mx + 175, my + 125, 18, color=(255, 215, 60, 255), bold=True, anchor_x='center')
        draw_text("Assault Specialist (+15% AR reload)", mx + 175, my + 105, 10, color=(180, 200, 225, 200), anchor_x='center')
        draw_text("EQUIPPED" if c1_sel else "CLICK TO SELECT", mx + 175, my + 82, 12,
                  color=(255, 215, 60, 255) if c1_sel else (35, 180, 255, 255), bold=True, anchor_x='center')

        # Anya Card
        c2_sel = (cur == "Anya")
        b2 = (255, 215, 60) if c2_sel else (50, 70, 110)
        draw_rect_2d(mx + 360, my + 70, 230, 290, (22, 30, 52), 0.9)
        draw_rect_outline_2d(mx + 360, my + 70, 230, 290, b2, 1.2)
        assets_manager.draw_image('char_female', mx + 380, my + 155, 190, 185)
        draw_text("ANYA", mx + 475, my + 125, 18, color=(255, 215, 60, 255), bold=True, anchor_x='center')
        draw_text("Shadow Agility (+10% sprint speed)", mx + 475, my + 105, 10, color=(180, 200, 225, 200), anchor_x='center')
        draw_text("EQUIPPED" if c2_sel else "CLICK TO SELECT", mx + 475, my + 82, 12,
                  color=(255, 215, 60, 255) if c2_sel else (35, 180, 255, 255), bold=True, anchor_x='center')

    def _draw_friends_modal(self, mx, my, mw, mh):
        draw_text("SQUAD & TEAMMATES", mx + 30, my + mh - 40, 22, color=(255, 215, 60, 255), bold=True)
        draw_text("Online squad mates and battle invites", mx + 30, my + mh - 62, 12, color=(160, 175, 205, 200))

        friends = [
            ("Ghost_Sniper", "Lv. 24", "In Lobby", (40, 220, 80)),
            ("Viper_Queen", "Lv. 19", "In Battle (Alive 12)", (255, 190, 40)),
            ("ShadowRogue", "Lv. 31", "Online", (40, 220, 80)),
            ("Phoenix_BR", "Lv. 14", "Offline (2h ago)", (150, 160, 180)),
        ]
        for i, (name, lvl, st, col) in enumerate(friends):
            fy = my + mh - 135 - i * 65
            draw_rect_2d(mx + 30, fy, mw - 60, 52, (22, 30, 50), 0.9)
            draw_rect_outline_2d(mx + 30, fy, mw - 60, 52, (45, 60, 95), 0.8)
            draw_text("👤", mx + 45, fy + 16, 18)
            draw_text(name, mx + 80, fy + 26, 15, color=(255, 255, 255, 255), bold=True)
            draw_text(lvl, mx + 80, fy + 10, 11, color=(255, 215, 60, 220))
            draw_text(st, mx + 340, fy + 18, 12, color=(col[0], col[1], col[2], 255), bold=True)

    def _draw_mail_modal(self, mx, my, mw, mh):
        draw_text("SYSTEM MAIL & REWARDS", mx + 30, my + mh - 40, 22, color=(255, 215, 60, 255), bold=True)
        draw_text("Daily supply drops and system rewards", mx + 30, my + mh - 62, 12, color=(160, 175, 205, 200))

        draw_rect_2d(mx + 35, my + 130, mw - 70, 210, (22, 30, 52), 0.9)
        draw_rect_outline_2d(mx + 35, my + 130, mw - 70, 210, (255, 215, 60), 0.9)

        draw_text("🎁 DAILY OPERATOR SUPPLY DROP", mx + 55, my + 300, 16, color=(255, 215, 60, 255), bold=True)
        draw_text("Claim your daily combat allowance:", mx + 55, my + 270, 12, color=(200, 215, 240, 220))
        draw_text("• +2,500 Coins  |  +50 Diamonds", mx + 55, my + 245, 14, color=(100, 230, 255, 255), bold=True)

        p = auth_manager.current_user or {}
        claimed = p.get("mail_claimed", False)
        claim_bg = (80, 90, 110) if claimed else (225, 40, 50)
        draw_rect_2d(mx + mw//2 - 90, my + 155, 180, 42, claim_bg, 0.95)
        draw_text("CLAIMED" if claimed else "CLAIM SUPPLIES", mx + mw//2, my + 168, 14,
                  color=(255, 255, 255, 255), bold=True, anchor_x='center')

    def _draw_settings_modal(self, mx, my, mw, mh):
        draw_text("SYSTEM SETTINGS", mx + 30, my + mh - 40, 22, color=(255, 215, 60, 255), bold=True)
        draw_text("Configure gameplay controls, graphics fidelity and audio", mx + 30, my + mh - 62, 12, color=(160, 175, 205, 200))

        # Difficulty
        draw_text("BOT DIFFICULTY", mx + 35, my + 305, 13, color=(255, 255, 255, 255), bold=True)
        self.btn_diff_easy.x, self.btn_diff_easy.y, self.btn_diff_easy.w = mx + 35, my + 265, 110
        self.btn_diff_medium.x, self.btn_diff_medium.y, self.btn_diff_medium.w = mx + 160, my + 265, 110
        self.btn_diff_hard.x, self.btn_diff_hard.y, self.btn_diff_hard.w = mx + 285, my + 265, 110
        self.btn_diff_easy.draw()
        self.btn_diff_medium.draw()
        self.btn_diff_hard.draw()

        # Graphics Preset
        draw_text("GRAPHICS PRESET", mx + 35, my + 235, 13, color=(255, 255, 255, 255), bold=True)
        self.btn_gfx_smooth.x, self.btn_gfx_smooth.y, self.btn_gfx_smooth.w = mx + 35, my + 195, 110
        self.btn_gfx_normal.x, self.btn_gfx_normal.y, self.btn_gfx_normal.w = mx + 160, my + 195, 110
        self.btn_gfx_ultra.x, self.btn_gfx_ultra.y, self.btn_gfx_ultra.w = mx + 285, my + 195, 110
        self.btn_gfx_smooth.draw()
        self.btn_gfx_normal.draw()
        self.btn_gfx_ultra.draw()

        # Sliders
        draw_text("MOUSE SENSITIVITY", mx + 35, my + 165, 13, color=(255, 255, 255, 255), bold=True)
        self._sens_bar.x, self._sens_bar.y, self._sens_bar.w = mx + 35, my + 140, 360
        self._sens_bar.draw()
        draw_text(f"{self._sens_bar.value:.2f}", self._sens_bar.x + self._sens_bar.w + 12, self._sens_bar.y, 12)

        draw_text("MASTER VOLUME", mx + 35, my + 110, 13, color=(255, 255, 255, 255), bold=True)
        self._vol_bar.x, self._vol_bar.y, self._vol_bar.w = mx + 35, my + 85, 360
        self._vol_bar.draw()
        draw_text(f"{int(self._vol_bar.value * 100)}%", self._vol_bar.x + self._vol_bar.w + 12, self._vol_bar.y, 12)

        p = auth_manager.current_user or {}
        draw_text(f"Logged in as: {p.get('username', 'Guest')}  |  Rank: {p.get('rank_name', 'Bronze')}",
                  mx + 35, my + 45, 12, color=(255, 215, 60, 240))

    def _draw_oauth_modal(self, mx, my, mw, mh):
        draw_text("GOOGLE SIGN-IN NOTICE", mx + 30, my + mh - 40, 20, color=(255, 215, 60, 255), bold=True)
        draw_text("OAuth 2.0 Security Configuration Information", mx + 30, my + mh - 62, 12, color=(160, 175, 205, 200))

        lines = auth_manager.get_google_auth_status().split("\n")
        y = my + mh - 105
        for line in lines:
            draw_text(line, mx + 35, y, 12, color=(220, 230, 245, 230))
            y -= 22

        draw_rect_2d(mx + mw//2 - 120, my + 30, 240, 42, (255, 195, 30), 0.95)
        draw_text("CONTINUE AS GUEST", mx + mw//2, my + 42, 14,
                  color=(20, 20, 20, 255), bold=True, anchor_x='center')

    # ── Toast Message ─────────────────────────────────────────────────────────

    def _draw_toast(self):
        if self.toast_timer > 0:
            self.toast_timer -= 0.016
            tw, th = 420, 36
            tx, ty = self.W // 2 - tw // 2, self.H - 110
            draw_rect_2d(tx, ty, tw, th, (18, 24, 40), 0.92)
            draw_rect_outline_2d(tx, ty, tw, th, (255, 215, 60), 0.9)
            draw_text(self.toast_msg, self.W//2, ty + 10, 12,
                      color=(255, 235, 140, 255), bold=True, anchor_x='center')


# ── Slider Widget ─────────────────────────────────────────────────────────────

class SliderWidget:
    """Draggable slider for volume and sensitivity."""

    def __init__(self, x, y, w, h, min_val, max_val, init_val):
        self.x = x
        self.y = y
        self.w = w
        self.h = h
        self.min = min_val
        self.max = max_val
        self.value = init_val
        self._dragging = False

    def _set_from_x(self, mx):
        t = max(0.0, min(1.0, (mx - self.x) / self.w))
        self.value = self.min + t * (self.max - self.min)

    def on_click(self, mx, my):
        if self.x <= mx <= self.x + self.w and self.y - 6 <= my <= self.y + self.h + 6:
            self._dragging = True
            self._set_from_x(mx)

    def on_drag(self, mx, my):
        if self._dragging:
            self._set_from_x(mx)

    def on_release(self):
        self._dragging = False

    def draw(self):
        draw_rect_2d(self.x, self.y, self.w, self.h, (30, 40, 65), 0.9)
        t = (self.value - self.min) / max(0.001, self.max - self.min)
        draw_rect_2d(self.x, self.y, int(self.w * t), self.h, (255, 195, 30), 1.0)
        kx = self.x + int(self.w * t) - 6
        draw_rect_2d(kx, self.y - 4, 12, self.h + 8, (255, 245, 180), 1.0)
        draw_rect_outline_2d(self.x, self.y, self.w, self.h, (65, 90, 140), 1.0)
