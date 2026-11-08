"""
renderer.py — Immediate-mode OpenGL helpers for Nexus Arena.

Uses pyglet's context + classic OpenGL (fixed-function pipeline)
for simplicity on Python 3.15 where Panda3D/Ursina wheels don't exist yet.
All drawing goes through a small set of helper functions.
"""
import math
from OpenGL.GL import *
from OpenGL.GLU import *
from math3d import Vec3


# ── Colour helpers ────────────────────────────────────────────────────────────

def set_color(rgb, alpha=1.0):
    """Accept (r,g,b) as 0-255 ints."""
    glColor4f(rgb[0]/255, rgb[1]/255, rgb[2]/255, alpha)

def set_color_f(r, g, b, a=1.0):
    glColor4f(r, g, b, a)


# ── Primitive drawing ─────────────────────────────────────────────────────────

def draw_box(x, y, z, w, h, d, color, alpha=1.0):
    """Draw an axis-aligned solid box centred at (x,y,z)."""
    hw, hh, hd = w/2, h/2, d/2
    set_color(color, alpha)
    glPushMatrix()
    glTranslatef(x, y, z)

    glBegin(GL_QUADS)
    # Front
    glNormal3f(0,0,1)
    glVertex3f(-hw,-hh, hd); glVertex3f( hw,-hh, hd)
    glVertex3f( hw, hh, hd); glVertex3f(-hw, hh, hd)
    # Back
    glNormal3f(0,0,-1)
    glVertex3f( hw,-hh,-hd); glVertex3f(-hw,-hh,-hd)
    glVertex3f(-hw, hh,-hd); glVertex3f( hw, hh,-hd)
    # Left
    glNormal3f(-1,0,0)
    glVertex3f(-hw,-hh,-hd); glVertex3f(-hw,-hh, hd)
    glVertex3f(-hw, hh, hd); glVertex3f(-hw, hh,-hd)
    # Right
    glNormal3f(1,0,0)
    glVertex3f( hw,-hh, hd); glVertex3f( hw,-hh,-hd)
    glVertex3f( hw, hh,-hd); glVertex3f( hw, hh, hd)
    # Top
    glNormal3f(0,1,0)
    glVertex3f(-hw, hh, hd); glVertex3f( hw, hh, hd)
    glVertex3f( hw, hh,-hd); glVertex3f(-hw, hh,-hd)
    # Bottom
    glNormal3f(0,-1,0)
    glVertex3f(-hw,-hh,-hd); glVertex3f( hw,-hh,-hd)
    glVertex3f( hw,-hh, hd); glVertex3f(-hw,-hh, hd)
    glEnd()

    glPopMatrix()


def draw_sphere(x, y, z, radius, color, slices=10, stacks=8):
    """Draw a solid sphere using GLU."""
    set_color(color)
    glPushMatrix()
    glTranslatef(x, y, z)
    q = gluNewQuadric()
    gluSphere(q, radius, slices, stacks)
    gluDeleteQuadric(q)
    glPopMatrix()


def draw_cylinder(x, y, z, radius, height, color, slices=8):
    """Draw a vertical cylinder (bottom face at y, top at y+height)."""
    set_color(color)
    glPushMatrix()
    glTranslatef(x, y, z)
    glRotatef(-90, 1, 0, 0)   # rotate so Z-axis cylinder points up
    q = gluNewQuadric()
    gluCylinder(q, radius, radius, height, slices, 1)
    # caps
    gluDisk(q, 0, radius, slices, 1)
    glTranslatef(0, 0, height)
    gluDisk(q, 0, radius, slices, 1)
    gluDeleteQuadric(q)
    glPopMatrix()


def draw_cone(x, y, z, radius, height, color, slices=8):
    """Cone with base at y, tip at y+height."""
    set_color(color)
    glPushMatrix()
    glTranslatef(x, y, z)
    glRotatef(-90, 1, 0, 0)
    q = gluNewQuadric()
    gluCylinder(q, radius, 0, height, slices, 1)
    gluDisk(q, 0, radius, slices, 1)
    gluDeleteQuadric(q)
    glPopMatrix()


def draw_flat_quad(x1, z1, x2, z2, y, color, alpha=1.0):
    """Draw a horizontal quad (ground patch)."""
    set_color(color, alpha)
    glBegin(GL_QUADS)
    glNormal3f(0, 1, 0)
    glVertex3f(x1, y, z1)
    glVertex3f(x2, y, z1)
    glVertex3f(x2, y, z2)
    glVertex3f(x1, y, z2)
    glEnd()


def draw_circle_outline_xz(cx, cz, radius, y, color, segments=60, alpha=1.0):
    """Draw a horizontal circle outline (safe-zone ring)."""
    set_color(color, alpha)
    glBegin(GL_LINE_LOOP)
    for i in range(segments):
        a = 2*math.pi * i / segments
        glVertex3f(cx + math.cos(a)*radius, y, cz + math.sin(a)*radius)
    glEnd()


def draw_rect_outline_xz(cx, cz, half, y, color, alpha=1.0):
    """Draw a square outline for zone boundary."""
    set_color(color, alpha)
    glBegin(GL_LINE_LOOP)
    glVertex3f(cx-half, y, cz-half)
    glVertex3f(cx+half, y, cz-half)
    glVertex3f(cx+half, y, cz+half)
    glVertex3f(cx-half, y, cz+half)
    glEnd()


# ── Lighting setup ────────────────────────────────────────────────────────────

def setup_lighting():
    """Set up basic directional lighting for a daytime feel."""
    glEnable(GL_LIGHTING)
    glEnable(GL_LIGHT0)
    glEnable(GL_COLOR_MATERIAL)
    glColorMaterial(GL_FRONT_AND_BACK, GL_AMBIENT_AND_DIFFUSE)

    # Ambient light (soft fill)
    glLightModelfv(GL_LIGHT_MODEL_AMBIENT, [0.30, 0.30, 0.35, 1.0])

    # Directional sun (w=0.0 → directional, not positional)
    glLightfv(GL_LIGHT0, GL_POSITION, [-0.5, 1.0, -0.3, 0.0])
    glLightfv(GL_LIGHT0, GL_DIFFUSE,  [1.0, 0.95, 0.85, 1.0])
    glLightfv(GL_LIGHT0, GL_SPECULAR, [0.4,  0.4,  0.4,  1.0])


def setup_gl(width, height):
    """One-time OpenGL state setup."""
    glClearColor(0.39, 0.63, 0.90, 1.0)   # sky blue
    glEnable(GL_DEPTH_TEST)
    glDepthFunc(GL_LEQUAL)
    glEnable(GL_BLEND)
    glBlendFunc(GL_SRC_ALPHA, GL_ONE_MINUS_SRC_ALPHA)
    glShadeModel(GL_SMOOTH)
    # GL_PERSPECTIVE_CORRECTION_HINT was removed in OpenGL 3.0; not needed.
    setup_lighting()
    glLineWidth(2.0)
    set_viewport(width, height)


def set_viewport(width, height):
    glViewport(0, 0, width, height)
    glMatrixMode(GL_PROJECTION)
    glLoadIdentity()
    gluPerspective(60.0, width / max(height, 1), 0.1, 500.0)
    glMatrixMode(GL_MODELVIEW)


def begin_3d(camera):
    """Load camera view matrix."""
    glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)
    glMatrixMode(GL_MODELVIEW)
    glLoadIdentity()
    eye = camera.eye
    tgt = camera.target
    gluLookAt(eye.x, eye.y, eye.z,
              tgt.x, tgt.y, tgt.z,
              0, 1, 0)


def begin_2d(width, height):
    """Switch to 2-D orthographic projection for the HUD."""
    glDisable(GL_LIGHTING)
    glDisable(GL_DEPTH_TEST)
    glMatrixMode(GL_PROJECTION)
    glPushMatrix()
    glLoadIdentity()
    glOrtho(0, width, 0, height, -1, 1)
    glMatrixMode(GL_MODELVIEW)
    glPushMatrix()
    glLoadIdentity()


def end_2d():
    """Restore 3-D projection."""
    glMatrixMode(GL_PROJECTION)
    glPopMatrix()
    glMatrixMode(GL_MODELVIEW)
    glPopMatrix()
    glEnable(GL_DEPTH_TEST)
    glEnable(GL_LIGHTING)


def draw_rect_2d(x, y, w, h, color, alpha=1.0):
    """Draw a 2-D filled rectangle (y measured from bottom)."""
    set_color(color, alpha)
    glBegin(GL_QUADS)
    glVertex2f(x,   y)
    glVertex2f(x+w, y)
    glVertex2f(x+w, y+h)
    glVertex2f(x,   y+h)
    glEnd()


def draw_rect_outline_2d(x, y, w, h, color, alpha=1.0):
    set_color(color, alpha)
    glBegin(GL_LINE_LOOP)
    glVertex2f(x,   y)
    glVertex2f(x+w, y)
    glVertex2f(x+w, y+h)
    glVertex2f(x,   y+h)
    glEnd()
