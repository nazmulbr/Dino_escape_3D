from OpenGL.GL import *
from OpenGL.GLU import *
from OpenGL.GLUT import *
import math
import random


# Dino position
dino_x, dino_y, dino_z = 0, 0, 0

dino_angle = 0
camera_x, camera_y, camera_z = 0, 100, 200
gem_count = 0
enemy_hit_count = 0
dino_speed = 1.0
dino_speed = 1.0 + 0.1 * gem_count
game_state = "running"
portal_x, portal_y, portal_z = 1000, 0, 0
hit_count = 0
MAX_HITS = 5

move_step = 2
speed_multiplier = 1.0
dino_facing_left = False

# Jumping variables
is_jumping = False
jump_velocity = 0
gravity = -0.25
jump_start_velocity = 6.5
max_fall_speed = -0.1

# asteroids
asteroids = [
    {'x': random.randint(-200, 100), 'y': 200, 'z': 0,
     'active': True, 'speed': random.uniform(0.02, 0.05)},
    {'x': random.randint(-200, 100), 'y': 200, 'z': 0,
     'active': True, 'speed': random.uniform(0.02, 0.05)}
]
asteroid_speed = 0.03
last_speed_update_gem_count = 0

rock_positions = []

# Dinodeath
dino_hit_count = 0
dino_alive = True
dino_shake_offset = 0
shake_direction = 1
dino_color = [0.0, 0.8, 0.2]

# Gem
gems_collected = 0
gem_positions = [(random.randint(-100, 100), -80)]
gem_spawn_z = -80

# enimes
enemies = [{'x': x, 'z': z, 'direction': 1}
           for x, z in [(-120, -60), (-60, -100), (60, -80), (120, -120)]]
enemy_speed = 0.05
enemy_range = 40
pits = [(x, z) for x, z in [(-90, -70), (-30, -110), (30, -90), (90, -100)]]


def update_camera():
    global camera_x, camera_y, camera_z
    camera_x = dino_x + 100 * math.sin(math.radians(dino_y))
    camera_y = dino_y + 50
    camera_z = dino_z + 100 * math.cos(math.radians(dino_y))


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


def generate_rocks():
    rocks = []
    for i in range(random.randint(7, 9)):
        x = random.randint(-180, 180)
        z = random.randint(-180, 180)
        rocks.append((x, z))
    return rocks


def draw_rocks():
    glColor3f(0.4, 0.4, 0.4)
    for x, z in rock_positions:
        glPushMatrix()
        glTranslatef(x, 2, z)
        glScalef(6, 4, 6)
        glutSolidCube(1)
        glPopMatrix()


def draw_text(x, y, text, font=GLUT_BITMAP_HELVETICA_18):
    glMatrixMode(GL_PROJECTION)
    glPushMatrix()
    glLoadIdentity()
    gluOrtho2D(0, 1000, 0, 800)
    glMatrixMode(GL_MODELVIEW)
    glPushMatrix()
    glLoadIdentity()
    glColor3f(1, 1, 1)
    glRasterPos2f(x, y)
    for ch in text:
        glutBitmapCharacter(font, ord(ch))
    glPopMatrix()
    glMatrixMode(GL_PROJECTION)
    glPopMatrix()
    glMatrixMode(GL_MODELVIEW)


def draw_dino(x, y, z):
    glPushMatrix()
    shake = dino_shake_offset if not dino_alive else 0
    glTranslatef(x + shake, y + 5, z)

    if dino_facing_left:
        glRotatef(180, 0, 1, 0)
    glColor3f(*dino_color)

    block = 3
    # Head
    for py in range(3, 5):
        for px in range(0, 3):
            glPushMatrix()
            glTranslatef(px * block, py * block, 0)
            glutSolidCube(block)
            glPopMatrix()
    # Body
    body = [(0, 2), (0, 1), (0, 0), (-1, 0), (-2, 0), (-2, 1), (-2, 2)]
    for px, py in body:
        glPushMatrix()
        glTranslatef(px*block, py*block, 0)
        glutSolidCube(block)
        glPopMatrix()
    # Arms
    glPushMatrix()
    glTranslatef(-1*block, 1*block, 0)
    glutSolidCube(block)
    glPopMatrix()
    # Legs
    for px, py in [(-1, -1), (-2, -1)]:
        glPushMatrix()
        glTranslatef(px*block, py*block, 0)
        glutSolidCube(block)
        glPopMatrix()
    # Tail
    for px, py in [(-3, 1), (-4, 2), (-5, 3)]:
        glPushMatrix()
        glTranslatef(px*block, py*block, 0)
        glutSolidCube(block)
        glPopMatrix()
    glPopMatrix()


def draw_ground():
    glPushMatrix()
    glColor3f(0., 0.29, 0.0)
    glTranslatef(0, -1.5, 0)
    glScalef(1000, 1, 1000)
    glutSolidCube(1)
    glPopMatrix(),


def draw_rocks():
    glColor3f(0.4, 0.4, 0.4)

    for x, z in rock_positions:
        glPushMatrix()

        glTranslatef(x, 2, z)

        glPushMatrix()
        glScalef(6, 2, 6)
        glutSolidCube(1)
        glPopMatrix()

        glPushMatrix()
        glTranslatef(0, 3, 0)
        glScalef(2, 2, 2)
        glutSolidSphere(1, 20, 20)
        glPopMatrix()

        glPushMatrix()
        glTranslatef(3, 1, 0)
        glRotatef(90, 1, 0, 0)
        glScalef(0.5, 2, 0.5)
        glutSolidCylinder(0.5, 2, 20, 20)
        glPopMatrix()

        glPopMatrix()


def draw_trees_and_bushes():
    tree_positions = [(-150, -70), (-100, -80), (-50, -90), (0, -100), (50, -85),
                      (100, -75), (200, -95), (-190, -60), (-30, -70), (30, -65), (80, -90), (130, -80)]

    quadric = gluNewQuadric()

    # trees
    for x, z in tree_positions:
        glPushMatrix()
        glTranslatef(x, 40, z)

        # Treetrunk
        glColor3f(0.4, 0.26, 0.13)
        glPushMatrix()
        glTranslatef(0, 5, 0)
        glRotatef(-90, 1, 0, 0)
        gluCylinder(quadric, 2, 2, 10, 10, 10)
        glPopMatrix()

        glColor3f(0.0, 0.5, 0.0)
        glTranslatef(0, 15, 0)
        glutSolidSphere(6, 16, 16)
        glPopMatrix()


def draw_gems():
    glColor3f(0.2, 0.9, 1.0)
    quadric = gluNewQuadric()
    for gx, gz in gem_positions:
        glPushMatrix()
        glTranslatef(gx, 3, gz)
        glPushMatrix()
        glTranslatef(0, 1.5, 0)
        glRotatef(-90, 1, 0, 0)
        gluCylinder(quadric, 3.0, 0.0, 3.0, 16, 1)
        glPopMatrix()
        glPushMatrix()
        glTranslatef(0, 1.5, 0)
        glRotatef(90, 1, 0, 0)
        gluCylinder(quadric, 3.0, 0.0, 3.0, 16, 1)
        glPopMatrix()
        glPopMatrix()


def draw_asteroid(x, y, z):
    glPushMatrix()
    glTranslatef(x, y, z)
    glColor3f(0.5, 0.5, 0.5)
    glutSolidSphere(6, 18, 18)
    quadric = gluNewQuadric()

    for i in range(5):
        glPushMatrix()
        glTranslatef(random.uniform(-4, 4),
                     random.uniform(-4, 4), random.uniform(-4, 4))
        glRotatef(random.randint(0, 360), 1, 1, 1)
        glScalef(random.uniform(0.5, 1.5), random.uniform(
            0.2, 0.8), random.uniform(0.5, 1.2))
        glColor3f(0.3 + random.uniform(0, 0.2), 0.3, 0.3)
        glutSolidCube(4)
        glPopMatrix()

    for i in range(4):
        glPushMatrix()
        glTranslatef(random.uniform(-3, 3),
                     random.uniform(-3, 3), random.uniform(-3, 3))
        glRotatef(random.uniform(0, 360), 1, 0, 0)
        glRotatef(random.uniform(0, 360), 0, 1, 0)
        glColor3f(0.2, 0.2, 0.2)
        gluCylinder(quadric, 0.5, 0.0, 5.0, 10, 2)
        glPopMatrix()
    glPopMatrix()


def draw_enemies():
    glColor3f(1.0, 0.0, 0.0)
    for enemy in enemies:
        glPushMatrix()
        glTranslatef(enemy['x'], 3, enemy['z'])
        glScalef(6, 6, 6)
        glutSolidCube(1)
        glPopMatrix()


def update_enemies():
    for enemy in enemies:
        enemy['x'] += enemy_speed * enemy['direction']
        if abs(enemy['x']) > 150:
            enemy['direction'] *= -1


spikes = [(-140, -90), (0, -120), (70, -130)]


def draw_spikes():
    glColor3f(0.6, 0.2, 0.2)
    for x, z in spikes:
        glPushMatrix()
        glTranslatef(x, 1, z)
        glRotatef(-90, 1, 0, 0)
        glutSolidCone(4, 8, 20, 4)
        glPopMatrix()


lasers = [{'x': x, 'z': z, 'dir': 1} for x, z in [(-100, -100), (50, -110)]]


def update_lasers():
    for l in lasers:
        l['x'] += 1.2 * l['dir']
        if abs(l['x']) > 160:
            l['dir'] *= -1


def draw_lasers():
    glColor3f(1.0, 0.0, 0.0)
    for l in lasers:
        glPushMatrix()
        glTranslatef(l['x'], 2, l['z'])
        glScalef(20, 0.5, 0.5)
        glutSolidCube(1)
        glPopMatrix()


def check_enemy_collision():
    global dino_hit_count, dino_alive
    for enemy in enemies:
        dist = math.sqrt((dino_x - enemy['x'])**2 + (dino_z - enemy['z'])**2)
        if dist < 10:
            dino_hit_count += 1
            if dino_hit_count >= 5:
                dino_alive = False
            return


def draw_pits():
    glColor3f(0.2, 0.2, 0.2)
    for x, z in pits:
        glPushMatrix()
        glTranslatef(x, -1.5, z)
        glScalef(10, 0.2, 10)
        glutSolidCube(1)
        glPopMatrix()


def check_collision():
    global dino_hit_count, dino_alive, speed_multiplier, dino_color

    # Enemy collision
    for e in enemies:
        if math.dist((dino_x, dino_z), (e['x'], e['z'])) < 10:
            dino_hit_count += 1
            if dino_hit_count >= 5:
                dino_alive = False

    # Pit collision
    for x, z in pits:
        if math.dist((dino_x, dino_z), (x, z)) < 10 and not is_jumping:
            speed_multiplier = max(1.0, speed_multiplier - 0.1)

    # Spike trap collision
    for x, z in spikes:
        if math.dist((dino_x, dino_z), (x, z)) < 8 and not is_jumping:
            dino_hit_count += 0.5
            dino_color[0] = 1.0  # Flash red for feedback

    # Laser collision
    for l in lasers:
        if abs(l['x'] - dino_x) < 10 and abs(l['z'] - dino_z) < 10:
            speed_multiplier = max(1.0, speed_multiplier - 0.2)


def check_gem_collision():
    global gem_positions, gems_collected, move_step, speed_multiplier, asteroid_speed, last_speed_update_gem_count
    new_positions = []
    for gx, gz in gem_positions:
        dist = math.sqrt((dino_x - gx)**2 + (dino_z - gz)**2)
        if dist < 10:
            gems_collected += 1
            speed_multiplier += 0.25
            move_step = int(3 * speed_multiplier)
            new_x = random.randint(-100, 100)
            new_positions.append((new_x, gem_spawn_z))
        else:
            new_positions.append((gx, gz))
    gem_positions[:] = new_positions

    if gems_collected // 2 > last_speed_update_gem_count // 2:
        print("Speed increased!")
        asteroid_speed += 1
        last_speed_update_gem_count = gems_collected


def idle():
    global dino_y, jump_velocity, is_jumping, dino_hit_count, gems_collected, dino_alive, dino_shake_offset, shake_direction, dino_color, game_state

    if is_jumping:
        dino_y += jump_velocity
        jump_velocity += gravity
        if jump_velocity < max_fall_speed:
            jump_velocity = max_fall_speed
        if dino_y <= 0:
            dino_y = 0
            jump_velocity = 0
            is_jumping = False

    if dino_alive:
        for asteroid in asteroids:
            asteroid['y'] -= asteroid['speed']
            if asteroid['y'] <= 0:
                asteroid['x'] = random.randint(-100, 100)
                asteroid['y'] = 200
                asteroid['z'] = dino_z
            if abs(asteroid['x'] - dino_x) < 10 and abs(asteroid['y'] - (dino_y + 5)) < 10 and abs(asteroid['z'] - dino_z) < 10:
                if gems_collected == 0:
                    dino_alive = False
                else:
                    dino_hit_count += 1
                    gems_collected = max(0, gems_collected - 0.25)
                    if dino_hit_count >= 3:
                        dino_alive = False
                    asteroid['x'] = random.randint(-100, 100)
                    asteroid['y'] = 200
                    asteroid['z'] = dino_z
    else:
        dino_shake_offset += shake_direction * 1
        if abs(dino_shake_offset) > 5:
            shake_direction *= -1
        dino_color = [random.random() for _ in range(3)]

    if game_state == "running":
        if math.dist([dino_x, dino_y, dino_z], [portal_x, portal_y, portal_z]) < 20:
            game_state = "win"

    # Lose condition
    if hit_count >= MAX_HITS:
        game_state = "lose"
    glutPostRedisplay()


def restart_game():
    global dino_x, dino_y, dino_z, move_step, speed_multiplier, dino_facing_left, is_jumping, jump_velocity, dino_hit_count
    global dino_alive, dino_shake_offset, shake_direction, dino_color, gems_collected, gem_positions, asteroids, asteroid_speed, last_speed_update_gem_count, rock_positions

    dino_x, dino_y, dino_z = 0, 0, 0
    move_step = 2
    speed_multiplier = 1.0
    dino_facing_left = False
    is_jumping = False
    jump_velocity = 0
    dino_hit_count = 0
    dino_alive = True
    dino_shake_offset = 0
    shake_direction = 1
    dino_color = [0.0, 0.8, 0.2]
    gems_collected = 0
    gem_positions = [(random.randint(-100, 100), -80)]
    asteroids = [
        {'x': random.randint(-200, 100), 'y': 200, 'z': 0,
         'active': True, 'speed': random.uniform(0.02, 0.05)},
        {'x': random.randint(-200, 100), 'y': 200, 'z': 0,
         'active': True, 'speed': random.uniform(0.02, 0.05)}
    ]
    rock_positions = generate_rocks()

    glutIdleFunc(idle)
    glutPostRedisplay()


def showScreen():
    glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)
    glLoadIdentity()
    gluLookAt(0, 100, 300, 0, 0, 0, 0, 1, 0)
    global rock_positions, game_state

    draw_ground()
    draw_trees_and_bushes()
    draw_gems()
    draw_rocks()

    draw_pits()
    draw_enemies()
    update_enemies()
    check_enemy_collision()
    update_lasers()
    draw_lasers()
    check_collision()
    draw_spikes()

    draw_end_portal()
    draw_game_result()

    if not rock_positions:
        rock_positions = generate_rocks()

    for asteroid in asteroids:
        if asteroid['active'] and dino_alive:
            draw_asteroid(asteroid['x'], asteroid['y'], asteroid['z'])
    draw_dino(dino_x, dino_y, dino_z)
    draw_text(10, 760, f"Game Score: {gems_collected}")
    if gems_collected > 0 and dino_alive:
        draw_text(10, 730, f"Hits Left: {max(0, 3 - dino_hit_count)}")
    if not dino_alive:
        draw_text(10, 730, "DINO DIED!", GLUT_BITMAP_HELVETICA_18)
    glutSwapBuffers()


def keyboardListener(key, x, y):
    global dino_x, dino_z, is_jumping, jump_velocity, dino_facing_left
    if key == b'r':
        restart_game()
        return
    if not dino_alive:
        return
    min_x, max_x = -165, 170
    min_z, max_z = -165, 170
    if key == b'a':
        dino_x -= move_step
        dino_facing_left = True
    elif key == b'd':
        dino_x += move_step
        dino_facing_left = False
    elif key == b'w':
        dino_z -= move_step
    elif key == b's':
        dino_z += move_step
    elif key == b' ' and not is_jumping:
        is_jumping = True
        jump_velocity = jump_start_velocity
        glutIdleFunc(idle)

    dino_x = max(min_x, min(max_x, dino_x))
    dino_z = max(min_z, min(max_z, dino_z))
    check_gem_collision()
    glutPostRedisplay()


def init():
    glClearColor(0.5, 0.8, 1.0, 1.0)
    glEnable(GL_DEPTH_TEST)
    glMatrixMode(GL_PROJECTION)
    glLoadIdentity()
    gluPerspective(60, 1, 1, 1000)
    glMatrixMode(GL_MODELVIEW)


def main():
    glutInit()
    glutInitDisplayMode(GLUT_DOUBLE | GLUT_RGB | GLUT_DEPTH)
    glutInitWindowSize(1000, 800)
    glutInitWindowPosition(0, 0)
    glutCreateWindow(b"Dino Escape")
    init()
    glutDisplayFunc(showScreen)
    glutKeyboardFunc(keyboardListener)
    glutIdleFunc(idle)
    glutMainLoop()


if __name__ == "__main__":
    main()
