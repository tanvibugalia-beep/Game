"""
game_manager.py — Round logic for Nexus Arena.

Responsibilities:
  • Spawn player + bots at the start of a round
  • Track timer, score, remaining-player count
  • Manage the shrinking safe zone
  • Apply zone damage to out-of-bound entities
  • Detect win / lose conditions
  • Handle restart
"""
import math
import random
import settings
from math3d import Vec3
from player import Player
from bot_ai import TrainingBot, RivalBot
from projectiles import ProjectileManager
from pickups import PickupManager


# ── Round states ──────────────────────────────────────────────────────────────
ROUND_WAITING  = 'waiting'
ROUND_ACTIVE   = 'active'
ROUND_VICTORY  = 'victory'
ROUND_DEFEAT   = 'defeat'
ROUND_PAUSED   = 'paused'


class GameManager:
    """
    Central coordinator for one match.
    The main game loop calls update() every frame.
    """

    def __init__(self, arena):
        self.arena = arena

        diff = settings.runtime["difficulty"]
        _presets = {
            "Easy":   {"bot_count": 5,  "bot_speed": 2.5, "bot_shoot_cd": 2.0,  "zone_damage": 2.0},
            "Medium": {"bot_count": 9,  "bot_speed": 3.8, "bot_shoot_cd": 1.2,  "zone_damage": 5.0},
            "Hard":   {"bot_count": 14, "bot_speed": 5.2, "bot_shoot_cd": 0.65, "zone_damage": 10.0},
        }
        preset = _presets[diff]

        self.bot_count   = preset["bot_count"]
        self.zone_damage = preset["zone_damage"]

        # Safe-zone
        self.zone_radius      = settings.ARENA_HALF
        self.zone_center      = Vec3(0, 0, 0)
        self._shrink_elapsed  = 0.0

        # Round timer
        self.round_time   = float(settings.ROUND_DURATION)
        self.round_state  = ROUND_WAITING
        self._start_timer = 3.0   # countdown before round starts

        # Entities
        self.player           = None
        self.bots: list       = []
        self.proj_manager     = ProjectileManager()
        self.pickup_manager   = None

        # Score / notifications
        self.player_score     = 0
        self._notifications   = []   # [(text, timer)]
        self._notify_duration = 2.5
        self.match_recorded   = False
        self.last_match_summary = None

        # Startup
        self._setup_round()

    # ── Setup ─────────────────────────────────────────────────────────────────

    def _spawn_positions(self, count: int) -> list[Vec3]:
        """Generate spread-out spawn positions around the arena."""
        positions = []
        for i in range(count):
            angle  = 2 * math.pi * i / count + random.uniform(-0.3, 0.3)
            radius = random.uniform(25, 55)
            x = math.cos(angle) * radius
            z = math.sin(angle) * radius
            y = self.arena.ground_height(x, z)
            positions.append(Vec3(x, y, z))
        return positions

    def _setup_round(self):
        # Player spawns at origin
        py = self.arena.ground_height(0, 0)
        self.player = Player(Vec3(0, py, 8))

        # Bots
        self.bots = []
        diff = settings.runtime["difficulty"]
        spawns = self._spawn_positions(self.bot_count)
        training_count = max(2, self.bot_count // 3)

        for i, sp in enumerate(spawns):
            if i < training_count:
                bot = TrainingBot(sp, i, diff)
            else:
                bot = RivalBot(sp, i, diff)
            self.bots.append(bot)

        # Pickups
        self.pickup_manager = PickupManager(self.arena)

        # Reset zone / timer
        self.zone_radius     = settings.ARENA_HALF
        self._shrink_elapsed = 0.0
        self.round_time      = float(settings.ROUND_DURATION)
        self.round_state     = ROUND_WAITING
        self._start_timer    = 3.0
        self.player_score    = 0
        self._notifications  = []
        self.match_recorded  = False
        self.last_match_summary = None
        self.proj_manager.clear()

    # ── Public API ────────────────────────────────────────────────────────────

    def restart(self):
        self._setup_round()

    def notify(self, text: str):
        self._notifications.append([text, self._notify_duration])

    def get_notifications(self) -> list:
        return [n[0] for n in self._notifications]

    @property
    def alive_bots(self):
        return [b for b in self.bots if b.alive]

    @property
    def total_players(self):
        return 1 + len(self.alive_bots)

    # ── Update ────────────────────────────────────────────────────────────────

    def update(self, dt: float, keys: dict, camera,
               shoot_requested: bool, mouse_dx: float, mouse_dy: float) -> dict:
        """
        Main game-logic tick. Returns a state dict for the UI to read.
        """
        # Tick notifications
        self._notifications = [
            [txt, t - dt] for txt, t in self._notifications if t - dt > 0
        ]

        # Camera always updates (even on menus, for smooth transitions)
        camera.apply_mouse(mouse_dx, mouse_dy)
        camera.update(self.player.pos if self.player else Vec3(), dt)

        # ── Countdown ────────────────────────────────────────────────────────
        if self.round_state == ROUND_WAITING:
            self._start_timer -= dt
            if self._start_timer <= 0:
                self.round_state = ROUND_ACTIVE
                self.notify("MATCH START! Last one standing wins!")
            return self._state_dict()

        if self.round_state == ROUND_PAUSED:
            return self._state_dict()

        if self.round_state in (ROUND_VICTORY, ROUND_DEFEAT):
            return self._state_dict()

        # ── Active round ──────────────────────────────────────────────────────
        self.round_time -= dt
        if self.round_time <= 0:
            self.round_time = 0
            self._resolve_timeout()

        # ── Shrinking zone ────────────────────────────────────────────────────
        shrink_elapsed = settings.ROUND_DURATION - self.round_time
        if shrink_elapsed > settings.ARENA_SHRINK_START:
            progress = (shrink_elapsed - settings.ARENA_SHRINK_START) / max(
                1, settings.ROUND_DURATION - settings.ARENA_SHRINK_START
            )
            target_r = settings.ARENA_SHRINK_END
            start_r  = settings.ARENA_HALF
            self.zone_radius = max(target_r,
                                   start_r - (start_r - target_r) * progress)

        # ── Player update ─────────────────────────────────────────────────────
        proj_requests = self.player.update(
            dt, keys,
            camera.forward_dir, camera.right_dir,
            self.arena, shoot_requested
        )
        for req in proj_requests:
            self.proj_manager.spawn(req['pos'], req['dir'], req['owner'], req.get('damage'))

        # ── Bot updates ───────────────────────────────────────────────────────
        for bot in self.bots:
            if not bot.alive:
                continue
            bot_proj = bot.update(dt, self.player, self.arena)
            for req in bot_proj:
                self.proj_manager.spawn(req['pos'], req['dir'], req['owner'])

            # Zone damage to bots
            dx = bot.pos.x - self.zone_center.x
            dz = bot.pos.z - self.zone_center.z
            if math.sqrt(dx*dx + dz*dz) > self.zone_radius:
                bot.take_damage(self.zone_damage * dt)

        # ── Projectile resolution ─────────────────────────────────────────────
        hit_events = self.proj_manager.update(dt, self.arena, self.player, self.bots)
        for evt in hit_events:
            victim  = evt['victim']
            damage  = evt['damage']
            killer  = evt['killer']
            if victim == 'player':
                self.player.take_damage(damage)
                if not self.player.alive:
                    self.notify("You were tagged out!")
                    self.round_state = ROUND_DEFEAT
            else:
                victim.take_damage(damage)
                if not victim.alive and killer == 'player':
                    self.player_score += 10
                    self.player.kills += 1
                    self.notify(f"Bot eliminated! +10 pts")

        # ── Pickup resolution ─────────────────────────────────────────────────
        msgs = self.pickup_manager.update(dt, self.player)
        for m in msgs:
            self.notify(m)

        # ── Zone damage to player ─────────────────────────────────────────────
        dx = self.player.pos.x - self.zone_center.x
        dz = self.player.pos.z - self.zone_center.z
        player_in_zone = math.sqrt(dx*dx + dz*dz) <= self.zone_radius
        if not player_in_zone and self.player.alive:
            self.player.take_damage(self.zone_damage * dt)

        # ── Win condition ─────────────────────────────────────────────────────
        if self.player.alive and len(self.alive_bots) == 0:
            self.player_score += 50
            self.round_state = ROUND_VICTORY
            self.notify("VICTORY! You outlasted everyone!")

        if not self.player.alive and self.round_state == ROUND_ACTIVE:
            self.round_state = ROUND_DEFEAT

        # ── Record match stats into player profile ────────────────────────────
        if self.round_state in (ROUND_VICTORY, ROUND_DEFEAT) and not self.match_recorded:
            from profile import player_profile
            won = (self.round_state == ROUND_VICTORY)
            duration = int(settings.ROUND_DURATION - self.round_time)
            self.last_match_summary = player_profile.record_match_result(
                won=won, kills=self.player.kills, score=self.player_score, duration_sec=duration
            )
            self.match_recorded = True

        return self._state_dict()

    def _resolve_timeout(self):
        """Time ran out — whoever has most HP wins."""
        alive = self.alive_bots
        if self.player.alive and len(alive) == 0:
            self.round_state = ROUND_VICTORY
        elif self.player.alive:
            self.round_state = ROUND_DEFEAT
            self.notify("Time out! More bots survived.")
        else:
            self.round_state = ROUND_DEFEAT

    def _state_dict(self) -> dict:
        """Snapshot of current game state for the UI renderer."""
        p = self.player
        dx = p.pos.x - self.zone_center.x
        dz = p.pos.z - self.zone_center.z
        in_zone = math.sqrt(dx*dx + dz*dz) <= self.zone_radius

        act_w = p.active_weapon
        return {
            'round_state':    self.round_state,
            'round_time':     self.round_time,
            'countdown':      max(0, self._start_timer),
            'player_hp':      p.hp,
            'player_shield':  p.shield,
            'player_score':   self.player_score,
            'player_kills':   p.kills,
            'player_alive':   p.alive,
            'in_zone':        in_zone,
            'zone_radius':    self.zone_radius,
            'bots_alive':     len(self.alive_bots),
            'bots_total':     self.bot_count,
            'notifications':  self.get_notifications(),
            'player_pos':     (p.pos.x, p.pos.z),
            'bots_pos':       [(b.pos.x, b.pos.z) for b in self.alive_bots],
            'match_summary':  self.last_match_summary,
            'weapon_name':    act_w.name,
            'weapon_cat':     act_w.category,
            'weapon_icon':    act_w.spec.get('icon', 'weapon_crimson_blaze'),
            'ammo_in_mag':    act_w.ammo_in_mag,
            'mag_size':       act_w.mag_size,
            'ammo_reserve':   act_w.ammo_reserve,
            'is_reloading':   act_w.is_reloading,
            'reload_progress': act_w.reload_progress(),
            'active_slot':    p.active_slot,
            'weapon_slots':   [w.name for w in p.weapons],
            'current_emote':  p.current_emote,
        }

    # ── Drawing ───────────────────────────────────────────────────────────────

    def draw_world(self, camera):
        from renderer import begin_3d
        begin_3d(camera)

        # Arena
        self.arena.draw()

        # Pickups
        self.pickup_manager.draw()

        # Bots
        for bot in self.bots:
            bot.draw()

        # Player
        self.player.draw()

        # Projectiles
        self.proj_manager.draw()

        # Safe zone boundary
        self._draw_zone()

    def _draw_zone(self):
        from OpenGL.GL import glDisable, glEnable, GL_LIGHTING, glLineWidth
        from renderer import draw_circle_outline_xz
        glDisable(GL_LIGHTING)
        glLineWidth(3.0)
        # Pulsing colour
        import math, time
        pulse = 0.7 + 0.3 * math.sin(time.time() * 3)
        col = (int(50*pulse), int(255*pulse), int(100*pulse))
        draw_circle_outline_xz(
            self.zone_center.x, self.zone_center.z,
            self.zone_radius, 0.05, col
        )
        glLineWidth(2.0)
        glEnable(GL_LIGHTING)
