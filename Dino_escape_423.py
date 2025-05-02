from OpenGL.GL import *
from OpenGL.GLU import *
from OpenGL.GLUT import *
import math
import random


# Dino Position and Orientation
dino_x, dino_y, dino_z = 0, 0, 0
dino_angle = 0
camera_pos = [0, 60, -100]
gem_count = 0
enemy_hit_count = 0
dino_speed = 1.0
dino_speed = 1.0 + 0.1 * gem_count
game_state = "running"
portal_x, portal_y, portal_z = 1000, 0, 0
hit_count = 0
MAX_HITS = 5


# Third-person camera positioning
def update_camera():
    camera_distance = 100
    camera_height = 60
    smooth_factor = 0.1

    dino_pos = [dino_x, dino_y, dino_z]
    dino_facing = [math.sin(dino_angle), 0, math.cos(dino_angle)]

    desired_cam_x = dino_pos[0] - dino_facing[0] * camera_distance
    desired_cam_y = dino_pos[1] + camera_height
    desired_cam_z = dino_pos[2] - dino_facing[2] * camera_distance

    camera_pos[0] += (desired_cam_x - camera_pos[0]) * smooth_factor
    camera_pos[1] += (desired_cam_y - camera_pos[1]) * smooth_factor
    camera_pos[2] += (desired_cam_z - camera_pos[2]) * smooth_factor

    gluLookAt(camera_pos[0], camera_pos[1], camera_pos[2],
              dino_pos[0], dino_pos[1], dino_pos[2],
              0, 1, 0)


def draw_ui():
    glDisable(GL_LIGHTING)
    glMatrixMode(GL_PROJECTION)
    glPushMatrix()
    glLoadIdentity()
    gluOrtho2D(0, 1000, 0, 800)
    glMatrixMode(GL_MODELVIEW)
    glPushMatrix()
    glLoadIdentity()

    glColor3f(1, 1, 1)

    def draw_text(x, y, text):
        glRasterPos2f(x, y)
        for ch in text:
            glutBitmapCharacter(GLUT_BITMAP_HELVETICA_18, ord(ch))

    draw_text(20, 770, f"Gems: {gem_count}")
    draw_text(20, 740, f"Enemy Hits: {enemy_hit_count}")
    draw_text(20, 710, f"Speed: {round(dino_speed, 2)}")

    glPopMatrix()
    glMatrixMode(GL_PROJECTION)
    glPopMatrix()
    glMatrixMode(GL_MODELVIEW)
    glEnable(GL_LIGHTING)


# End Portal (a glowing ring)
def draw_end_portal():
    glPushMatrix()
    glTranslatef(portal_x, portal_y, portal_z)
    glColor3f(0.5, 0.8, 1.0)
    glutSolidTorus(3, 15, 20, 50)
    glPopMatrix()


# Win condition
if math.dist([dino_x, dino_y, dino_z], [portal_x, portal_y, portal_z]) < 20:
    game_state = "win"

# Lose condition
if hit_count >= 5:
    game_state = "lose"


def draw_game_result():
    if game_state not in ["win", "lose"]:
        return

    glDisable(GL_LIGHTING)
    glMatrixMode(GL_PROJECTION)
    glPushMatrix()
    glLoadIdentity()
    gluOrtho2D(0, 1000, 0, 800)
    glMatrixMode(GL_MODELVIEW)
    glPushMatrix()
    glLoadIdentity()

    glColor3f(1, 0, 0) if game_state == "lose" else glColor3f(0, 1, 0)
    text = "GAME OVER" if game_state == "lose" else "YOU WIN"

    def draw_centered_text(x, y, text):
        glRasterPos2f(x, y)
        for ch in text:
            glutBitmapCharacter(GLUT_BITMAP_TIMES_ROMAN_24, ord(ch))

    draw_centered_text(450, 400, text)

    glPopMatrix()
    glMatrixMode(GL_PROJECTION)
    glPopMatrix()
    glMatrixMode(GL_MODELVIEW)
    glEnable(GL_LIGHTING)


# add this to the update loop
if game_state == "running":
    # Win condition
    if math.dist([dino_x, dino_y, dino_z], [portal_x, portal_y, portal_z]) < 20:
        game_state = "win"

    # Lose condition
    if hit_count >= MAX_HITS:
        game_state = "lose"

# call this in the render loop
draw_end_portal()
draw_game_result()
