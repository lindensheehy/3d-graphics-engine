import pygame as pg
import numpy as np
import math, time, json, random

# These classes are used to create variables with attributes. For example coordinates or angles
class vec2d:
    def __init__(self, x, y):
        self.x = x
        self.y = y

    def to_tuple(self):
        return (self.x, self.y)

    def scale(self, factor):
        self.x *= factor
        self.y *= factor

class vec3d:
    def __init__(self, x, y, z):
        self.x = x
        self.y = y
        self.z = z

    def to_tuple(self):
        return (self.x, self.y, self.z)

    def scale(self, factor):
        self.x *= factor
        self.y *= factor
        self.z *= factor

class new_point:
    def __init__(self, pos: vec3d):
        self.pos = pos
        self.hovered = False
        global_.points.append(self)

class rect_prism:
    def __init__(self, pos: tuple, size: tuple):
        '''
        pos and size are both tuples wtih length 3
        '''
        self.posx = pos[0]
        self.posy = pos[1]
        self.posz = pos[2]
        self.sizex = size[0]
        self.sizey = size[1]
        self.sizez = size[2]

class object:

    instances = []

    def __init__(self, pos: tuple, mass: float):
        self.mass = mass
        self.x = pos[0]
        self.y = pos[1]
        self.y = pos[2]
        self.velocity = vec3d(0, 0, 0)
        self.acceleration = vec3d(0, 0, 0)

    def do_frame():
        for obj in instances:
            obj.x += obj.velocity.x * dt
            obj.y += obj.velocity.y * dt
            obj.z += obj.velocity.z * dt

            obj.velocity.x += obj.acceleration.x * dt
            obj.velocity.y += obj.acceleration.y * dt
            obj.velocity.z += obj.acceleration.z * dt

            obj.velocity.y += gravity * dt

class tri:
    pass

class mesh:
    pass

# Classes containing variables which need to be avaliable throughout all functions
# Using a classes instead of the global keyword to avoid cluttering the namespace
class global_:
    screen = None   # Surface representing the window open
    dt = None   # Delta time. How much time has passed since the last frame
    points = None   # Array of all points currently being drawn
    print_keys = None   # Bool if keys pressed are printed to console or not
    mouse_pos = None   # Current mouse pos
    dmouse_pos = None   # Change in mouse pos since last frame
    fps = None   # Contains a string of how many fps the display is running at
    font = None   # Pygames font object, used to write text to screen
    gravity = None   # Number representing the gravitational acceleration

class camera:

    movement_speed = 60

    pos = vec3d(0, 0, 0)

    yaw = 0   # Around y axis, on the xz plane
    pitch = 0   # Around x axis, on the yz plane
    roll = 0   # Around z axis, on the yx plane

    fov = vec2d(120, 90)

class display:

    width = 1500
    height = 750

    class bounds:
        left = 360 - (camera.fov.x / 2)
        right = (camera.fov.x / 2)
        top = 360 - (camera.fov.y / 2)
        bottom = (camera.fov.y / 2)

    '''
    def update_bounds():
        display.bounds.left = angle_rollover(camera.yaw - (camera.fov.x / 2))
        display.bounds.right = angle_rollover(camera.yaw + (camera.fov.x / 2))
        display.bounds.top = angle_rollover(camera.pitch - (camera.fov.y / 2))
        display.bounds.bottom = angle_rollover(camera.pitch + (camera.fov.y / 2))
    '''

class screen_borders:
    '''
    Contains information about how the screen bounds can be represented as eqations for the collision function.
    '''

    class left:
        dx = 0
        dy = 750
        ox = 0
        oy = 0

    class right:
        dx = 0
        dy = 750
        ox = 1500
        oy = 0

    class top:
        dx = 1500
        dy = 0
        ox = 0
        oy = 750

    class bottom:
        dx = 1500
        dy = 0
        ox = 0
        oy = 0

# Math Functions
def angle_rollover(angle: float, max: float = 360) -> float:
    '''
    Changes angles so they are always within 0-360.  
    (-10) -> 350
    (370) -> 10
    '''
    new_angle = angle

    while True:
        if new_angle > max:
            new_angle -= max
        elif new_angle < 0:
            new_angle += max
        else:
            break

    return new_angle

def in_angle(low: float, high: float, val: float) -> float:
    '''
    Takes 3 angles as input ranging from 0-360.
    Returns a decimal between 0 and 1 representing how far towards high the val is. 
    '''
    # Example: low=300, high=60, val=0 returns 0.5
    
    # Adjust degree values by increments of decrements of 360 so math can be done
    if low > high and val > high:
        low -= 360
        val -= 360
    if low > high and val < low:
        high += 360
        val += 360

    # Return
    if val >= low and val <= high:
        return (val - low) / (high - low)
    return None

def in_bounds(p: tuple, bounds: tuple) -> bool:
    '''
    Returns True if the given point lies within the bounding box specified
    Returns False otherwise
    '''
    for i in enumerate(p):
        if i[1] < bounds[i[0]][0] or i[1] > bounds[i[0]][1]:
            return False

    return True

def distance(point1: tuple, point2: tuple = (0, 0)) -> float:   # Returns distance between 2 points. can be passed either tuples or instances of new_point

    # Distance between 2 points with unlimited components.
    if type(point1) is tuple and type(point2) is tuple:
        sum = 0
        for i in range(len(point1)):
            sum += abs(point1[i] - point2[i]) ** 2
        return math.sqrt(sum)

    # Distance between 2 points defined as instances of new_point
    else:
        dx = abs(point1.x - point2.x)
        dy = abs(point1.y - point2.y)
        dz = abs(point1.z - point2.z)
        return math.sqrt((dx * dx) + (dy * dy) + (dz * dz))

def get_angle(point:tuple, angle_from: tuple = (0, 0)) -> float:   # Returns the angle from the Y axis to p2 relative to p1

    p1x, p1y = angle_from
    p2x, p2y = point

    # All cases where the 2 points share a coordinate, in which case the angle will be a multiple of 90
    if p2x == p1x and p2y > p1y:   # Same X, p2 has greater Y
        return 0
    if p2x == p1x and p2y < p1y:   # Same X, p2 has lesser Y
        return 180
    if p2y == p1y and p2x > p1x:   # Same Y, p2 has greater X
        return 90
    if p2y == p1y and p2x < p1x:   # Same Y, p2 has lesser X
        return 270

    # Get slope between points and use acrtan to derive an angle from m
    try:
        m = abs((p1y - p2y) / (p1x - p2x))
        angle = 90 - math.degrees(math.atan(m))
    except ZeroDivisionError:
        angle = 0

    # Adjust the angle based on the quadrant the point lies in. Range 0-360
    if p2y < p1y:
        angle = 180 - angle
    if p2x < p1x:
        angle = 360 - angle
    
    # If none of the above apply, the angle lies in quadrant 1 meaning there is no adjustment needed.

    return angle

def rotate2d(point: tuple, degrees: float, around: tuple = (0, 0)) -> vec2d:
    '''
    Returns (x, y) of a point rotated some number of degrees about another point. COUNTER CLOCKWISE
    '''

    # Attempt to change tuple inputs to vec2d objects. Throws an error if this fails.
    try:
        if degrees == 0: return vec2d(point[0], point[1])
        p = vec2d(float(point[0]), float(point[1]))
        a = vec2d(float(around[0]), float(around[1]))
    except:
        raise Exception(f"\nrotate2d(point = {point}, degrees = {degrees}, around = {around})\nInvalid Arguments")

    # Relative (x, y) location to the "around point"
    rel = vec2d(p.x - a.x, p.y - a.y)

    # Trig constants
    sin = math.sin(math.radians(degrees))
    cos = math.cos(math.radians(degrees))

    # New components
    p.x = (cos * rel.x) - (sin * rel.y) + a.x
    p.y = (cos * rel.y) + (sin * rel.x) + a.y

    return p

def rotate3d(point: tuple, angle: tuple, around: tuple = (0, 0, 0)) -> vec3d:
    '''
    Returns the (x, y, z) of a point rotated by any yaw and pitch around another point
    '''

    try:
        p = vec3d(float(point[0]), float(point[1]), float(point[2]))
        a = vec3d(float(around[0]), float(around[1]), float(around[2]))
        yaw, pitch = float(angle[0]), float(angle[1])
    except:
        raise Exception(f"\nrotate2d(point = {point}, angle = {angle}, around = {around})\nInvalid Arguments")

    # If yaw is not 0, rotate point about the y axis
    if yaw != 0:
        p.x, p.z = rotate2d((p.x, p.z), yaw, (a.x, a.z)).to_tuple()

    # If pitch is not 0, rotate point about the x axis
    # Because yaw rotation is done first, camera pitch always lines up with rotation around the x axis
    if pitch != 0:
        p.z, p.y = rotate2d((p.z, p.y), pitch, (a.z, a.y)).to_tuple()

    return vec3d(p.x, p.y, p.z)

def collision(dx1, dy1, ox1, oy1, dx2, dy2, ox2, oy2) -> tuple:
    '''
    dx and dy represent the slope of the line
    ox and oy represent a point on the line, the offset from (0, 0)
    Returns a tuple (x, y) of a point where two lines collide
    y = (m1 * x) + b1  and  y = (m2 * x) + b2
    Returns None if lines do not collide
    '''

    # Building First Equation:  y = eq1[0] * (x - eq1[1]) + eq1[2]
    eq1_is_vertical = False
    eq1 = [0, ox1, oy1]

    try:
        m1 = dy1 / dx1
        eq1[0] = m1
    except ZeroDivisionError:
        eq1_is_vertical = True
        eq1 = [ox1]


    # Building Second Equation:  y = eq2[0] * (x - eq2[1]) + eq2[2]
    eq2_is_vertical = False
    eq2 = [0, ox2, oy2]

    try:
        m2 = dy2 / dx2
        eq2 = [m2, ox2, oy2]
    except ZeroDivisionError:
        eq2_is_vertical = True
        eq2 = [ox2]

    # If Both lines are vertical, there is no collision
    if eq1_is_vertical and eq2_is_vertical:
        return None

    # Solve for x by substitution
    if eq1_is_vertical:
        x = eq1[0]   # If equation 1 is vertical, the x must be equal to ox1
    elif eq2_is_vertical:
        x = eq2[0]   # If equation 2 is vertical, the x must be equal to ox2
    else:
        try:
            # This huge equation is just a reformed version of:  m1 * (x - ox1) + oy1 = m2 * (x - ox2) + oy2, where x is isolated
            x = ((eq2[2] + (eq1[0] * eq1[1])) - (eq1[2] + (eq2[0] * eq2[1]))) / (eq1[0] - eq2[0])
        except ZeroDivisionError:
            # The slopes of both lines are equal, meaning no collision
            return None

    # Solve for y based on x using eq1
    try:
        y = eq1[0] * (x - eq1[1]) + eq1[2]
    except IndexError:
        y = eq2[0] * (x - eq2[1]) + eq2[2]

    return (x, y)

def restrict_tri(tri = ((0, 0), (0, 0), (0, 0)), bounds = ((0, 1500), (0, 750))) -> list:
    '''
    Returns a list of tuples of x and y coordinates for the shape of the triangle after being bound
    '''

    # If either all points are inside the bounds or all are outside, return tri
    if in_bounds(tri[0], bounds) and in_bounds(tri[1], bounds) and in_bounds(tri[2], bounds):
        return tri
    if (not in_bounds(tri[0], bounds)) and (not in_bounds(tri[1], bounds)) and (not in_bounds(tri[2], bounds)):
        return tri

    # Variable initiation
    new_points = []

    border = [screen_borders.left, screen_borders.right, screen_borders.top, screen_borders.bottom]

    for i in range(3):

        # Assigning variables so that all sets of verticies (v1, v2), (v2, v3) and (v3, v1) get done
        p1 = tri[i]
        if i != 2:
            p2 = tri[i + 1]
        else:
            p2 = tri[0]

        # Doing some of the math before hand to keep the statements clearer
        dx = p1[0] - p2[0]
        dy = p1[1] - p2[1]
        ox, oy = p1

        point_bounds = ((min(p1[0], p2[0]), max(p1[0], p2[0])), (min(p1[1], p2[1]), max(p1[1], p2[1])))

        # Check if the line between the points collides with any of the borders at a point inside the bounds of the points.
        for i in border:
            p = collision(dx, dy, ox, oy, i.dx, i.dy, i.ox, i.oy)
            try:
                if in_bounds(p, point_bounds):
                    new_points.append(p)
            except TypeError:
                pass
    
    poly = []

    for p in tri:
        if in_bounds(p, bounds):
            poly.append(p)

    poly += new_points

    return poly

def points_to_mesh_2d(points: tuple) -> tuple:
    
    # Create a list of the angle each point makes with the starting point
    start_point = points[0]
    angles = []
    for p in points[1:]:
        angles.append([get_angle(start_point, p), p])
    angles.sort()

    mesh = []

    for i in range(len(angles) - 1):
        p1 = angles[i][1]
        p2 = angles[i + 1][1]

        mesh.append((start_point, p1, p2))

    return mesh

# Setup and every frame update functions
def init_vars():
    '''
    Sets all needed global variables. Called on startup.
    Only made into its own method for tidiness.
    '''

    # Should the key id of key presses be printed to the console
    global_.print_keys = False
    global_.keys_down = []

    # Boolean if user is defining a triangle or not. Changes/disables some controls.
    global_.tri_mode = False

    # Pygame surface of the window
    global_.screen = pg.display.set_mode((display.width, display.height))

    # Set up for pygames fonts to write text to the screen
    pg.font.init()
    global_.font = pg.font.SysFont('arial', 15)

    # Array of all points to be drawn
    global_.points = []
    points = new_cube((100, 0, 100), 20)
    #points = [new_point(vec3d(100, 100, 100))]
    '''
    for i in range(-30, 30):
        i *= 20
        for ii in range(-30, 30):
            ii *= 20
            #global_.points.append(
            new_point(vec3d(i, ii, 200))
    '''

    # Array of all triangles to be drawn
    global_.tris = []

    global_.screen_dots = []

    # Time related variables. Used for both timing and counting frames
    global_.time_one = time.time()

    # Variables for calculating and drawing fps counter
    global_.timer = 0
    global_.frame_count = 0
    global_.fps = global_.font.render("0", False, (255, 255, 255))

    # A global counter that only ever increments every frame. Used to have something happen once or every x frames.
    global_.frame_counter = 0

    # Mouse position variable and 
    global_.mouse_pos = pg.mouse.get_pos()

    # Set the global gravitational acceleration
    # Gravity affects the y velocity of objects
    global_.gravity = -10

    return

def update_dt():   # Gets new dt (delta time) and sets time_one to current time for next call

    global_.dt = time.time() - global_.time_one
    global_.time_one = time.time()
    global_.timer += global_.dt

    return

def update_mouse_pos():   # Updates both mouse_pos and dmouse_pos (delta mouse_pos)

    new_mouse_pos = pg.mouse.get_pos()
    global_.dmouse_pos = (
        global_.mouse_pos[0] - new_mouse_pos[0], 
        global_.mouse_pos[1] - new_mouse_pos[1]
    )
    global_.mouse_pos = new_mouse_pos

    return

def draw_fps():   # Draws the fps counter to the top left of the screen

    global_.font = pg.font.SysFont('arial', 15)

    if global_.timer > 1:
        global_.fps = global_.font.render(str(global_.frame_count), False, (255, 255, 255))
        global_.timer = 0
        global_.frame_count = 0
    else:
        global_.frame_count += 1

    global_.screen.blit(global_.fps, (10, 10))

    return

# All the other stuff
def get_player_input():   # Returns array of keys pressed

    keys_were_down = []
    for i in global_.keys_down:
        keys_were_down.append(i[0])

    # Array to hold all input events as ints
    keys = []

    #   Mouse   #
    # Grabs mouse down events
    mouse_events = pg.mouse.get_pressed()

    # Checks mouse events and adds a negative value to the list. negative values are reserved for mouse actions
    for click in enumerate(mouse_events):
        if click[1]:
            keys.append([click[0] - 3, click[0] in keys_were_down])

    #   Keyboard   #
    # Gets a list of bools for if every key is pressed or not
    all_keys = pg.key.get_pressed()

    # Checks all keys for down, and adds the index of the keydown to the return value for input handling
    for key in enumerate(all_keys):
        if key[1]: 
            keys.append([key[0], key[0] in keys_were_down])
    
    # Optionally prints the keys down, used to get key ids
    if global_.print_keys:
        print(keys)

    # This returns an array of all the keys pressed as their numerical id, returns [] if no keys pressed.
    return keys

def handle_input():   # Do all necessary actions based on played input

    global_.keys_down = get_player_input()

    controls = json.load(open("controls.json", 'r'))

    distance_moved = camera.movement_speed * global_.dt

    for key in global_.keys_down:

        # Movement
        cam_mov_vector = vec2d(0, 0)

        if key[0] == controls["left"]:
            cam_mov_vector.x -= distance_moved
        elif key[0] == controls["right"]:
            cam_mov_vector.x += distance_moved
        elif key[0] == controls["forward"]:
            cam_mov_vector.y += distance_moved
        elif key[0] == controls["backward"]:
            cam_mov_vector.y -= distance_moved
        elif key[0] == controls["up"]:
            camera.pos.y += distance_moved
        elif key[0] == controls["down"]:
            camera.pos.y -= distance_moved

        # Change (x, z) movement vector based on camera yaw rotation so the forward key always goes forwards
        cam_mov = rotate2d(cam_mov_vector.to_tuple(), -camera.yaw)
        camera.pos.x += cam_mov.x
        camera.pos.z += cam_mov.y

        # Other
        if key[0] == controls["toggle_tri_mode"] and not key[1]:
            global_.tri_mode = not global_.tri_mode

    if global_.tri_mode:

        global_.mouse_left_down = pg.mouse.get_pressed()[0]

        if global_.mouse_left_down and not global_.mouse_left_was_down:
            create_tri_from_ui()
            global_.mouse_left_was_down = True
        elif not global_.mouse_left_down:
            global_.mouse_left_was_down = False
        return
    
    global_.current_tri = []
    
    # Mouse Movement
    if pg.mouse.get_pressed()[0]:
        if global_.dmouse_pos[0] != 0:
            camera.yaw = angle_rollover(camera.yaw - (global_.dmouse_pos[0] / 10), 360)
        if global_.dmouse_pos[1] != 0:
            camera.pitch = angle_rollover(camera.pitch - (global_.dmouse_pos[1] / 10), 360)
        global_.mouse_left_was_down = True

    # Change camera pitch to be in the range 270, 90
    if camera.pitch > 90 and camera.pitch <= 180:
        camera.pitch = 90
    if camera.pitch < 270 and camera.pitch > 180:
        camera.pitch = 270

    return

def new_cube(pos, size) -> None:   # Returns array of instances of new_point

    # Set up all possible (x, y, z) values
    edgesx = [pos[0] - size, pos[0] + size]
    edgesy = [pos[1] - size, pos[1] + size]
    edgesz = [pos[2] - size, pos[2] + size]

    # Loop through all (x, y, z) and append them to a list as instances of new_point
    for x in edgesx:
        for y in edgesy:
            for z in edgesz:
                new_point(vec3d(x, y, z))

    return None

def get_screen_pos(point: vec3d, restrict_to_window = False):   # Returns a the location on the screen of a point in 3d space. Returns None if point is not in fov

    screen_pos = [0, 0]

    # Get the points location relative to the x rotation of the camera
    relative = rotate3d(point.to_tuple(), (camera.yaw, camera.pitch), camera.pos.to_tuple())

    if global_.tri_mode:
        #relative.z -= (distance((camera.pos.x, camera.pos.y), (relative.x, relative.y)) / 2)
        pass

    # Check if point is behind camera
    if relative.z < camera.pos.z:
        return None

    # x angle from camera to points location after accounting for cam rotation
    anglex = get_angle((relative.x, relative.z), (camera.pos.x, camera.pos.z))
    anglex = round(anglex, 2)

    # y angle from camera to points location after accounting for cam rotation
    dy = relative.y - camera.pos.y
    dist = distance((camera.pos.x, camera.pos.z), (relative.x, relative.z))
    angley = get_angle((dy, dist))
    angley = round(360 - angley, 2)

    # Gets a float from 0-1 indicating how far from the left of the window the point should be drawn
    in_range_x = in_angle(display.bounds.left, display.bounds.right, anglex)
    in_range_y = in_angle(display.bounds.top, display.bounds.bottom, angley)

    # Get where the point would be if the window was wide enough to show it, 
    # Only do this if restrict_to_window was false AND the point is not already on the screen
    if not restrict_to_window and (in_range_x == None or in_range_y == None):

        in_range_x = in_angle(-180, 180, angle_rollover(anglex + 180) - 180)
        in_range_y = in_angle(-180, 180, angle_rollover(angley + 180) - 180)

        screen_pos[0] = in_range_x * (display.width * 3) - display.width
        screen_pos[1] = in_range_y * (display.height * 4) - (display.height * (3 / 2))

        return screen_pos

    # Give back the points (x, y) location in the window if it is in both the x and y fov of the camera
    elif in_range_x != None and in_range_y != None:
        screen_pos[0] = in_range_x * display.width
        screen_pos[1] = in_range_y * display.height
        return screen_pos
    
    return None

def get_dot(point, draw = True) -> tuple:   # Gets and returns screen position of a point. optionally draws the point as a circle

    screen_pos = get_screen_pos(point.pos)

    if screen_pos == None:
        return

    if draw:

        if point.hovered:
            r = 4
        else:
            r = 2

        # Draw dot
        '''
        if global_.tri_mode:
            p = vec2d(screen_pos[0], screen_pos[1])
            pg.draw.circle(global_.screen, (255, 255, 255), p.transform(), r)
        else:
            pg.draw.circle(global_.screen, (255, 255, 255), screen_pos, r)
        '''

        pg.draw.circle(global_.screen, (255, 255, 255), screen_pos, r)

        # Write any label associated with the point on top of it
        #global font
        #font = pg.font.SysFont('arial', 14)
        #point_label = font.render(point.label, False, (255, 255, 255))
        #screen.blit(point_label, (screen_pos[0] - 5, screen_pos[1] - 20))

    return screen_pos

def draw_tri(p1: tuple, p2: tuple, p3: tuple) -> bool:

    if get_screen_pos(p1.pos) == None and get_screen_pos(p2.pos) == None and get_screen_pos(p3.pos) == None:
        return None

    pos1 = get_screen_pos(p1.pos, False)
    pos2 = get_screen_pos(p2.pos, False)
    pos3 = get_screen_pos(p3.pos, False)

    poly = restrict_tri((pos1, pos2, pos3))
    poly_mesh = points_to_mesh_2d(poly)
    
    for tri in poly_mesh:
        pg.draw.polygon(global_.screen, (255, 255, 255), tri, width=0)

    return True

def create_tri_from_ui():
    '''
    Allows user to create triangles in the ui.
    Much easier than manually defining the tris.
    '''
    for p in global_.points:
        if p.hovered == True:
            #p.label = "p" + str(len(current_tri) + 1)
            global_.current_tri.append(p)
            if len(global_.current_tri) == 3:
                global_.tris.append(global_.current_tri)
                global_.tri_mode = False
    
    print(global_.current_tri)

    return

# The big boy main function
def main():

    # Fill and load all global variables
    init_vars()

    running = True

    while running:
        
        events = pg.event.get()

        update_dt()
        update_mouse_pos()

        handle_input()

        global_.screen.fill((0, 0, 0))

        for point in global_.points:
            point_pos = get_dot(point, True)
            if point_pos != None:
                if distance(tuple(point_pos), global_.mouse_pos) < 5:
                    point.hovered = True
                else:
                    point.hovered = False

        for tri in global_.tris:
            draw_tri(tri[0], tri[1], tri[2])

        draw_fps()

        pg.display.update()

        #print(str(camera.yaw) + ", " + str(camera.pitch))

        global_.frame_counter += 1

        # Stop running if tab is closed
        for event in events:
            if event.type == 32787:
                running = False

    return

def testing_func():

    # Generates a grid of dots along the x and y axis
    # Useful for trying to fix rendering issues like fisheye effect
    '''
    points = []
    for i in range(-40, 40):
        for ii in range(-25, 25):
            points.append(vec2d(750 + (i * 15), 375 + (ii * 15)))
    
    screen = pg.display.set_mode((display.width, display.height))

    running = True
    while running:

        pg.draw.rect(screen, (0, 0, 0), pg.Rect(0, 0, 1500, 750))

        for p in points:
            if in_bounds((p.x, p.y), ((0, 1500), (0, 750))):
                new_point = p.transform()
                pg.draw.circle(screen, (255, 255, 255), new_point, 2)

        pg.display.update()

        for event in pg.event.get():
            if event.type == 32787:
                running = False
    '''
    return

# Check if file is being run as main
if __name__ == "__main__":

    #rotate2d((2, 4), 50, "ra")

    #testing_func()
    main()