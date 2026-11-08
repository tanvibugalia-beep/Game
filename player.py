"""
player.py — Human-controlled Player Entity for DAKSH BATTLE.

Features:
- Complete weapon loadout (Slot 1: Primary, Slot 2: Secondary, Slot 3: Pistol)
- Real ballistic firing with magazine capacity, reserve ammo, and reload (R key)
- Multi-pellet spread for shotguns (Thunder SPAS, Double Striker)
- Weapon switching (1, 2, 3 keys)
- Emote system with 3D character animation (B key)
- WASD movement, sprint, jump, gravity, terrain following
- Health (HP 100/100) and Armor Shield (100/100)
"""
import math
import random
import settings
from math3d import Vec3
from renderer import draw_box, draw_sphere, draw_cylinder
from weapons import WeaponInstance
from auth_manager import auth_manager


class Player:
    """Third-person battle-royale operator for DAKSH BATTLE."""

    COLLISION_RADIUS = 0.45

    def __init__(self, spawn_pos: Vec3):
        self.pos    = spawn_pos.copy()
        self.vel    = Vec3()
        self.yaw    = 0.0       # visual facing direction (degrees)

        # Stats
        self.hp      = settings.PLAYER_MAX_HP
        self.shield  = settings.PLAYER_MAX_SHIELD
        self.alive   = True
        self.score   = 0
        self.kills   = 0

        # Load weapons from active profile
        user_prof = auth_manager.current_user or {}
        eq_map = user_prof.get("equipped_weapons", {})
        ar_name = eq_map.get("AR", "Crimson Blaze")
        smg_name = eq_map.get("SMG", "Cobra MP5")
        pst_name = eq_map.get("Pistol", "Tactical G18")

        self.weapons = [
            WeaponInstance(ar_name),
            WeaponInstance(smg_name),
            WeaponInstance(pst_name),
        ]
        self.active_slot = 0

        # Timers & Status
        self.invuln_timer      = 0.0
        self.speed_boost_timer = 0.0
        self.on_ground         = True
        self._vy               = 0.0

        # Emote state
        self.current_emote     = None    # None, 'wave', 'dance', 'celebration', 'thumbs_up'
        self.emote_timer       = 0.0

    @property
    def active_weapon(self) -> WeaponInstance:
        return self.weapons[self.active_slot]

    @property
    def is_invulnerable(self):
        return self.invuln_timer > 0

    def switch_weapon(self, slot_idx: int):
        """Switch active weapon slot (0=Primary, 1=Secondary, 2=Pistol)."""
        if 0 <= slot_idx < len(self.weapons) and slot_idx != self.active_slot:
            self.active_slot = slot_idx
            # Cancel reload on weapon switch
            self.active_weapon.is_reloading = False

    def trigger_emote(self, emote_name: str = "wave"):
        """Trigger a character emote."""
        self.current_emote = emote_name.lower()
        self.emote_timer = 2.5

    def take_damage(self, amount: float):
        if self.invuln_timer > 0:
            return
        if self.shield > 0:
            absorbed = min(self.shield, amount)
            self.shield -= absorbed
            amount -= absorbed
        self.hp = max(0, self.hp - amount)
        if self.hp <= 0:
            self.alive = False

    def heal(self, amount: float):
        self.hp = min(settings.PLAYER_MAX_HP, self.hp + amount)

    def add_shield(self, amount: float):
        self.shield = min(settings.PLAYER_MAX_SHIELD, self.shield + amount)

    def apply_speed_boost(self):
        self.speed_boost_timer = settings.PICKUP_SPEED_DUR

    def respawn(self, pos: Vec3):
        self.pos   = pos.copy()
        self.vel   = Vec3()
        self._vy   = 0.0
        self.hp    = settings.PLAYER_MAX_HP
        self.shield = int(settings.PLAYER_MAX_SHIELD * 0.5)
        self.alive = True
        self.invuln_timer = settings.PLAYER_RESPAWN_INVULN

    # ── Update ────────────────────────────────────────────────────────────────

    def update(self, dt: float, keys: dict, camera_fwd: Vec3,
               camera_right: Vec3, arena, shoot_requested: bool) -> list:
        """
        Update player movement, ballistics, weapon switching, and reload.
        Returns list of projectile creation requests.
        """
        projectile_requests = []
        if not self.alive:
            return projectile_requests

        # Update active weapon timer
        for w in self.weapons:
            w.update(dt)

        self.invuln_timer      = max(0.0, self.invuln_timer - dt)
        self.speed_boost_timer = max(0.0, self.speed_boost_timer - dt)

        # Emote timer
        if self.emote_timer > 0:
            self.emote_timer -= dt
            if self.emote_timer <= 0:
                self.current_emote = None

        # Weapon switching keys
        if keys.get('1'): self.switch_weapon(0)
        elif keys.get('2'): self.switch_weapon(1)
        elif keys.get('3'): self.switch_weapon(2)

        # Reload key
        if keys.get('r'):
            self.active_weapon.start_reload()

        # Emote key (B)
        if keys.get('b') and self.current_emote is None:
            self.trigger_emote('dance')

        # ── Movement direction from keys ──────────────────────────────────────
        move = Vec3()
        if keys.get('w'): move = move + camera_fwd
        if keys.get('s'): move = move - camera_fwd
        if keys.get('a'): move = move - camera_right
        if keys.get('d'): move = move + camera_right

        move.y = 0
        if move.length() > 0.01:
            move = move.normalized()
            self.yaw = math.degrees(math.atan2(move.x, move.z))
            # Moving cancels emote
            if self.current_emote:
                self.current_emote = None
                self.emote_timer = 0.0

        speed = settings.PLAYER_SPEED
        if keys.get('shift'):
            speed *= settings.PLAYER_SPRINT_MULT
        if self.speed_boost_timer > 0:
            speed *= settings.PICKUP_SPEED_MULT

        # Apply movement with collision
        new_x = self.pos.x + move.x * speed * dt
        new_z = self.pos.z + move.z * speed * dt

        if not arena.collides_with_solid(new_x, self.pos.z, self.COLLISION_RADIUS):
            self.pos.x = new_x
        if not arena.collides_with_solid(self.pos.x, new_z, self.COLLISION_RADIUS):
            self.pos.z = new_z

        self.pos.x, self.pos.z = arena.clamp_to_boundary(self.pos.x, self.pos.z)

        # ── Gravity + jump ────────────────────────────────────────────────────
        ground_y = arena.ground_height(self.pos.x, self.pos.z)

        if self.on_ground and keys.get('space'):
            self._vy = settings.PLAYER_JUMP_HEIGHT
            self.on_ground = False
            self.current_emote = None

        if not self.on_ground:
            self._vy -= settings.PLAYER_GRAVITY * dt
            self.pos.y += self._vy * dt

        if self.pos.y <= ground_y:
            self.pos.y = ground_y
            self._vy   = 0.0
            self.on_ground = True

        # ── Firing with Weapon Mechanics ──────────────────────────────────────
        weap = self.active_weapon
        if shoot_requested and weap.can_shoot():
            fired = weap.shoot()
            if fired:
                self.current_emote = None
                base_dir = camera_fwd.copy()
                base_dir.y = 0.0
                base_dir = base_dir.normalized()

                spawn_pos = Vec3(self.pos.x + base_dir.x * 1.0,
                                 self.pos.y + 1.4,
                                 self.pos.z + base_dir.z * 1.0)

                # Generate projectiles (multiple for shotgun, single for others)
                pellets = weap.pellets
                spread = weap.spread

                for _ in range(pellets):
                    # Apply angular spread
                    sx = random.uniform(-spread, spread) if spread > 0 else 0
                    sy = random.uniform(-spread * 0.5, spread * 0.5) if spread > 0 else 0
                    sz = random.uniform(-spread, spread) if spread > 0 else 0

                    pdir = Vec3(base_dir.x + sx, base_dir.y + sy, base_dir.z + sz).normalized()
                    projectile_requests.append({
                        'pos': spawn_pos,
                        'dir': pdir,
                        'owner': 'player',
                        'damage': weap.damage,
                    })

        return projectile_requests

    # ── 3D Character Drawing ──────────────────────────────────────────────────

    def draw(self):
        if not self.alive:
            return
        x, y, z = self.pos.x, self.pos.y, self.pos.z

        # Flicker during invulnerability
        import time
        if self.invuln_timer > 0 and int(time.time() * 8) % 2 == 0:
            return

        from OpenGL.GL import glPushMatrix, glPopMatrix, glRotatef, glTranslatef
        glPushMatrix()
        glTranslatef(x, y, z)
        glRotatef(-self.yaw, 0, 1, 0)

        # Emote animation offsets
        l_arm_y = 1.05
        r_arm_y = 1.05
        l_arm_rot = 0
        r_arm_rot = 0
        body_bob = 0.0

        if self.current_emote:
            anim_t = (2.5 - self.emote_timer) * 8.0
            if self.current_emote == 'wave':
                r_arm_y = 1.45 + math.sin(anim_t) * 0.15
                r_arm_rot = 35 + math.sin(anim_t * 2) * 25
            elif self.current_emote == 'dance':
                body_bob = math.sin(anim_t * 2) * 0.12
                r_arm_y = 1.30 + math.sin(anim_t) * 0.20
                l_arm_y = 1.30 - math.sin(anim_t) * 0.20
            elif self.current_emote in ('celebration', 'thumbs_up'):
                r_arm_y = 1.50
                l_arm_y = 1.50

        # Torso / Tactical Jacket (Crimson Red with Black Inner Vest)
        draw_box(0, 1.1 + body_bob, 0, 0.72, 0.95, 0.42, settings.COLOR_CRIMSON)
        draw_box(0, 1.12 + body_bob, -0.02, 0.46, 0.85, 0.44, (25, 25, 30))

        # Golden Crown Insignia on Back
        draw_box(0, 1.25 + body_bob, 0.22, 0.28, 0.22, 0.04, settings.COLOR_GOLD)

        # Tactical Backpack on Back
        draw_box(0, 1.05 + body_bob, 0.28, 0.42, 0.55, 0.25, (30, 20, 45))
        draw_box(0, 1.05 + body_bob, 0.41, 0.25, 0.30, 0.04, (180, 50, 240))

        # Head / Hair / Tactical Mask
        draw_sphere(0, 1.88 + body_bob, 0, 0.30, (230, 195, 175))
        draw_box(0, 2.05 + body_bob, -0.02, 0.48, 0.22, 0.50, (30, 30, 35))
        draw_box(0, 1.82 + body_bob, -0.22, 0.34, 0.16, 0.15, (25, 25, 30))
        draw_box(0, 1.94 + body_bob, -0.25, 0.32, 0.08, 0.04, (255, 215, 60))

        # Tactical Legs & Combat Boots
        draw_box(-0.19, 0.42, 0, 0.26, 0.65, 0.28, (28, 28, 35))
        draw_box( 0.19, 0.42, 0, 0.26, 0.65, 0.28, (28, 28, 35))
        draw_box(-0.19, 0.12, 0.04, 0.28, 0.24, 0.36, (200, 35, 45))
        draw_box( 0.19, 0.12, 0.04, 0.28, 0.24, 0.36, (200, 35, 45))

        # Arms
        draw_box(-0.46, l_arm_y + body_bob, 0, 0.20, 0.68, 0.22, settings.COLOR_CRIMSON)
        draw_box(-0.46, l_arm_y - 0.33 + body_bob, 0.02, 0.22, 0.24, 0.24, (25, 25, 30))
        draw_box( 0.46, r_arm_y + body_bob, 0, 0.20, 0.68, 0.22, settings.COLOR_CRIMSON)
        draw_box( 0.46, r_arm_y - 0.33 + body_bob, 0.02, 0.22, 0.24, 0.24, (25, 25, 30))

        # Equipped Weapon in Hands
        weap = self.active_weapon
        wcol = weap.spec.get("color", (220, 35, 45))
        draw_box(0.24, 0.95 + body_bob, -0.55, 0.12, 0.16, 0.75, wcol)
        draw_box(0.24, 0.98 + body_bob, -0.85, 0.06, 0.06, 0.35, (30, 30, 35))
        draw_box(0.24, 0.82 + body_bob, -0.45, 0.08, 0.18, 0.14, (255, 195, 30))
        draw_box(0.24, 1.08 + body_bob, -0.50, 0.08, 0.10, 0.25, (35, 180, 255))

        glPopMatrix()
