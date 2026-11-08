"""
projectiles.py — Paint-blob / energy-tag projectile system for Nexus Arena.

Projectiles travel in a straight line, apply damage on hit,
and are removed after their lifetime or when they hit terrain/objects.
"""
import math
import settings
from math3d import Vec3
from renderer import draw_sphere


class Projectile:
    """A single paint-blob projectile."""

    def __init__(self, pos: Vec3, direction: Vec3, owner: str, damage: int = None):
        self.pos     = pos.copy()
        self.dir     = direction.normalized()
        self.owner   = owner          # 'player' or bot id
        self.alive   = True
        self.damage  = damage if damage is not None else settings.PROJ_DAMAGE
        self.timer   = settings.PROJ_LIFETIME
        self.radius  = settings.PROJ_RADIUS

    def update(self, dt: float, arena) -> bool:
        """
        Move the projectile. Return True if it should be destroyed.
        """
        if not self.alive:
            return True

        self.timer -= dt
        if self.timer <= 0:
            self.alive = False
            return True

        # Move
        speed = settings.PROJ_SPEED
        self.pos.x += self.dir.x * speed * dt
        self.pos.y += self.dir.y * speed * dt
        self.pos.z += self.dir.z * speed * dt

        # Hit ground / terrain
        ground_y = arena.ground_height(self.pos.x, self.pos.z)
        if self.pos.y <= ground_y:
            self.alive = False
            return True

        # Hit solid objects
        if arena.collides_with_solid(self.pos.x, self.pos.z, self.radius):
            self.alive = False
            return True

        # Out of arena bounds
        limit = arena.half + 5
        if abs(self.pos.x) > limit or abs(self.pos.z) > limit:
            self.alive = False
            return True

        return False

    def hits_target(self, target_pos: Vec3, target_radius: float = 0.7) -> bool:
        """Return True if this projectile is within hit distance of target."""
        dx = self.pos.x - target_pos.x
        dy = self.pos.y - (target_pos.y + 1.0)
        dz = self.pos.z - target_pos.z
        dist_sq = dx*dx + dy*dy + dz*dz
        return dist_sq < (self.radius + target_radius) ** 2

    def draw(self):
        if not self.alive:
            return
        # Pulsing energy-tag glow effect using lifetime
        scale = 0.75 + 0.25 * math.sin(self.timer * 22)
        base_color = settings.PROJ_COLOR_GOLD if self.owner == 'player' else settings.PROJ_COLOR
        draw_sphere(self.pos.x, self.pos.y, self.pos.z,
                    self.radius * scale, base_color, slices=7, stacks=5)
        # Bright incandescent core
        core_color = (255, 245, 180) if self.owner == 'player' else (200, 255, 255)
        draw_sphere(self.pos.x, self.pos.y, self.pos.z,
                    self.radius * 0.45, core_color, slices=5, stacks=4)


class ProjectileManager:
    """Manages all active projectiles in the scene."""

    def __init__(self):
        self._projectiles: list[Projectile] = []

    def spawn(self, pos: Vec3, direction: Vec3, owner: str, damage: int = None):
        self._projectiles.append(Projectile(pos, direction, owner, damage))

    def update(self, dt: float, arena, player, bots: list):
        """
        Move all projectiles, resolve hit detection.

        Returns a list of hit-events:
          {'victim': 'player' | bot_obj, 'damage': int, 'killer': owner}
        """
        hit_events = []
        to_remove = []

        for proj in self._projectiles:
            destroyed = proj.update(dt, arena)
            if destroyed:
                to_remove.append(proj)
                continue

            # ── Hit player ───────────────────────────────────────────────────
            if proj.owner != 'player' and player.alive and not player.is_invulnerable:
                if proj.hits_target(player.pos, 0.7):
                    hit_events.append({
                        'victim': 'player',
                        'damage': proj.damage,
                        'killer': proj.owner,
                    })
                    to_remove.append(proj)
                    proj.alive = False
                    continue

            # ── Hit bots ─────────────────────────────────────────────────────
            if proj.owner == 'player':
                for bot in bots:
                    if not bot.alive:
                        continue
                    if proj.hits_target(bot.pos, 0.7):
                        hit_events.append({
                            'victim': bot,
                            'damage': proj.damage,
                            'killer': 'player',
                        })
                        to_remove.append(proj)
                        proj.alive = False
                        break

        for p in to_remove:
            if p in self._projectiles:
                self._projectiles.remove(p)

        return hit_events

    def draw(self):
        for proj in self._projectiles:
            proj.draw()

    def clear(self):
        self._projectiles.clear()
