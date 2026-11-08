"""
assets_manager.py — Central asset loader and cache for DAKSH BATTLE.

Loads individual artwork elements from the assets/ directory:
- splash_background
- login_background
- lobby_background
- player_character
- character_portraits (char_male, char_female)
- game_map, minimap_hud
- weapon_icons (crimson_blaze, golden_eagle, frostbite_sniper)
- rank_badges (bronze, silver, gold, platinum, diamond, heroic, master)
- inventory_icons (helmet, vest, backpack, medkit, energy, booster, crates)
- game_logo, logo_splash

Provides fallback procedural rendering if any asset fails to load.
"""
import os
import pyglet
from OpenGL.GL import (
    glEnable, glDisable, glBlendFunc, glColor4f,
    GL_BLEND, GL_SRC_ALPHA, GL_ONE_MINUS_SRC_ALPHA, GL_TEXTURE_2D
)

ASSETS_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'assets')

_image_cache: dict[str, pyglet.image.AbstractImage | None] = {}
_missing_warned: set[str] = set()

def get_asset_path(filename: str) -> str:
    """Return the absolute path to an asset file in assets/."""
    if not filename.endswith('.png') and not filename.endswith('.jpg'):
        filename = f"{filename}.png"
    return os.path.join(ASSETS_DIR, filename)

def load_image(name: str) -> pyglet.image.AbstractImage | None:
    """Load and cache an image from the assets folder. Returns None if missing."""
    if name in _image_cache:
        return _image_cache[name]

    path = get_asset_path(name)
    if not os.path.exists(path):
        # Also check without adding extension if name already had one
        alt_path = os.path.join(ASSETS_DIR, name)
        if os.path.exists(alt_path):
            path = alt_path
        else:
            if name not in _missing_warned:
                print(f"[Assets] Asset '{name}' not found at {path}, using procedural fallback.")
                _missing_warned.add(name)
            _image_cache[name] = None
            return None

    try:
        img = pyglet.image.load(path)
        _image_cache[name] = img
        return img
    except Exception as e:
        print(f"[Assets] Failed to load '{name}': {e}")
        _image_cache[name] = None
        return None

def draw_image(name: str, x: float, y: float, width: float, height: float):
    """
    Draw an image at (x, y) with specified width and height.
    Falls back to a styled placeholder rectangle if image is missing.
    """
    img = load_image(name)
    if img is not None:
        try:
            # Enable blending for transparent PNGs
            glEnable(GL_BLEND)
            glBlendFunc(GL_SRC_ALPHA, GL_ONE_MINUS_SRC_ALPHA)
            glColor4f(1.0, 1.0, 1.0, 1.0)
            img.blit(x, y, width=width, height=height)
            return True
        except Exception:
            pass

    # Procedural fallback box
    from renderer import draw_rect_2d, draw_rect_outline_2d
    draw_rect_2d(x, y, width, height, (30, 35, 55), 0.8)
    draw_rect_outline_2d(x, y, width, height, (255, 180, 40), 0.9)
    return False

def preload_all():
    """Preload key assets into memory."""
    common_assets = [
        'splash_background', 'login_background', 'lobby_background',
        'game_logo', 'logo_splash', 'game_map', 'minimap_hud',
        'char_male', 'char_female', 'player_character', 'pet_panda',
        'avatar_default',
        'rank_bronze', 'rank_silver', 'rank_gold', 'rank_platinum',
        'rank_diamond', 'rank_heroic', 'rank_master',
        'weapon_crimson_blaze', 'weapon_golden_eagle', 'weapon_frostbite_sniper',
        'item_helmet', 'item_vest', 'item_backpack', 'item_medkit',
        'item_energy', 'item_booster', 'item_crate_bronze', 'item_crate_blue',
        'item_crate_tech', 'item_crate_gold'
    ]
    for asset in common_assets:
        load_image(asset)
