"""
settings.py — Global configuration constants for DAKSH BATTLE.
Theme: Crimson Red, Golden Yellow, Neon Blue, and Dark Futuristic.
Tagline: PLAY • FIGHT • SURVIVE
"""

# ── Window ────────────────────────────────────────────────────────────────────
GAME_NAME     = "DAKSH BATTLE"
VERSION       = "2.0.0"
WINDOW_TITLE  = "DAKSH BATTLE"
TAGLINE       = "PLAY • FIGHT • SURVIVE"
WINDOW_WIDTH  = 1280
WINDOW_HEIGHT = 720
FULLSCREEN    = False

# ── Brand Theme Colours (RGB 0-255 tuples) ────────────────────────────────────
COLOR_BG_DARK       = (12, 14, 24)
COLOR_PANEL_BG      = (20, 24, 38)
COLOR_PANEL_BORDER  = (45, 55, 85)
COLOR_CRIMSON       = (225, 35, 45)       # Signature Flame Red
COLOR_GOLD          = (255, 198, 35)      # Royal Victory Gold
COLOR_NEON_BLUE     = (35, 180, 255)      # Cyber Neon Cyan
COLOR_TEXT_LIGHT    = (240, 245, 255)
COLOR_TEXT_MUTED    = (150, 165, 190)

SKY_COLOR        = (100, 160, 230)
GRASS_COLOR      = (62, 140, 55)
ROAD_COLOR       = (80, 80, 88)
TREE_TRUNK_COLOR = (108, 70, 36)
TREE_LEAF_COLOR  = (46, 130, 50)
ROCK_COLOR       = (120, 120, 130)
BUILDING_COLOR   = (175, 160, 145)
BUILDING2_COLOR  = (140, 170, 155)

# Character visual colors
PLAYER_COLOR     = (220, 35, 45)      # Daksh Crimson Suit
PLAYER_ACCENT    = (255, 195, 30)     # Golden Highlights
BOT_PATROL_COLOR = (220, 200, 50)     # Training android (yellow)
BOT_RIVAL_COLOR  = (240, 80, 35)      # Rival combatant (orange/red)
PROJ_COLOR       = (35, 220, 255)     # Glowing Cyan Energy Tag
PROJ_COLOR_GOLD  = (255, 200, 40)     # Golden Fire Tag

HP_COLOR         = (50, 220, 80)      # Green Health Bar
SHIELD_COLOR     = (35, 160, 255)     # Blue Armor Bar
PICKUP_HP_COLOR  = (80, 255, 80)
PICKUP_SHIELD_COLOR = (80, 160, 255)
PICKUP_SPEED_COLOR  = (255, 220, 30)

# ── Player Physics & Stats ───────────────────────────────────────────────────
PLAYER_SPEED        = 6.5    # units/s walk
PLAYER_SPRINT_MULT  = 1.75
PLAYER_JUMP_HEIGHT  = 5.8
PLAYER_MAX_HP       = 100
PLAYER_MAX_SHIELD   = 100    # Free Fire style 100 Armor / 100 HP
PLAYER_GRAVITY      = 20.0
PLAYER_SHOOT_COOLDOWN = 0.28
PLAYER_RESPAWN_INVULN = 2.0

# ── Camera ────────────────────────────────────────────────────────────────────
CAM_DISTANCE   = 8.5
CAM_HEIGHT     = 3.8
CAM_PITCH_MIN  = -15   # degrees
CAM_PITCH_MAX  = 55
CAM_SMOOTH     = 9.0
MOUSE_SENS_DEFAULT = 0.20

# ── Projectile ────────────────────────────────────────────────────────────────
PROJ_SPEED      = 32.0
PROJ_LIFETIME   = 3.2
PROJ_DAMAGE     = 22
PROJ_RADIUS     = 0.35

# ── Arena ─────────────────────────────────────────────────────────────────────
ARENA_HALF          = 80.0   # starting safe-zone half-extent
ARENA_SHRINK_START  = 50.0   # seconds before first shrink
ARENA_SHRINK_END    = 16.0
ARENA_SHRINK_RATE   = 3.5
ZONE_DAMAGE_PER_SEC = 6.0

# ── Bots ──────────────────────────────────────────────────────────────────────
BOT_MAX_HP       = 80
BOT_SPEEDS       = {"Easy": 2.6, "Medium": 4.0, "Hard": 5.4}
BOT_SHOOT_CDS    = {"Easy": 1.8, "Medium": 1.1, "Hard": 0.60}
BOT_DETECT_RANGE = 24.0
BOT_PATROL_RADIUS= 15.0
BOT_COUNTS       = {"Easy": 5, "Medium": 9, "Hard": 14}

# ── Round ─────────────────────────────────────────────────────────────────────
ROUND_DURATION   = 300

# ── Pickups ──────────────────────────────────────────────────────────────────
PICKUP_HP_RESTORE    = 35
PICKUP_SHIELD_RESTORE= 40
PICKUP_SPEED_DUR     = 8.0
PICKUP_SPEED_MULT    = 1.55
PICKUP_SPAWN_COUNT   = 20

# ── Runtime mutable settings ─────────────────────────────────────────────────
runtime = {
    "difficulty":    "Medium",
    "mouse_sens":    MOUSE_SENS_DEFAULT,
    "vol_master":    0.7,
    "vol_sfx":       0.8,
    "vol_music":     0.5,
    "fullscreen":    False,
}
