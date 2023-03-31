import pygame as pg
import numpy as np
import math, time, json, random
import geometry
from mathfuncs import my_math_functions as m
from geometry import Tri2, Tri3, Bounds2, Bounds3, Mesh
from vectors import Vec2, Vec3

# These classes are used to create variables with attributes. For example coordinates or angles
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

        # Looks super complicated but really all this does is takes the products of numbers in diagonal lines
        # The majority of the complication here is allowing this function to work for any size matrix

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

class object:

    instances = set()

    def __init__(self, pos: Vec3, mesh: Mesh, mass: float = 0):
        print(f"Object Created at {pos}")
        object.instances.add(self)

        self.mesh = mesh
        self.mass = mass
        self.pos = pos
        self.velocity = Vec3(0, 0, 0)
        self.acceleration = Vec3(0, 0, 0)

    def __del__(self):
        print(f"Object Created at {self.pos}")
        object.instances.remove(self)

    def do_frame(self):
        self.pos.x += self.velocity.x * Global.dt
        self.pos.y += self.velocity.y * Global.dt
        self.pos.z += self.velocity.z * Global.dt

        self.velocity.x += self.acceleration.x * Global.dt
        self.velocity.y += self.acceleration.y * Global.dt
        self.velocity.z += self.acceleration.z * Global.dt

        self.velocity.y += Global.gravity * Global.dt

# Classes containing variables which need to be avaliable throughout all functions
# Using a classes instead of the global keyword to avoid cluttering the namespace
class camera:

    movement_speed = 200

    pos = Vec3(0, 0, 0)
    vel = Vec3(0, 0, 0)
    acc = Vec3(0, 0, 0)

    yaw = 0   # Around y axis, on the xz plane
    pitch = 0   # Vertically, on the axis of yaw
    roll = 0   # Around z axis, on the yx plane

    rotvec = Vec3(0, 0, 1)

    fov = Vec2(120, 90)

class display:

    width = 1500
    height = 750

    bounds = Bounds2(Vec2(0, 0), Vec2(1500, 750))

class Global:

    pg.display.init()
    pg.font.init()
    screen = pg.display.set_mode((display.width, display.height))   # Surface representing the window open
    font = pg.font.SysFont('arial', 15)   # Pygames font object, used to write text to screen

    frame_time = time.time()   # Stores the time at the start of the frame. Used to find dt between frames
    dt = None   # Delta time. How much time has passed since the last frame
    frame_counter = 0   # A frame counter which only ever increments on each frame

    timer = 0   # A timer to detect when 1 second has passed since the last fps update
    frame_count = 0   # A count of how many frames have passed between fps updates
    fps = font.render("0", False, (255, 255, 255))   # Contains a string of how many fps the display is running at

    mouse_pos = pg.mouse.get_pos()   # Current mouse pos
    dmouse_pos = None   # Change in mouse pos since last frame
    keys_down = []   # List of key ids which were pressed on the last frame
    print_keys = False   # Bool if keys pressed are printed to console or not

    objects = []   # List of all objects currently which exist
    
    fly_mode = True   # If true, the player will not be affected by gravity and will fly

    lighting_vec = Vec3(-2, -4, -1)
    gravity = -500   # Number representing the gravitational acceleration
    abs_floor = 0   # The lowest y value the player/camera can go to

# Setup and every frame update functions
def update_dt():
    '''
    Gets new dt (delta time) and sets time_one to current time for next call
    '''
    Global.dt = time.time() - Global.frame_time
    Global.frame_time = time.time()
    Global.timer += Global.dt

    return

def update_mouse_pos():
    '''
    Updates both mouse_pos and dmouse_pos (delta mouse_pos)
    '''
    new_mouse_pos = pg.mouse.get_pos()
    Global.dmouse_pos = (
        Global.mouse_pos[0] - new_mouse_pos[0], 
        Global.mouse_pos[1] - new_mouse_pos[1]
    )
    Global.mouse_pos = new_mouse_pos

    return

def draw_fps():
    '''
    Draws the fps counter to the top left of the screen
    '''

    if Global.timer > 1:
        Global.fps = Global.font.render(str(Global.frame_count), False, (255, 255, 255))
        Global.timer = 0
        Global.frame_count = 0
    else:
        Global.frame_count += 1

    Global.screen.blit(Global.fps, (10, 10))

    return

def draw_sky():
    '''
    Draws the blue background to the window to give the player an idea of thier camera pitch
    '''

    # Get sky height
    h = Vec2(500, 0).rotate(-camera.pitch).y
    h = min(425, max(-375, h))

    # Draw sky
    pg.draw.rect(Global.screen, (50, 50, 150), pg.Rect(0, 0, 1500, h + 350))
    pg.draw.rect(Global.screen, (25, 25, 75), pg.Rect(0, h + 350, 1500, 25))

    return

def do_physics():
    '''
    Makes all objects do what they need to do for the frame
    Only does velocity, acceleration etc.
    '''
    if not Global.fly_mode:
        camera.vel.y += Global.gravity * Global.dt
        camera.pos.y += camera.vel.y * Global.dt
        if camera.pos.y < Global.abs_floor:
            camera.vel.y = 0
            camera.pos.y = Global.abs_floor

def draw_objects():
    for item in object.instances:
        draw_mesh(item.mesh)
    return

# All the other stuff
def get_player_input() -> list:
    '''
    Returns array of keys pressed as ints of the key ids
    '''

    keys_were_down = []
    for i in Global.keys_down:
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
    if Global.print_keys:
        print(keys)

    # This returns an array of all the keys pressed as their numerical id, returns [] if no keys pressed.
    return keys

def handle_input():
    '''
    Do all necessary actions based on played input
    '''

    Global.keys_down = get_player_input()

    with open("controls.json", 'r') as file:
        controls = json.load(file)

    distance_moved = camera.movement_speed * Global.dt

    for key in Global.keys_down:

        # Movement
        cam_mov_vector = Vec2(0, 0)

        # Up and down movement
        if Global.fly_mode:
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
        cam_mov = cam_mov_vector
        cam_mov.rotate(-camera.yaw)
        camera.pos.x += cam_mov.x
        camera.pos.z += cam_mov.y

        # Other
        if key[0] == controls["toggle_fly_mode"] and not key[1]:
            print(camera.rotvec)
            Global.fly_mode = not Global.fly_mode
    
    # Mouse Movement
    if pg.mouse.get_pressed()[0]:
        if Global.dmouse_pos[0] != 0:
            camera.yaw = m.rollover(camera.yaw - (Global.dmouse_pos[0] / 10))
        if Global.dmouse_pos[1] != 0:
            camera.pitch = m.rollover(camera.pitch - (Global.dmouse_pos[1] / 10))
        Global.mouse_left_was_down = True

    camera.rotvec = Vec3(0, 0, 1).rotate(-camera.yaw, -camera.pitch)

    # Change camera pitch to be in the range 270, 90
    if camera.pitch > 90 and camera.pitch <= 180:
        camera.pitch = 90
    if camera.pitch < 270 and camera.pitch > 180:
        camera.pitch = 270

    return

def get_screen_pos(point: Vec3):
    '''
    Returns a the location on the screen of a point in 3d space. Returns None if point is not in fov
    '''

    screen_pos = Vec2(0, 0)

    # Get the points location relative to the x rotation of the camera
    relative = point.copy()

    relative.rotate(camera.yaw, 0, camera.pos)
    relative.z, relative.y = Vec2(relative.z, relative.y).rotate(camera.pitch, Vec2(camera.pos.z, camera.pos.y))

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

    # Gets a value 0-1 for how far the point is towards the top left in x and y directions then translates that to a screen coordinate
    in_range_x = m.in_angle(-180, 180, m.rollover(anglex + 180) - 180)
    in_range_y = m.in_angle(-180, 180, m.rollover(angley + 180) - 180)

    screen_pos.x = in_range_x * (display.width * 3) - display.width
    screen_pos.y = in_range_y * (display.height * 4) - (display.height * (3 / 2))

    return screen_pos

def draw_tri(tri: Tri3) -> bool: 
    '''
    Draws a triangle to the screen.
    '''

    if not tri.is_facing(camera.rotvec):
        return False

    # Project all 3 veticies to 2d space
    pos1 = get_screen_pos(tri.p1)
    pos2 = get_screen_pos(tri.p2)
    pos3 = get_screen_pos(tri.p3)

    if None in [pos1, pos2, pos3]:
        return False

    bounds = tuple(display.bounds)

    # If all 3 points are out of fov return None
    if not ((pos1.in_bounds(bounds)) or (pos2.in_bounds(bounds)) or (pos3.in_bounds(bounds))):
        return False

    # Run the restrict_tri function to bound the triangle to the window borders. making a new polygon which fits to the window if neccesary
    verticies = geometry.restrict_tri(Tri2(pos1, pos2, pos3))
    poly = []
    for i in verticies:
        poly.append(tuple(i))
        
    # Get a shading value and then draw the traingle in a respective lighting
    shade = tri.facing_vec(Global.lighting_vec)
    pg.draw.polygon(Global.screen, (shade * 255, shade * 255, shade * 255), poly, width=0)

    return True

def draw_mesh(mesh: Mesh) -> int:
    '''
    Takes a mesh (group of triangles) and draws all the triangles to the screen
    Returns number of triangles drawn
    '''

    tri_list = list()

    for index, tri in enumerate(mesh.tris):
        tri_list.append([camera.pos.distance_to(tri.center()), index, tri])
    tri_list.sort(reverse = True)

    tris_drawn = 0

    for i in tri_list:
        draw_tri(i[2])
        tris_drawn += 1

    return tris_drawn

def main():
    '''
    This function contains the entire program. The primary code here is the loop that runs while the GUI window is open
    '''

    box1 = object(Vec3(100, 100, 100), geometry.rect_prism(Vec3(100, 100, 100)))
    box2 = object(Vec3(300, 300, 300), geometry.rect_prism(Vec3(50, 50, 50), Vec3(300, 300, 300)))
    #obj = object(Vec3(100, 100, 100), Mesh())
    #obj.mesh.add(Tri3(Vec3(100, 0, 100), Vec3(100, 100, 100), Vec3(0, 0, 100)))
     
    running = True

    while running:
        
        events = pg.event.get()

        update_dt()
        update_mouse_pos()
        handle_input()

        do_physics()

        Global.screen.fill((0, 0, 0))
        draw_sky()
        draw_objects()
        draw_fps()

        pg.display.update()

        Global.frame_counter += 1

        # Stop running if tab is closed
        for event in events:
            if event.type == 32787:
                running = False

    return

# Check if file is being run as main
if __name__ == "__main__":
    main()