from audioop import cross
import pygame as pg
import numpy as np
import math, time, json, random
from mathfuncs import my_math_functions as m

# These classes are used to create variables with attributes. For example coordinates or angles
class vec2d:
    def __init__(self, x, y):
        self.x = x
        self.y = y

    def __str__(self):
        return f"x: {self.x}, y: {self.y}"

    def __iter__(self):
        yield self.x
        yield self.y

    def scale(self, factor):
        self.x *= factor
        self.y *= factor

class vec3d:
    def __init__(self, x: float, y: float, z: float):
        self.x = x
        self.y = y
        self.z = z
        self.magnitude = math.sqrt((x ** 2) + (y ** 2) + (z ** 2))

    def __str__(self):
        return f"x: {self.x}, y: {self.y}, z: {self.z}"

    def __iter__(self):
        yield self.x
        yield self.y
        yield self.z

    def scale(self, factor: float):
        '''
        Scales a vector by a given factor, each component becomes 
        '''
        return vec3d(self.x * factor, self.y * factor, self.z * factor)

    def abs_scale(self, magnitude: float = 1):
        '''
        Returns a vecortsssss
        By defualt, changes magnitude to 1
        '''
        return vec3d(
            (self.x / self.magnitude) * magnitude, 
            (self.y / self.magnitude) * magnitude, 
            (self.z / self.magnitude) * magnitude
        )

class matrix2d:
    def __init__(self, vals):
        '''
        Define a square 2d matrix as an array
        '''
        self.vals = vals
        self.rx = len(vals[0])
        self.ry = len(vals)
        self.square = self.rx == self.ry

    def add_row(self, items: list):
        if len(items) != self.rx:
            raise Exception(f"Attempted to add list {items} as a row to a matrix with {self.rx} collums")
        self.vals += [items]
        self.ry += 1
        self.square = self.rx == self.ry

    def add_collum(self, items: list):
        if len(items) != self.ry:
            raise Exception(f"Attempted to add list {items} as a collum to a matrix with {self.ry} rows")
        for index, item in enumerate(items):
            self.vals[index] += [item]
        self.rx += 1
        self.square = self.rx == self.ry

    def flip(self):
        '''
        Changes the matrix to that the y rows become x rows and vise versa
        '''
        final_value = []
        for i in range(self.rx):
            items = []
            for ii in range(self.ry):
                items += [self.vals[ii][i]]
            final_value += [items]
        self.vals = final_value

    def subset(self, startx: int, starty: int, sizex: int, sizey: int):
        final_value = []
        if startx + sizex <= self.rx and starty + sizey <= self.ry:
            for i in range(starty, starty + sizey):
                final_value.append(self.vals[i][startx:startx + sizex])
        return matrix2d(final_value)

    def determinant(self) -> float:
        '''
        Returns the determinant of a matrix with size r (r by r matrix)
        '''

        if self.square == False:
            raise Exception(f"matrix2d.determinant() was called on a matrix with dimensions {self.rx} x {self.ry}")

        # If the matrix is 1x1, which it really should never be, the function returns the only value.
        if self.rx == 1:
            return self.vals[0][0]

        # If the matrix is 2x2, the other way of computing determinant will give 0, so this is done instead
        if self.rx == 2:
            return (self.vals[0][0] * self.vals[1][1]) - (self.vals[0][1] * self.vals[1][0])
            pass

        # Looks super complicated but really all this does is takes the products of numbers in diagonal lines
        # The magority of the complication here is allowing this function to work for any size matrix

        total = 0

        # First add all the products of the down right diagonals
        for i in range(self.rx):
            product = 1
            for ii in range(self.rx):
                product *= self.vals[ii][m.rollover(i + ii, -1, self.r - 1)]
            total += product
        
        # Then subtract all the products of the diagonals down left
        for i in range(self.rx):
            product = 1
            for ii in range(self.rx):
                product *= self.vals[ii][m.rollover(i - ii, -1, self.r - 1)]
            total -= product
        
        return total

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
        for obj in object.instances:
            obj.x += obj.velocity.x * global_.dt
            obj.y += obj.velocity.y * global_.dt
            obj.z += obj.velocity.z * global_.dt

            obj.velocity.x += obj.acceleration.x * global_.dt
            obj.velocity.y += obj.acceleration.y * global_.dt
            obj.velocity.z += obj.acceleration.z * global_.dt

            obj.velocity.y += global_.gravity * global_.dt

class tri:
    def __init__(self, p1: vec3d, p2: vec3d, p3: vec3d):

        # Individual points making up the triangle
        self.p1 = p1
        self.p2 = p2
        self.p3 = p3

        # Vectors representing distance between points 1,2 ; 2,3 ; 3,1 respectively
        self.v12 = vec3d(
            p1.x - p2.x, 
            p1.y - p2.y, 
            p1.z - p2.z
        )
        self.v23 = vec3d(
            p2.x - p3.x, 
            p2.y - p3.y, 
            p2.z - p3.z
        )
        self.v31 = vec3d(
            p3.x - p1.x, 
            p3.y - p1.y, 
            p3.z - p1.z
        )

        # Normal of the Triangle, can be scaled by any factor including negative
        self.normal = cross_product(self.v12, self.v23)

        # Center point of the triangle
        self.center = vec3d(
            (p1.x + p2.x + p3.x) / 3,
            (p1.y + p2.y + p3.y) / 3,
            (p1.z + p2.z + p3.z) / 3
        )

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
    abs_floor = None   # The lowest y value the player/camera can go to
    tri_mode = None   # If true, the user can click 3 points to make a triangle
    fly_mode = None   # If true, the player will not be affected by gravity and will fly

class camera:

    movement_speed = 60

    pos = vec3d(0, 0, 0)
    vel = vec3d(0, 0, 0)
    acc = vec3d(0, 0, 0)

    yaw = 0   # Around y axis, on the xz plane
    pitch = 0   # Vertically, on the axis of yaw
    roll = 0   # Around z axis, on the yx plane

    rotvec = vec3d(1, 0, 0)

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
        display.bounds.left = rollover(camera.yaw - (camera.fov.x / 2))
        display.bounds.right = rollover(camera.yaw + (camera.fov.x / 2))
        display.bounds.top = rollover(camera.pitch - (camera.fov.y / 2))
        display.bounds.bottom = rollover(camera.pitch + (camera.fov.y / 2))
    '''

# Math Functions
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
        p.x, p.z = tuple(rotate2d((p.x, p.z), yaw, (a.x, a.z)))

    # If pitch is not 0, rotate point about the x axis
    # Because yaw rotation is done first, camera pitch always lines up with rotation around the x axis
    if pitch != 0:
        p.z, p.y = tuple(rotate2d((p.z, p.y), pitch, (a.z, a.y)))

    return p

def cross_product(v1: vec3d, v2: vec3d) -> vec3d:
    '''
    Returns a 3d vector of the cross product between v1 and v2
    In other words a vector perpendicular to v1 and v2
    '''
    x = (v1.y * v2.z) - (v1.z * v2.y)
    y = (v1.z * v2.x) - (v1.x * v2.z)
    z = (v1.x * v2.y) - (v1.y * v2.x)
    return vec3d(x, y, z)

def dot_product(v1: vec3d, v2: vec3d) -> vec3d:
    '''
    Returns the dot product of v1 and v2
    Used to find angle between vectors
    '''
    return (v1.x * v2.x) + (v1.y * v2.y) + (v1.z * v2.z)

def angle_between(v1: vec3d, v2: vec3d) -> vec3d:
    '''
    Returns the angle between 2 vectors in 3d space (along the plane they share)
    '''
    return math.degrees(math.acos((dot_product(v1, v2)) / (v1.magnitude * v2.magnitude)))

def points_to_mesh_2d(points: tuple) -> tuple:
    
    # Create a list of the angle each point makes with the starting point
    start_point = points[0]
    angles = []
    for p in points[1:]:
        angles.append([m.get_angle(start_point, p), p])
    angles.sort()

    mesh = []

    for i in range(len(angles) - 1):
        p1 = angles[i][1]
        p2 = angles[i + 1][1]

        mesh.append((start_point, p1, p2))

    return mesh

def tri_facing_cam(tri: tri) -> float:
    angle = min(angle_between(camera.rotvec, tri.normal), angle_between(camera.rotvec, tri.normal.scale(-1)))
    return m.num_between(angle, 0, 180)

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

    # Boolean value for if the player can fly or not. If True, gravity wont affect the player
    global_.fly_mode = True

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
    global_.gravity = -500

    global_.abs_floor = 0

    return

def update_dt():
    '''
    Gets new dt (delta time) and sets time_one to current time for next call
    '''
    global_.dt = time.time() - global_.time_one
    global_.time_one = time.time()
    global_.timer += global_.dt

    return

def update_mouse_pos():
    '''
    Updates both mouse_pos and dmouse_pos (delta mouse_pos)
    '''
    new_mouse_pos = pg.mouse.get_pos()
    global_.dmouse_pos = (
        global_.mouse_pos[0] - new_mouse_pos[0], 
        global_.mouse_pos[1] - new_mouse_pos[1]
    )
    global_.mouse_pos = new_mouse_pos

    return

def draw_fps():
    '''
    Draws the fps counter to the top left of the screen
    '''
    global_.font = pg.font.SysFont('arial', 15)

    if global_.timer > 1:
        global_.fps = global_.font.render(str(global_.frame_count), False, (255, 255, 255))
        global_.timer = 0
        global_.frame_count = 0
    else:
        global_.frame_count += 1

    global_.screen.blit(global_.fps, (10, 10))

    return

def do_physics():
    '''
    Makes all objects do what they need to do for the frame
    Only does velocity, acceleration etc.
    '''
    if not global_.fly_mode:
        camera.vel.y += global_.gravity * global_.dt
        camera.pos.y += camera.vel.y * global_.dt
        if camera.pos.y < global_.abs_floor:
            camera.vel.y = 0
            camera.pos.y = global_.abs_floor

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

        # Up and down movement
        if global_.fly_mode:
            if key[0] == controls["up"]:
                camera.pos.y += distance_moved
            if key[0] == controls["down"]:
                camera.pos.y -= distance_moved
        else:
            if key[0] == controls["up"] and not key[1]:
                camera.vel.y = 350

        if key[0] == controls["left"]:
            cam_mov_vector.x -= distance_moved
        elif key[0] == controls["right"]:
            cam_mov_vector.x += distance_moved
        elif key[0] == controls["forward"]:
            cam_mov_vector.y += distance_moved
        elif key[0] == controls["backward"]:
            cam_mov_vector.y -= distance_moved

        # Change (x, z) movement vector based on camera yaw rotation so the forward key always goes forwards
        cam_mov = rotate2d(tuple(cam_mov_vector), -camera.yaw)
        camera.pos.x += cam_mov.x
        camera.pos.z += cam_mov.y

        # Other
        if key[0] == controls["toggle_tri_mode"] and not key[1]:
            global_.tri_mode = not global_.tri_mode

        if key[0] == controls["toggle_fly_mode"] and not key[1]:
            global_.fly_mode = not global_.fly_mode

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
            camera.yaw = m.rollover(camera.yaw - (global_.dmouse_pos[0] / 10))
        if global_.dmouse_pos[1] != 0:
            camera.pitch = m.rollover(camera.pitch - (global_.dmouse_pos[1] / 10))
        global_.mouse_left_was_down = True

    camera.rotvec = rotate3d((1, 0, 0), (camera.yaw, camera.pitch))

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
    relative = rotate3d(tuple(point), (camera.yaw, camera.pitch), tuple(camera.pos))

    if global_.tri_mode:
        #relative.z -= (distance((camera.pos.x, camera.pos.y), (relative.x, relative.y)) / 2)
        pass

    # Check if point is behind camera
    if relative.z < camera.pos.z:
        return None

    # x angle from camera to points location after accounting for cam rotation
    anglex = m.get_angle((relative.x, relative.z), (camera.pos.x, camera.pos.z))
    anglex = round(anglex, 2)

    # y angle from camera to points location after accounting for cam rotation
    dy = relative.y - camera.pos.y
    dist = m.distance((camera.pos.x, camera.pos.z), (relative.x, relative.z))
    angley = m.get_angle((dy, dist))
    angley = round(360 - angley, 2)

    # Gets a float from 0-1 indicating how far from the left of the window the point should be drawn
    in_range_x = m.in_angle(display.bounds.left, display.bounds.right, anglex)
    in_range_y = m.in_angle(display.bounds.top, display.bounds.bottom, angley)

    # Get where the point would be if the window was wide enough to show it, 
    # Only do this if restrict_to_window was false AND the point is not already on the screen
    if not restrict_to_window and (in_range_x == None or in_range_y == None):

        in_range_x = m.in_angle(-180, 180, m.rollover(anglex + 180) - 180)
        in_range_y = m.in_angle(-180, 180, m.rollover(angley + 180) - 180)

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

def draw_tri(tri_: tri) -> bool:

    if get_screen_pos(tri_.p1) == None and get_screen_pos(tri_.p2) == None and get_screen_pos(tri_.p3) == None:
        return None

    pos1 = get_screen_pos(tri_.p1, False)
    pos2 = get_screen_pos(tri_.p2, False)
    pos3 = get_screen_pos(tri_.p3, False)

    poly = m.restrict_tri((pos1, pos2, pos3))
    poly_mesh = points_to_mesh_2d(poly)
    
    for tri in poly_mesh:
        shade = tri_facing_cam(tri_)
        pg.draw.polygon(global_.screen, (shade * 255, shade * 255, shade * 255), tri, width=0)

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
            print(p.pos)
            if len(global_.current_tri) == 3:
                global_.tris.append(tri(
                    global_.current_tri[0].pos, 
                    global_.current_tri[1].pos, 
                    global_.current_tri[2].pos
                ))
                global_.tri_mode = False

    return

# The big main function
def main():

    # Fill and load all global variables
    init_vars()

    running = True

    while running:
        
        events = pg.event.get()

        #print(global_.fly_mode)

        update_dt()
        update_mouse_pos()

        handle_input()

        do_physics()

        global_.screen.fill((0, 0, 0))

        # Draw the blue sky
        h = rotate2d((500, 0), -camera.pitch).y
        h = min(425, max(-375, h))
        pg.draw.rect(global_.screen, (50, 50, 150), pg.Rect(0, 0, 1500, h + 350))
        pg.draw.rect(global_.screen, (25, 25, 75), pg.Rect(0, h + 350, 1500, 25))

        for point in global_.points:
            point_pos = get_dot(point, True)
            if point_pos != None:
                if m.distance(tuple(point_pos), global_.mouse_pos) < 5:
                    point.hovered = True
                else:
                    point.hovered = False

        for t in global_.tris:
            draw_tri(t)

        draw_fps()

        pg.display.update()

        #print(str(camera.yaw) + ", " + str(camera.pitch))

        global_.frame_counter += 1

        # Stop running if tab is closed
        for event in events:
            if event.type == 32787:
                running = False

    return

# Check if file is being run as main
if __name__ == "__main__":
    main()