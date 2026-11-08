"""
math3d.py — Lightweight 3-D vector / matrix math used throughout Nexus Arena.
No external dependencies; pure Python for portability.
"""
import math

class Vec3:
    """Simple 3-component vector."""
    __slots__ = ('x', 'y', 'z')

    def __init__(self, x=0.0, y=0.0, z=0.0):
        self.x = float(x)
        self.y = float(y)
        self.z = float(z)

    # ── Arithmetic ──────────────────────────────────────────────────────────
    def __add__(self, o):  return Vec3(self.x+o.x, self.y+o.y, self.z+o.z)
    def __sub__(self, o):  return Vec3(self.x-o.x, self.y-o.y, self.z-o.z)
    def __mul__(self, s):  return Vec3(self.x*s,   self.y*s,   self.z*s)
    def __rmul__(self, s): return self.__mul__(s)
    def __truediv__(self, s): return Vec3(self.x/s, self.y/s, self.z/s)
    def __neg__(self):     return Vec3(-self.x, -self.y, -self.z)
    def __repr__(self):    return f"Vec3({self.x:.2f},{self.y:.2f},{self.z:.2f})"

    def copy(self):        return Vec3(self.x, self.y, self.z)

    # ── Vector ops ──────────────────────────────────────────────────────────
    def length_sq(self):
        return self.x*self.x + self.y*self.y + self.z*self.z

    def length(self):
        return math.sqrt(self.length_sq())

    def normalized(self):
        l = self.length()
        if l < 1e-9:
            return Vec3(0, 0, 0)
        return self / l

    def dot(self, o):
        return self.x*o.x + self.y*o.y + self.z*o.z

    def cross(self, o):
        return Vec3(
            self.y*o.z - self.z*o.y,
            self.z*o.x - self.x*o.z,
            self.x*o.y - self.y*o.x
        )

    def lerp(self, o, t):
        return self + (o - self) * t

    def xz_length(self):
        """Horizontal distance (ignore Y)."""
        return math.sqrt(self.x*self.x + self.z*self.z)

    def to_tuple(self):
        return (self.x, self.y, self.z)


# ── Matrix helpers (column-major, compatible with OpenGL) ─────────────────────

def mat4_identity():
    """Return a 16-element list representing the 4×4 identity matrix."""
    return [
        1,0,0,0,
        0,1,0,0,
        0,0,1,0,
        0,0,0,1,
    ]

def mat4_translate(x, y, z):
    m = mat4_identity()
    m[12]=x; m[13]=y; m[14]=z
    return m

def mat4_scale(x, y, z):
    m = mat4_identity()
    m[0]=x; m[5]=y; m[10]=z
    return m

def mat4_rotate_y(deg):
    r = math.radians(deg)
    c, s = math.cos(r), math.sin(r)
    m = mat4_identity()
    m[0]=c;  m[2]=s
    m[8]=-s; m[10]=c
    return m

def mat4_rotate_x(deg):
    r = math.radians(deg)
    c, s = math.cos(r), math.sin(r)
    m = mat4_identity()
    m[5]=c;  m[6]=-s
    m[9]=s;  m[10]=c
    return m

def mat4_mul(a, b):
    """Multiply two 4×4 matrices stored as 16-element lists (column-major)."""
    r = [0.0]*16
    for row in range(4):
        for col in range(4):
            r[col*4+row] = sum(a[k*4+row]*b[col*4+k] for k in range(4))
    return r

def mat4_perspective(fov_deg, aspect, near, far):
    f = 1.0 / math.tan(math.radians(fov_deg) / 2.0)
    nf = 1.0 / (near - far)
    return [
        f/aspect, 0,  0,                  0,
        0,        f,  0,                  0,
        0,        0,  (far+near)*nf,     -1,
        0,        0,  2*far*near*nf,      0,
    ]

def mat4_look_at(eye, center, up):
    """Standard lookAt — eye, center, up are Vec3."""
    f = (center - eye).normalized()
    s = f.cross(up).normalized()
    u = s.cross(f)
    return [
         s.x,  u.x, -f.x, 0,
         s.y,  u.y, -f.y, 0,
         s.z,  u.z, -f.z, 0,
        -s.dot(eye), -u.dot(eye), f.dot(eye), 1,
    ]
