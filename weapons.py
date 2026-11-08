"""
weapons.py — Complete Weapon Armory & Ballistic Systems for DAKSH BATTLE.

Contains fully implemented weapon definitions across ALL required categories:
- Assault Rifles (AR)
- Submachine Guns (SMG)
- Shotguns
- Pistols
- Sniper Rifles

Each weapon has unique stats:
- damage
- fire_rate (cooldown between shots)
- range_effective
- mag_size (magazine capacity)
- reserve_ammo
- spread (in radians)
- reload_time (in seconds)
- pellets (1 for standard, 8 for shotguns)
- icon and visual color
"""

WEAPON_CATEGORIES = ["AR", "SMG", "Shotgun", "Pistol", "Sniper"]

WEAPONS = {
    # ── Assault Rifles ────────────────────────────────────────────────────────
    "Crimson Blaze": {
        "name": "Crimson Blaze",
        "category": "AR",
        "description": "High-impact tactical rifle equipped with a crimson flame shroud.",
        "damage": 34,
        "fire_rate": 0.11,
        "range": 55.0,
        "mag_size": 30,
        "reserve_ammo": 120,
        "spread": 0.022,
        "reload_time": 2.1,
        "pellets": 1,
        "icon": "weapon_crimson_blaze",
        "color": (225, 35, 45)
    },
    "Golden Eagle": {
        "name": "Golden Eagle",
        "category": "AR",
        "description": "Rapid-fire precision carbine with golden titanium heat sink.",
        "damage": 29,
        "fire_rate": 0.088,
        "range": 52.0,
        "mag_size": 35,
        "reserve_ammo": 140,
        "spread": 0.018,
        "reload_time": 1.9,
        "pellets": 1,
        "icon": "weapon_golden_eagle",
        "color": (255, 195, 30)
    },

    # ── Submachine Guns ───────────────────────────────────────────────────────
    "Cobra MP5": {
        "name": "Cobra MP5",
        "category": "SMG",
        "description": "Lightweight close-quarters submachine gun with high stability.",
        "damage": 23,
        "fire_rate": 0.072,
        "range": 32.0,
        "mag_size": 32,
        "reserve_ammo": 160,
        "spread": 0.035,
        "reload_time": 1.6,
        "pellets": 1,
        "icon": "weapon_crimson_blaze",
        "color": (40, 210, 110)
    },
    "Neon Vector": {
        "name": "Neon Vector",
        "category": "SMG",
        "description": "Hyper-velocity burst SMG shredding rivals at close range.",
        "damage": 20,
        "fire_rate": 0.054,
        "range": 25.0,
        "mag_size": 33,
        "reserve_ammo": 165,
        "spread": 0.042,
        "reload_time": 1.5,
        "pellets": 1,
        "icon": "weapon_golden_eagle",
        "color": (35, 180, 255)
    },

    # ── Shotguns ──────────────────────────────────────────────────────────────
    "Thunder SPAS": {
        "name": "Thunder SPAS",
        "category": "Shotgun",
        "description": "Tactical pump-action shotgun delivering a lethal 8-pellet spread.",
        "damage": 16,  # 16 x 8 = 128 max
        "fire_rate": 0.65,
        "range": 16.0,
        "mag_size": 8,
        "reserve_ammo": 40,
        "spread": 0.11,
        "reload_time": 2.4,
        "pellets": 8,
        "icon": "weapon_crimson_blaze",
        "color": (255, 120, 30)
    },
    "Double Striker": {
        "name": "Double Striker",
        "category": "Shotgun",
        "description": "Twin-barrel powerhouse delivering immense instantaneous burst.",
        "damage": 20,  # 20 x 8 = 160 max
        "fire_rate": 0.32,
        "range": 13.0,
        "mag_size": 2,
        "reserve_ammo": 30,
        "spread": 0.14,
        "reload_time": 2.0,
        "pellets": 8,
        "icon": "weapon_golden_eagle",
        "color": (230, 60, 40)
    },

    # ── Pistols ───────────────────────────────────────────────────────────────
    "Tactical G18": {
        "name": "Tactical G18",
        "category": "Pistol",
        "description": "Reliable high-capacity sidearm with quick-draw response.",
        "damage": 22,
        "fire_rate": 0.13,
        "range": 26.0,
        "mag_size": 17,
        "reserve_ammo": 85,
        "spread": 0.028,
        "reload_time": 1.4,
        "pellets": 1,
        "icon": "weapon_crimson_blaze",
        "color": (160, 180, 210)
    },
    "Desert Hawk": {
        "name": "Desert Hawk",
        "category": "Pistol",
        "description": "Heavy .50 caliber magnum pistol with bone-crushing impact.",
        "damage": 54,
        "fire_rate": 0.36,
        "range": 38.0,
        "mag_size": 7,
        "reserve_ammo": 35,
        "spread": 0.020,
        "reload_time": 1.7,
        "pellets": 1,
        "icon": "weapon_golden_eagle",
        "color": (240, 200, 70)
    },

    # ── Sniper Rifles ─────────────────────────────────────────────────────────
    "Frostbite AWM": {
        "name": "Frostbite AWM",
        "category": "Sniper",
        "description": "Cryogenic bolt-action heavy sniper rifle with match-grade accuracy.",
        "damage": 115,
        "fire_rate": 1.25,
        "range": 120.0,
        "mag_size": 5,
        "reserve_ammo": 25,
        "spread": 0.004,
        "reload_time": 2.8,
        "pellets": 1,
        "icon": "weapon_frostbite_sniper",
        "color": (60, 215, 255)
    },
    "Shadow Kar98k": {
        "name": "Shadow Kar98k",
        "category": "Sniper",
        "description": "Agile marksman rifle built for high mobility and swift target acquisition.",
        "damage": 86,
        "fire_rate": 0.92,
        "range": 90.0,
        "mag_size": 5,
        "reserve_ammo": 30,
        "spread": 0.007,
        "reload_time": 2.3,
        "pellets": 1,
        "icon": "weapon_frostbite_sniper",
        "color": (175, 120, 240)
    }
}

class WeaponInstance:
    """An active weapon state instance held by a player or bot during a match."""

    def __init__(self, weapon_name: str):
        self.spec = WEAPONS.get(weapon_name, WEAPONS["Crimson Blaze"])
        self.name = self.spec["name"]
        self.category = self.spec["category"]
        self.damage = self.spec["damage"]
        self.fire_rate = self.spec["fire_rate"]
        self.pellets = self.spec.get("pellets", 1)
        self.spread = self.spec.get("spread", 0.02)
        self.reload_time = self.spec.get("reload_time", 2.0)
        self.mag_size = self.spec["mag_size"]
        self.reserve_max = self.spec["reserve_ammo"]

        # Dynamic state
        self.ammo_in_mag = self.mag_size
        self.ammo_reserve = self.reserve_max
        self.cooldown = 0.0
        self.is_reloading = False
        self.reload_timer = 0.0

    def update(self, dt: float):
        """Update cooldown and reload timers."""
        if self.cooldown > 0:
            self.cooldown = max(0.0, self.cooldown - dt)

        if self.is_reloading:
            self.reload_timer -= dt
            if self.reload_timer <= 0:
                self._finish_reload()

    def can_shoot(self) -> bool:
        return self.cooldown <= 0 and not self.is_reloading and self.ammo_in_mag > 0

    def start_reload(self) -> bool:
        """Trigger weapon reload if needed and ammo reserve is available."""
        if self.is_reloading or self.ammo_in_mag >= self.mag_size or self.ammo_reserve <= 0:
            return False
        self.is_reloading = True
        self.reload_timer = self.reload_time
        return True

    def _finish_reload(self):
        """Complete the reload process."""
        needed = self.mag_size - self.ammo_in_mag
        transfer = min(needed, self.ammo_reserve)
        self.ammo_in_mag += transfer
        self.ammo_reserve -= transfer
        self.is_reloading = False
        self.reload_timer = 0.0

    def shoot(self) -> bool:
        """Consume ammo and reset fire cooldown."""
        if not self.can_shoot():
            if self.ammo_in_mag <= 0 and not self.is_reloading:
                self.start_reload()
            return False

        self.ammo_in_mag -= 1
        self.cooldown = self.fire_rate

        # Auto reload on empty
        if self.ammo_in_mag <= 0 and self.ammo_reserve > 0:
            self.start_reload()

        return True

    def reload_progress(self) -> float:
        if not self.is_reloading:
            return 1.0
        return max(0.0, min(1.0, 1.0 - (self.reload_timer / max(0.01, self.reload_time))))


# Alias for cross-platform access
WEAPON_CATALOG = WEAPONS

