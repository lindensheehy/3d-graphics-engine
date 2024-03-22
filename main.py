import pygame as pg
import numpy as np
import math, time, json, random
import geometry
from mathfuncs import my_math_functions as m
from geometry import Tri2, Tri3, Bounds2, Bounds3, Mesh
from vectors_lib.vectors import Vec2, Vec3
from objects import *

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

# Classes containing variables which need to be avaliable throughout all functions
# Using a classes instead of the global keyword to avoid cluttering the namespace
class camera:

    movement_speed = 200

    pos = Vec3(-500, 500, -500)
    vel = Vec3(0, 0, 0)
    acc = Vec3(0, 0, 0)
    gravity = -500

    yaw = 45   # Around y axis, on the xz plane
    pitch = 45   # Vertically, on the axis of yaw
    roll = 0   # Around z axis, on the yx plane

    rotvec = Vec3(0, 0, 1)

    fov = Vec2(40, 20)

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
    print_keys = True   # Bool if keys pressed are printed to console or not

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

def draw_crosshair():
    '''
    Draws a crosshair at the center of the screen
    Used to show what the camera is "looking" at
    '''

    pg.draw.line(Global.screen, (0, 255, 0), (750, 370), (750, 380), 1)
    pg.draw.line(Global.screen, (0, 255, 0), (745, 375), (755, 375), 1)

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

    # Camera
    if not Global.fly_mode:
        camera.vel.y += camera.gravity * Global.dt
        camera.pos.y += camera.vel.y * Global.dt
        if camera.pos.y < Global.abs_floor:
            camera.vel.y = 0
            camera.pos.y = Global.abs_floor

    # Objects
    for obj in Object.instances:
        obj.do_physics(Global.dt)

def draw_objects():

    distances = list()
    num = 0  # This avoids objects at the same place from being sorted poorly

    for item in Object.instances:
        distances.append([camera.pos.distance_to(item.pos), num, item])
        num += 1

    distances.sort(reverse = True)

    for dist, skip, item in distances:
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

        global box1
        rotate_around = None

        if key[0] == 14:
            #box1.move(Vec3(0, 1, 0))
            box1.rotate(0, 1, 0, rotate_around)
            #box1.gravity = Vec3(0, -10, 0)

        if key[0] == 13:
            #box1.move(Vec3(0, 1, 0))
            box1.rotate(1, 0, 0, rotate_around)

        if key[0] == 15:
            #box1.move(Vec3(0, 1, 0))
            box1.rotate(0, 0, 1, rotate_around)
    
    # Mouse Movement
    if pg.mouse.get_pressed()[0]:
        if Global.dmouse_pos[0] != 0:
            camera.yaw = m.rollover(camera.yaw - (Global.dmouse_pos[0] / 10))
        if Global.dmouse_pos[1] != 0:
            camera.pitch = m.rollover(camera.pitch - (Global.dmouse_pos[1] / 10))
        Global.mouse_left_was_down = True

    # Pitch rotation needs to be done first
    camera.rotvec = Vec3(0, 0, 1)
    camera.rotvec.rotate(0, camera.pitch, 0)
    camera.rotvec.rotate(-camera.yaw, 0, 0)

    # Change camera pitch to be in the range 270, 90
    if camera.pitch > 90 and camera.pitch <= 180:
        camera.pitch = 90
    if camera.pitch < 270 and camera.pitch > 180:
        camera.pitch = 270

    return

def get_screen_pos(point: Vec3) -> Vec2:
    '''
    Returns a the location on the screen of a point in 3d space. Returns None if point is behind camera
    Can return coordinates outside the size of the screen so that triangles which are partially off screen can still be drawn correctly
    '''

    screen_pos = Vec2(0, 0)

    # Get the points location relative to the x rotation of the camera
    relative = point.copy()

    relative.rotate(camera.yaw, 0, 0, camera.pos)
    relative.rotate(0, -camera.pitch, 0, camera.pos)

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
    # This value has 0 being 90 degrees left of the camera and 1 being 90 degrees right of the camera for a total usable range of 180 degrees
    in_range_x = m.in_angle(-180, 180, m.rollover(anglex + 180) - 180)
    in_range_y = m.in_angle(-180, 180, m.rollover(angley + 180) - 180)

    # This takes the above x and y decimal values and turns them into usable screen coordinates based on the cameras fov
    # with an fov of 180, the decial would simply be upscaled and a smaller fov means a smaller range in which these "in_range" varibles would produce points shwon on screen
    rangex = display.width * (180 / camera.fov.x)
    rangey = display.height * (180 / camera.fov.y)
    screen_pos.x = in_range_x * rangex - ((rangex - display.width) / 2)
    screen_pos.y = in_range_y * rangey - ((rangey - display.height) / 2)

    return screen_pos

def draw_tri(tri: Tri3, show_normal = False) -> bool: 
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
    pg.draw.polygon(Global.screen, ((shade * 50) + 205, shade * 255, shade * 255), poly, width=0)

    # Draw the triangles normal vector
    if show_normal:
        try:
            normal_start = tuple(get_screen_pos(tri.center()))
            normal_end = tuple(get_screen_pos(tri.center() + (tri.normal * 5)))
            pg.draw.line(Global.screen, (255, 0, 0), normal_start, normal_end)
        except TypeError:
            pass

    return True

def draw_mesh(mesh: Mesh) -> int:
    '''
    Takes a mesh (group of triangles) and draws all the triangles to the screen
    Returns number of triangles drawn
    '''

    tris_in_draw_dist = list()

    # Check all triangles to make sure they are in the draw distance
    for tri in mesh.tris:
        # Draw distance of -1 means none was given and therefore always draw the traingle
        if (mesh.max_draw_dist == -1) or (tri.center().distance_to(camera.pos) < mesh.max_draw_dist):
            tris_in_draw_dist.append(tri)

    tri_list = list()

    # Sorts tris in mesh based on how similar their normal vec is to the camera facing vec, and then draws them from least similar to most
    for index, tri in enumerate(tris_in_draw_dist):
        tri_list.append([tri.facing_vec(camera.rotvec), index, tri])
    tri_list.sort(reverse = True)

    tris_drawn = 0

    for i in tri_list:
        draw_tri(i[2], True)
        tris_drawn += 1

    return tris_drawn

def main():
    '''
    This function contains the entire program. The primary code here is the loop that runs while the GUI window is open
    '''
    global box1
    box1 = PhysicsObject(Vec3(50, 50, 50), geometry.rect_prism(Vec3(100, 100, 100)), 100)
    box2 = PhysicsObject(Vec3(150, 150, 150), geometry.rect_prism(Vec3(100, 100, 100), Vec3(250, 250, 250)), 100)
    box3 = PhysicsObject(Vec3(250, 250, 250), geometry.rect_prism(Vec3(100, 100, 100), Vec3(-250, 250, -250)), 100)
    #box2 = object(Vec3(300, 300, 300), geometry.rect_prism(Vec3(50, 50, 50), Vec3(300, 300, 300)))

    # This huge block makes a simple mesh of just 2 triangles at y = 0 which acts as the floor
    '''
    floor = object(
        Vec3(0, -1000, 0), 
        Mesh(
            [
                Tri3(
                    Vec3(-1000, 0, -1000),
                    Vec3(-1000, 0, 1000),
                    Vec3(1000, 0, -1000)
                ),
                Tri3(
                    Vec3(1000, 0, 1000),
                    Vec3(1000, 0, -1000),
                    Vec3(-1000, 0, 1000)
                )
            ],
            max_draw_dist = -1
        )
    )
    '''
    #floor.mesh.downsize_tris(1000)


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

        try:
            center = Vec3(0, 0, 0)
            normal_start = tuple(get_screen_pos(center))
            normal_end = tuple(get_screen_pos(camera.rotvec * 10))
            pg.draw.line(Global.screen, (255, 0, 0), normal_start, normal_end)
        except TypeError:
            pass

        draw_crosshair()

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