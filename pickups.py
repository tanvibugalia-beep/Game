"""
pickups.py — Collectible items for Nexus Arena.

Three types:
  • HealthPack   — restores HP
  • ShieldPack   — restores shield
  • SpeedBoost   — temporary speed increase

Pickups glow and spin to attract attention.
"""
import math
import random
import settings
from math3d import Vec3
from renderer import draw_box, draw_sphere, draw_cylinder


class Pickup:
    """Base collectible item."""

    PICK_RADIUS = 1.2    # distance at which the player collects it

    def __init__(self, pos: Vec3, kind: str):
        self.pos   = pos.copy()
        self.kind  = kind    # 'health', 'shield', 'speed'
        self.alive = True
        self._spin = random.uniform(0, 360)
        self._bob_phase = random.uniform(0, math.pi * 2)

    def update(self, dt: float):
        self._spin      = (self._spin + 90 * dt) % 360
        self._bob_phase = (self._bob_phase + 2.0 * dt) % (math.pi * 2)

    def can_collect(self, player_pos: Vec3) -> bool:
        dx = player_pos.x - self.pos.x
        dz = player_pos.z - self.pos.z
        return math.sqrt(dx*dx + dz*dz) < self.PICK_RADIUS

    def apply_to(self, player) -> str:
        """Apply the pickup effect. Returns description string."""
        if self.kind == 'health':
            player.heal(settings.PICKUP_HP_RESTORE)
            return f"+{settings.PICKUP_HP_RESTORE} HP"
        elif self.kind == 'shield':
            player.add_shield(settings.PICKUP_SHIELD_RESTORE)
            return f"+{settings.PICKUP_SHIELD_RESTORE} Shield"
        elif self.kind == 'speed':
            player.apply_speed_boost()
            return "Speed Boost!"
        return ""

    def draw(self):
        if not self.alive:
            return
        bob_y = self.pos.y + 0.8 + math.sin(self._bob_phase) * 0.2

        from OpenGL.GL import glPushMatrix, glPopMatrix, glRotatef, glTranslatef
        glPushMatrix()
        glTranslatef(self.pos.x, bob_y, self.pos.z)
        glRotatef(self._spin, 0, 1, 0)

        if self.kind == 'health':
            # Red cross shape
            draw_box(0, 0, 0, 0.6, 0.15, 0.15, settings.PICKUP_HP_COLOR)
            draw_box(0, 0, 0, 0.15, 0.6, 0.15, settings.PICKUP_HP_COLOR)
            draw_sphere(0, 0, 0, 0.25, (150, 255, 150), slices=8, stacks=6)

        elif self.kind == 'shield':
            # Blue diamond
            draw_box(0, 0, 0, 0.45, 0.45, 0.12, settings.PICKUP_SHIELD_COLOR)
            draw_sphere(0, 0, 0, 0.22, (150, 200, 255), slices=8, stacks=6)

        elif self.kind == 'speed':
            # Yellow lightning bolt (simplified)
            draw_box( 0.05, 0.15, 0, 0.15, 0.35, 0.15, settings.PICKUP_SPEED_COLOR)
            draw_box(-0.05,-0.15, 0, 0.15, 0.35, 0.15, settings.PICKUP_SPEED_COLOR)
            draw_sphere(0, 0, 0, 0.22, (255, 240, 100), slices=8, stacks=6)

        glPopMatrix()


class PickupManager:
    """Manages all collectible pickups in the arena."""

    def __init__(self, arena, count: int = None):
        if count is None:
            count = settings.PICKUP_SPAWN_COUNT
        self._pickups: list[Pickup] = []
        self._spawn_pickups(arena, count)

    def _spawn_pickups(self, arena, count: int):
        kinds = ['health', 'shield', 'speed']
        # Spread pickups across the arena
        rng = random.Random(99)
        for i in range(count):
            for _ in range(50):
                x = rng.uniform(-arena.half * 0.85, arena.half * 0.85)
                z = rng.uniform(-arena.half * 0.85, arena.half * 0.85)
                if math.sqrt(x*x + z*z) < 10:
                    continue
                if arena.collides_with_solid(x, z, 1.5):
                    continue
                y = arena.ground_height(x, z)
                kind = kinds[i % len(kinds)]
                self._pickups.append(Pickup(Vec3(x, y, z), kind))
                break

    def update(self, dt: float, player):
        """Update animations and check for collection."""
        messages = []
        for pickup in self._pickups:
            if not pickup.alive:
                continue
            pickup.update(dt)
            if player.alive and pickup.can_collect(player.pos):
                msg = pickup.apply_to(player)
                pickup.alive = False
                messages.append(msg)
        return messages

    def draw(self):
        for p in self._pickups:
            p.draw()

    def reset(self, arena):
        self._pickups.clear()
        self._spawn_pickups(arena, settings.PICKUP_SPAWN_COUNT)
