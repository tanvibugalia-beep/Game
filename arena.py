"""
arena.py — Nexus Arena island map.

Generates all static geometry: terrain patches, roads, hills,
trees, rocks, buildings and perimeter walls.
Everything is stored as a list of draw-call descriptors so that
arena.draw() can render it every frame without rebuilding geometry.
"""
import math
import random
import settings
from renderer import (
    draw_box, draw_cylinder, draw_cone, draw_sphere,
    draw_flat_quad, draw_rect_outline_xz
)


class TreeObject:
    def __init__(self, x, z):
        self.x = x
        self.z = z
        # Random variety
        self.trunk_h = random.uniform(2.5, 4.5)
        self.trunk_r  = random.uniform(0.25, 0.40)
        self.canopy_r = random.uniform(1.8, 3.0)
        self.canopy_y = self.trunk_h * 0.7

    def draw(self):
        draw_cylinder(self.x, 0, self.z,
                      self.trunk_r, self.trunk_h,
                      settings.TREE_TRUNK_COLOR)
        draw_sphere(self.x, self.canopy_y + self.canopy_r * 0.5, self.z,
                    self.canopy_r, settings.TREE_LEAF_COLOR)

    def collides_xz(self, x, z, radius=0.5):
        dx = x - self.x; dz = z - self.z
        return math.sqrt(dx*dx + dz*dz) < self.trunk_r + radius


class RockObject:
    def __init__(self, x, z):
        self.x = x
        self.z = z
        self.w = random.uniform(1.0, 2.5)
        self.h = random.uniform(0.6, 1.4)
        self.d = random.uniform(1.0, 2.5)

    def draw(self):
        draw_box(self.x, self.h/2, self.z,
                 self.w, self.h, self.d,
                 settings.ROCK_COLOR)

    def collides_xz(self, x, z, radius=0.5):
        dx = abs(x - self.x) - self.w/2
        dz = abs(z - self.z) - self.d/2
        px = max(dx, 0); pz = max(dz, 0)
        return math.sqrt(px*px + pz*pz) < radius


class BuildingObject:
    def __init__(self, x, z, w, h, d, color):
        self.x = x; self.z = z
        self.w = w; self.h = h; self.d = d
        self.color = color

    def draw(self):
        # Main body
        draw_box(self.x, self.h/2, self.z,
                 self.w, self.h, self.d, self.color)
        # Roof ridge (darker top)
        draw_box(self.x, self.h + 0.3, self.z,
                 self.w + 0.2, 0.5, self.d + 0.2,
                 (max(0, self.color[0]-30),
                  max(0, self.color[1]-30),
                  max(0, self.color[2]-30)))

    def collides_xz(self, x, z, radius=0.5):
        dx = abs(x - self.x) - self.w/2
        dz = abs(z - self.z) - self.d/2
        px = max(dx, 0); pz = max(dz, 0)
        return math.sqrt(px*px + pz*pz) < radius


class TransmissionTower:
    """Futuristic communications tower seen across the Daksh Battle island."""
    def __init__(self, x, z, h=16.0):
        self.x = x
        self.z = z
        self.h = h

    def draw(self):
        # Base truss
        draw_box(self.x, self.h * 0.35, self.z, 1.8, self.h * 0.7, 1.8, (70, 75, 85))
        # Upper pylon
        draw_cylinder(self.x, self.h * 0.7, self.z, 0.45, self.h * 0.3, (190, 45, 45), slices=6)
        # Antenna spire
        draw_cylinder(self.x, self.h, self.z, 0.12, 3.5, (220, 220, 230), slices=4)
        # Blinking beacon
        import time
        beacon_on = int(time.time() * 2.5) % 2 == 0
        beacon_col = (255, 40, 40) if beacon_on else (100, 20, 20)
        draw_sphere(self.x, self.h + 3.6, self.z, 0.32, beacon_col, slices=6, stacks=4)

    def collides_xz(self, x, z, radius=0.5):
        dx = x - self.x
        dz = z - self.z
        return math.sqrt(dx*dx + dz*dz) < 1.2 + radius


class AirshipObject:
    """Daksh Battle sky airship / supply blimp hovering high over the island."""
    def __init__(self, cx=0, cy=35, cz=0, r=45):
        self.cx = cx
        self.cy = cy
        self.cz = cz
        self.r = r

    def draw(self):
        import time
        t = time.time() * 0.05
        ax = self.cx + math.cos(t) * self.r
        az = self.cz + math.sin(t) * self.r
        # Main hull (Zeppelin shape: elongated boxes/spheres)
        draw_box(ax, self.cy, az, 14.0, 4.5, 4.5, (30, 45, 90)) # Deep Navy Blue
        draw_sphere(ax - 7.0, self.cy, az, 2.2, (225, 35, 45))  # Crimson Nose
        draw_sphere(ax + 7.0, self.cy, az, 2.2, (255, 195, 30)) # Golden Tail
        # Gondola / Cabin below
        draw_box(ax, self.cy - 2.8, az, 6.0, 1.2, 1.8, (230, 230, 240))
        # Golden banner along side
        draw_box(ax, self.cy, az, 10.0, 1.2, 4.6, (255, 195, 30))


class HillObject:
    def __init__(self, x, z, r, h):
        self.x = x; self.z = z; self.r = r; self.h = h

    def height_at(self, x, z):
        """Return ground Y at world (x,z) due to this hill (smooth cosine bump)."""
        dx = x - self.x; dz = z - self.z
        d = math.sqrt(dx*dx + dz*dz)
        if d >= self.r:
            return 0.0
        t = d / self.r
        return self.h * 0.5 * (1 + math.cos(math.pi * t))

    def draw(self):
        # Draw the hill as a stack of flattened spheres (poor-man's hill)
        slices = 16
        for k in range(slices):
            frac = k / slices
            alt  = self.h * math.sin(math.pi * frac / 2)
            rr   = self.r * math.cos(math.pi * frac / 2)
            g = int(settings.GRASS_COLOR[1] - 20 * frac)
            draw_cylinder(self.x, alt, self.z,
                          rr, 0.6, (55, g, 40), slices=20)


class Arena:
    """
    Generates and draws the full island arena map.
    Also provides terrain-height queries and collision helpers.
    """

    def __init__(self, seed=42):
        rng = random.Random(seed)
        self.half = settings.ARENA_HALF

        # ── Hills ──────────────────────────────────────────────────────────
        self.hills = []
        hill_specs = [
            (20, 15, 22, 5),
            (-30, -10, 18, 4),
            (5, 30, 16, 6),
            (-15, 20, 12, 3.5),
            (35, -25, 14, 4),
        ]
        for hx, hz, hr, hh in hill_specs:
            self.hills.append(HillObject(hx, hz, hr, hh))

        # ── Trees ──────────────────────────────────────────────────────────
        self.trees = []
        attempts = 0
        while len(self.trees) < 60 and attempts < 500:
            attempts += 1
            x = rng.uniform(-self.half + 5, self.half - 5)
            z = rng.uniform(-self.half + 5, self.half - 5)
            # Keep clear of spawn area
            if math.sqrt(x*x + z*z) < 12:
                continue
            # No overlap with existing trees
            if any(t.collides_xz(x, z, 3.0) for t in self.trees):
                continue
            self.trees.append(TreeObject(x, z))

        # ── Rocks ──────────────────────────────────────────────────────────
        self.rocks = []
        for _ in range(35):
            x = rng.uniform(-self.half + 3, self.half - 3)
            z = rng.uniform(-self.half + 3, self.half - 3)
            if math.sqrt(x*x + z*z) < 8:
                continue
            self.rocks.append(RockObject(x, z))

        # ── Buildings ──────────────────────────────────────────────────────
        self.buildings = []
        building_specs = [
            ( 25,  25, 8, 5, 6,  settings.BUILDING_COLOR),
            (-25,  20, 6, 7, 5,  settings.BUILDING2_COLOR),
            ( 20, -30, 10,4, 8,  settings.BUILDING_COLOR),
            (-20, -25, 7, 6, 7,  settings.BUILDING2_COLOR),
            (  0,  45, 12,8, 10, settings.BUILDING_COLOR),
            (-40,  10, 8, 5, 6,  settings.BUILDING2_COLOR),
            ( 40, -10, 6, 9, 5,  settings.BUILDING_COLOR),
            (-10, -50, 9, 6, 8,  settings.BUILDING2_COLOR),
            ( 50,  30, 7, 5, 6,  settings.BUILDING_COLOR),
            (-50, -30, 8, 7, 7,  settings.BUILDING2_COLOR),
        ]
        for spec in building_specs:
            self.buildings.append(BuildingObject(*spec))

        # ── Road segments (drawn as flat quads) ────────────────────────────
        # Simple cross-road pattern through centre
        self.roads = [
            (-self.half, -6, self.half, 6),   # E-W road
            (-6, -self.half, 6, self.half),   # N-S road
            (10, -6, 40, 6),                  # East branch
            (-40, -6, -10, 6),                # West branch
        ]

        # ── Transmission Towers ───────────────────────────────────────────────
        self.towers = [
            TransmissionTower(30, -35, 18.0),
            TransmissionTower(-35, 35, 20.0),
            TransmissionTower(-45, -40, 16.0),
            TransmissionTower(45, 40, 19.0),
        ]

        # ── Sky Airship ───────────────────────────────────────────────────────
        self.airship = AirshipObject(cx=0, cy=32, cz=0, r=48)

        # All solid objects (for collision)
        self.solid_objects = self.trees + self.rocks + self.buildings + self.towers

    # ── Terrain height ────────────────────────────────────────────────────────

    def ground_height(self, x, z):
        """Return terrain Y at world position (x,z)."""
        y = 0.0
        for h in self.hills:
            y += h.height_at(x, z)
        return y

    # ── Collision ─────────────────────────────────────────────────────────────

    def collides_with_solid(self, x, z, radius=0.45):
        """Return True if the circle (x,z,radius) overlaps any solid object."""
        for obj in self.solid_objects:
            if obj.collides_xz(x, z, radius):
                return True
        return False

    def clamp_to_boundary(self, x, z, margin=1.0):
        """Keep position inside arena border (soft wall)."""
        limit = self.half - margin
        x = max(-limit, min(limit, x))
        z = max(-limit, min(limit, z))
        return x, z

    # ── Drawing ───────────────────────────────────────────────────────────────

    def draw(self):
        # ── Ground plane ────────────────────────────────────────────────────
        draw_flat_quad(-self.half, -self.half,
                        self.half,  self.half,
                        0.0, settings.GRASS_COLOR)

        # ── Outer boundary wall (low fence) ─────────────────────────────────
        draw_box(0, 0.5, -self.half, self.half*2, 1.0, 0.5,
                 (80, 100, 80))
        draw_box(0, 0.5,  self.half, self.half*2, 1.0, 0.5,
                 (80, 100, 80))
        draw_box(-self.half, 0.5, 0, 0.5, 1.0, self.half*2,
                 (80, 100, 80))
        draw_box( self.half, 0.5, 0, 0.5, 1.0, self.half*2,
                 (80, 100, 80))

        # ── Roads ────────────────────────────────────────────────────────────
        for (x1,z1,x2,z2) in self.roads:
            draw_flat_quad(x1, z1, x2, z2, 0.01, settings.ROAD_COLOR)

        # ── Hills ────────────────────────────────────────────────────────────
        for h in self.hills:
            h.draw()

        # ── Trees ────────────────────────────────────────────────────────────
        for t in self.trees:
            t.draw()

        # ── Rocks ────────────────────────────────────────────────────────────
        for r in self.rocks:
            r.draw()

        # ── Buildings ────────────────────────────────────────────────────────
        for b in self.buildings:
            b.draw()

        # ── Towers ───────────────────────────────────────────────────────────
        for tw in self.towers:
            tw.draw()

        # ── Airship ──────────────────────────────────────────────────────────
        self.airship.draw()
