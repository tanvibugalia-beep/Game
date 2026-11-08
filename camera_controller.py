"""
camera_controller.py — Third-person orbit camera for Nexus Arena.

The camera orbits around the player using yaw (horizontal) and
pitch (vertical) angles driven by mouse movement.
"""
import math
from math3d import Vec3
import settings


class CameraController:
    """
    Maintains eye position + look-at target for the 3-D view.

    yaw   — horizontal rotation (degrees, 0 = camera behind player looking toward +Z)
    pitch — vertical tilt (degrees, + = looking down)
    """

    def __init__(self):
        self.yaw   = 0.0
        self.pitch = 20.0
        self.distance = settings.CAM_DISTANCE
        self.height   = settings.CAM_HEIGHT

        self.eye    = Vec3(0, 5, -10)
        self.target = Vec3(0, 1,   0)

        self._sens = settings.runtime["mouse_sens"]

    # ── Input ────────────────────────────────────────────────────────────────

    def apply_mouse(self, dx, dy):
        """Called with raw pixel delta each frame (mouse locked to window)."""
        sens = settings.runtime["mouse_sens"]
        self.yaw   += dx * sens
        # In pyglet dy > 0 means mouse moved up; pitch + = looking down, so negate dy
        self.pitch  = max(settings.CAM_PITCH_MIN,
                          min(settings.CAM_PITCH_MAX,
                              self.pitch - dy * sens))

    # ── Update ────────────────────────────────────────────────────────────────

    def update(self, player_pos: Vec3, dt: float):
        """
        Recalculate eye position so the camera orbits around
        a point slightly above the player's centre.
        """
        # The pivot is the player's upper body
        pivot = Vec3(player_pos.x,
                     player_pos.y + self.height * 0.4,
                     player_pos.z)

        yaw_r   = math.radians(self.yaw)
        pitch_r = math.radians(self.pitch)

        # Spherical coordinates → Cartesian offset
        cos_p = math.cos(pitch_r)
        offset = Vec3(
            math.sin(yaw_r)  * cos_p * self.distance,
            math.sin(pitch_r)        * self.distance,
            math.cos(yaw_r)  * cos_p * self.distance,
        )

        desired_eye = pivot + offset
        # Smooth follow
        smooth = min(1.0, settings.CAM_SMOOTH * dt)
        self.eye    = self.eye.lerp(desired_eye, smooth)
        self.target = self.target.lerp(pivot, smooth)

    # ── Derived helpers ───────────────────────────────────────────────────────

    @property
    def forward_dir(self) -> Vec3:
        """Horizontal forward direction based on yaw (used for player movement)."""
        r = math.radians(self.yaw)
        return Vec3(-math.sin(r), 0, -math.cos(r)).normalized()

    @property
    def right_dir(self) -> Vec3:
        """Horizontal right direction."""
        r = math.radians(self.yaw)
        return Vec3(math.cos(r), 0, -math.sin(r)).normalized()
