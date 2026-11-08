"""
bot_ai.py — Bot entities with a simple Finite State Machine AI.

States:
  PATROL  → wander around a home point, shoot if player in range
  CHASE   → move toward detected target
  DODGE   → strafe sideways briefly after being shot
  RETREAT → back away when health is low

Two bot flavours:
  • TrainingBot  (yellow)  — slower, friendlier, teaches player
  • RivalBot     (orange)  — faster, more aggressive
"""
import math
import random
import settings
from math3d import Vec3
from renderer import draw_box, draw_sphere, draw_cylinder


# ── State constants ────────────────────────────────────────────────────────────
STATE_PATROL  = 'patrol'
STATE_CHASE   = 'chase'
STATE_DODGE   = 'dodge'
STATE_RETREAT = 'retreat'
STATE_DEAD    = 'dead'


class Bot:
    """
    Base bot class. Sub-classed by TrainingBot and RivalBot.
    """

    COLLISION_RADIUS = 0.45

    def __init__(self, spawn_pos: Vec3, bot_id: int, difficulty: str):
        self.pos       = spawn_pos.copy()
        self.vel       = Vec3()
        self.yaw       = random.uniform(0, 360)
        self.bot_id    = bot_id
        self.difficulty = difficulty
        self.alive     = True

        self.hp        = settings.BOT_MAX_HP
        self.speed     = settings.BOT_SPEEDS.get(difficulty, 3.8)
        self.shoot_cd  = settings.BOT_SHOOT_CDS.get(difficulty, 1.2)
        self._shoot_timer = random.uniform(0, self.shoot_cd)

        # Patrol home base
        self.home      = spawn_pos.copy()
        self._patrol_target = self._new_patrol_target()
        self._patrol_timer  = 0.0

        # Dodge state
        self._dodge_dir   = Vec3()
        self._dodge_timer = 0.0

        # State machine
        self.state = STATE_PATROL

        # Bot colour (overridden by subclasses)
        self.color = settings.BOT_PATROL_COLOR

        # Gravity
        self._vy       = 0.0
        self.on_ground = True

    # ── Helpers ───────────────────────────────────────────────────────────────

    def _new_patrol_target(self) -> Vec3:
        angle  = random.uniform(0, 2*math.pi)
        radius = random.uniform(3, settings.BOT_PATROL_RADIUS)
        return Vec3(
            self.home.x + math.cos(angle) * radius,
            0,
            self.home.z + math.sin(angle) * radius,
        )

    def take_damage(self, amount: float):
        self.hp -= amount
        if self.hp <= 0:
            self.hp    = 0
            self.alive = False
            self.state = STATE_DEAD
        else:
            # React to being hit → dodge
            self.state        = STATE_DODGE
            self._dodge_timer = random.uniform(0.4, 0.9)
            angle = random.uniform(0, 2*math.pi)
            self._dodge_dir   = Vec3(math.cos(angle), 0, math.sin(angle))

    # ── State machine ─────────────────────────────────────────────────────────

    def _dist_to(self, other_pos: Vec3) -> float:
        dx = self.pos.x - other_pos.x
        dz = self.pos.z - other_pos.z
        return math.sqrt(dx*dx + dz*dz)

    def _face_toward(self, target: Vec3):
        dx = target.x - self.pos.x
        dz = target.z - self.pos.z
        self.yaw = math.degrees(math.atan2(dx, dz))

    def _move_toward(self, target: Vec3, speed: float, dt: float, arena) -> bool:
        """Move one step toward target. Returns True if arrived."""
        dx = target.x - self.pos.x
        dz = target.z - self.pos.z
        dist = math.sqrt(dx*dx + dz*dz)
        if dist < 0.5:
            return True
        nx = dx / dist; nz = dz / dist
        self._face_toward(target)
        new_x = self.pos.x + nx * speed * dt
        new_z = self.pos.z + nz * speed * dt
        if not arena.collides_with_solid(new_x, self.pos.z, self.COLLISION_RADIUS):
            self.pos.x = new_x
        if not arena.collides_with_solid(self.pos.x, new_z, self.COLLISION_RADIUS):
            self.pos.z = new_z
        self.pos.x, self.pos.z = arena.clamp_to_boundary(self.pos.x, self.pos.z)
        return False

    def update(self, dt: float, player, arena) -> list:
        """
        Tick the bot AI. Returns a list of projectile spawn requests.
        """
        proj_requests = []
        if not self.alive:
            return proj_requests

        # ── Gravity ──────────────────────────────────────────────────────────
        ground_y = arena.ground_height(self.pos.x, self.pos.z)
        if not self.on_ground:
            self._vy -= settings.PLAYER_GRAVITY * dt
            self.pos.y += self._vy * dt
        if self.pos.y <= ground_y:
            self.pos.y  = ground_y
            self._vy    = 0.0
            self.on_ground = True

        # ── Shoot timer ──────────────────────────────────────────────────────
        self._shoot_timer = max(0.0, self._shoot_timer - dt)

        # ── Perception ───────────────────────────────────────────────────────
        dist_to_player = self._dist_to(player.pos) if player.alive else 9999

        # ── Transitions ──────────────────────────────────────────────────────
        if self.state != STATE_DODGE:
            if self.hp < settings.BOT_MAX_HP * 0.25:
                self.state = STATE_RETREAT
            elif dist_to_player < settings.BOT_DETECT_RANGE:
                self.state = STATE_CHASE
            elif self.state == STATE_CHASE and dist_to_player > settings.BOT_DETECT_RANGE * 1.3:
                self.state = STATE_PATROL

        # ── State actions ─────────────────────────────────────────────────────
        if self.state == STATE_PATROL:
            arrived = self._move_toward(self._patrol_target, self.speed * 0.7, dt, arena)
            if arrived:
                self._patrol_target = self._new_patrol_target()

        elif self.state == STATE_CHASE:
            # Move toward player (stop at comfortable range)
            if dist_to_player > 6.0:
                self._move_toward(player.pos, self.speed, dt, arena)
            self._face_toward(player.pos)
            # Shoot if ready
            if self._shoot_timer <= 0 and player.alive:
                self._shoot_timer = self.shoot_cd
                dx = player.pos.x - self.pos.x
                dy = (player.pos.y + 1.0) - (self.pos.y + 1.4)
                dz = player.pos.z - self.pos.z
                d  = math.sqrt(dx*dx + dy*dy + dz*dz)
                if d > 0.01:
                    direction = Vec3(dx/d, dy/d, dz/d)
                    spawn = Vec3(self.pos.x + direction.x,
                                 self.pos.y + 1.4,
                                 self.pos.z + direction.z)
                    proj_requests.append({
                        'pos':   spawn,
                        'dir':   direction,
                        'owner': f'bot_{self.bot_id}',
                    })

        elif self.state == STATE_DODGE:
            self._dodge_timer -= dt
            new_x = self.pos.x + self._dodge_dir.x * self.speed * 1.2 * dt
            new_z = self.pos.z + self._dodge_dir.z * self.speed * 1.2 * dt
            if not arena.collides_with_solid(new_x, self.pos.z, self.COLLISION_RADIUS):
                self.pos.x = new_x
            if not arena.collides_with_solid(self.pos.x, new_z, self.COLLISION_RADIUS):
                self.pos.z = new_z
            self.pos.x, self.pos.z = arena.clamp_to_boundary(self.pos.x, self.pos.z)
            if self._dodge_timer <= 0:
                self.state = STATE_CHASE

        elif self.state == STATE_RETREAT:
            # Move away from player
            dx = self.pos.x - player.pos.x
            dz = self.pos.z - player.pos.z
            d  = math.sqrt(dx*dx + dz*dz) + 0.001
            retreat_target = Vec3(
                self.pos.x + (dx/d) * 8,
                0,
                self.pos.z + (dz/d) * 8,
            )
            self._move_toward(retreat_target, self.speed, dt, arena)
            if dist_to_player > 20:
                self.state = STATE_PATROL

        return proj_requests

    # ── Drawing ───────────────────────────────────────────────────────────────

    def draw(self):
        if not self.alive:
            return
        x, y, z = self.pos.x, self.pos.y, self.pos.z
        col = self.color

        from OpenGL.GL import glPushMatrix, glPopMatrix, glRotatef, glTranslatef
        glPushMatrix()
        glTranslatef(x, y, z)
        glRotatef(-self.yaw, 0, 1, 0)

        # Robot body (slightly chunky)
        draw_box(0, 1.0, 0, 0.75, 1.1, 0.5, col)
        # Head (square robot head)
        draw_box(0, 1.9, 0, 0.55, 0.50, 0.50, col)
        # Eye visor
        draw_box(0, 1.95, -0.26, 0.35, 0.15, 0.05, (255, 230, 50))
        # Legs
        draw_box(-0.20, 0.30, 0, 0.28, 0.60, 0.30, col)
        draw_box( 0.20, 0.30, 0, 0.28, 0.60, 0.30, col)
        # Arms
        draw_box(-0.52, 1.0, 0, 0.22, 0.70, 0.22, col)
        draw_box( 0.52, 1.0, 0, 0.22, 0.70, 0.22, col)
        # Antenna
        draw_cylinder(0, 2.15, 0, 0.04, 0.35, col, slices=5)
        draw_sphere(0, 2.52, 0, 0.09, (255, 80, 80), slices=5, stacks=4)

        glPopMatrix()

        # Health bar above bot
        self._draw_health_bar(x, y + 2.8, z)

    def _draw_health_bar(self, x, y, z):
        """Billboard health bar above the bot."""
        from OpenGL.GL import (glDisable, glEnable, GL_LIGHTING, GL_DEPTH_TEST,
                                glBegin, glEnd, GL_QUADS, glColor4f, glVertex3f,
                                glLineWidth, GL_LINES, glNormal3f)
        frac = self.hp / settings.BOT_MAX_HP
        w = 1.2
        glDisable(GL_LIGHTING)

        glColor4f(0.2, 0.2, 0.2, 0.8)
        glBegin(GL_QUADS)
        glVertex3f(x - w/2, y,       z)
        glVertex3f(x + w/2, y,       z)
        glVertex3f(x + w/2, y + 0.18, z)
        glVertex3f(x - w/2, y + 0.18, z)
        glEnd()

        r = 1.0 - frac; g = frac; b = 0.1
        glColor4f(r, g, b, 1.0)
        glBegin(GL_QUADS)
        glVertex3f(x - w/2,         y,        z + 0.01)
        glVertex3f(x - w/2 + w*frac,y,        z + 0.01)
        glVertex3f(x - w/2 + w*frac,y + 0.15, z + 0.01)
        glVertex3f(x - w/2,         y + 0.15, z + 0.01)
        glEnd()

        glEnable(GL_LIGHTING)


class TrainingBot(Bot):
    """Slower, friendlier training robot (yellow)."""
    def __init__(self, spawn_pos, bot_id, difficulty):
        super().__init__(spawn_pos, bot_id, difficulty)
        self.color = settings.BOT_PATROL_COLOR
        # Training bots are always a bit slower
        self.speed *= 0.8
        self.shoot_cd *= 1.4


class RivalBot(Bot):
    """Faster, more aggressive rival bot (orange)."""
    def __init__(self, spawn_pos, bot_id, difficulty):
        super().__init__(spawn_pos, bot_id, difficulty)
        self.color = settings.BOT_RIVAL_COLOR
