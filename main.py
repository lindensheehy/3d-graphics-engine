import pygame as pg
import math, time, json, random

global screen   # Surface representing the window open
global dt   # Delta time. How much time has passed since the last frame
global points   # Array of all points currently being drawn
global print_keys   # Bool if keys pressed are printed to console or not
global mouse_pos   # Current mouse pos
global dmouse_pos   # Change in mouse pos since last frame

# These classes are used to create variables representing 3d attributes. For example coordinates or angles
class new_point:
    def __init__(self, x, y, z):
        self.x = x
        self.y = y
        self.z = z
        self.hovered = False
        self.label = ""

class new_rotation:
    def __init__(self, theta_x, theta_y, theta_z):
        self.rx = theta_x
        self.ry = theta_y
        self.rz = theta_z

# Either constants or objects with many attributes where an array would be confusing.
class camera:

    movement_speed = 60

    x = 0
    y = 0
    z = 0

    yaw = 0   # Around y axis, on the xz plane
    pitch = 0   # Around x axis, on the yz plane
    roll = 0   # Around z axis, on the yx plane

    class fov:
        x = 120
        y = 90

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

# Math Functions
def array_contains(array, val):
    for i in array:
        if i == val:
            return True
    return False

def angle_rollover(angle, max = 360) -> float:   # Changes angles so they are always within 0-360.  -10 would become 350

    new_angle = angle

    while True:
        if new_angle > max:
            new_angle -= max
        elif new_angle < 0:
            new_angle += max
        else:
            break

    return new_angle

def in_angle(low, high, val) -> float:   # Description too long so its inside the function
    # Takes 3 angles as input ranging from 0-360, and returns a decimal representing how far towards high the val is. 
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

def distance(point1, point2 = (0, 0)) -> float:   # Returns distance between 2 points. can be passed either tuples or instances of new_point

    # Distance between 2 points with unlimited components.
    if type(point1) is tuple and type(point2) is tuple:
        sum = 0
        for i in range(len(point1)):
            sum +=math.pow(abs(point1[i] - point2[i]), 2)
        return math.sqrt(sum)

    # Distance between 2 points defined as instances ofaaaaaass new_point
    else:
        dx = abs(point1.x - point2.x)
        dy = abs(point1.y - point2.y)
        dz = abs(point1.z - point2.z)
        return math.sqrt((dx * dx) + (dy * dy) + (dz * dz))

def get_angle(point, angle_from = (0, 0)) -> float:   # Returns the angle from the Y axis to p2 relative to p1

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

def rotate_2d(point, degrees, around = (0, 0)) -> tuple:   # Returns (x, y) of a point rotated "degrees" about another point. COUNTER CLOCKWISE

    # Relative (x, y) location to the "around point"
    relative = [point[0] - around[0], point[1] - around[1]]

    # Trig values
    rads = math.radians(degrees)
    sin = math.sin(rads)
    cos = math.cos(rads)

    # New x and y components
    x = (cos * relative[0]) - (sin * relative[1]) + around[0]
    y = (cos * relative[1]) + (sin * relative[0]) + around[1]

    x = round(x, 3)
    y = round(y, 3)

    return (x, y)

def rotate_3d(point, angle, around) -> new_point:   # Returns the (x, y, z) of a point rotated by any yaw and pitch around another point

    yaw, pitch = angle
    x, y, z = (point.x, point.y, point.z)

    # If yaw is not 0, rotate point about the y axis
    if yaw != 0:
        x, z = rotate_2d((x, z), yaw, (around.x, around.z))

    # If pitch is not 0, rotate point about the x axis
    # Because yaw rotation is done first, camera pitch always lines up with rotation around the x axis
    if pitch != 0:  
        z, y = rotate_2d((z, y), pitch, (around.z, around.y))

    return new_point(x, y, z)

# Setup and every frame update functions
def init_vars():   # Fill all needed variables. Called before startupd

    # Should the key id of key presses be printed to the console
    global print_keys
    print_keys = False

    global keys_down
    keys_down = []

    # Boolean if user is defining a triangle or not. Changes/disables some controls.
    global tri_mode
    tri_mode = False

    # Pygame surface of the window
    global screen
    screen = pg.display.set_mode((display.width, display.height))

    # Set up for pygames fonts to write text to the screen
    pg.font.init()
    global font
    font = pg.font.SysFont('arial', 15)

    # Array of all points to be drawn
    global points
    points = new_cube((100, 0, 100), 20)

    # Array of all triangles to be drawn
    global tris
    tris = []

    global screen_dots
    screen_dots = []

    # Time related variables. Used for both timing and counting frames
    global time_one
    time_one = time.time()

    # Variables for calculating and drawing fps counter
    global timer
    timer = 0
    global frame_count
    frame_count = 0
    global fps
    fps = font.render("0", False, (255, 255, 255))

    # A global counter that only ever increments every frame. Used to have something happen once or every x frames.
    global frame_counter
    frame_counter = 0

    # Mouse position variable and 
    global mouse_pos
    global dmouse_pos
    mouse_pos = pg.mouse.get_pos()

    return

def update_dt():   # Gets new dt (delta time) and sets time_one to current time for next call

    global time_one, dt, timer
    
    dt = time.time() - time_one
    time_one = time.time()
    timer += dt

    return

def update_mouse_pos():   # Updates both mouse_pos and dmouse_pos (delta mouse_pos)

    global mouse_pos, dmouse_pos

    new_mouse_pos = pg.mouse.get_pos()
    dmouse_pos = (mouse_pos[0] - new_mouse_pos[0], mouse_pos[1] - new_mouse_pos[1])
    mouse_pos = new_mouse_pos

    return

def draw_fps():   # Draws the fps counter to the top left of the screen

    global fps, frame_count, timer

    global font
    font = pg.font.SysFont('arial', 15)

    if timer > 1:
        fps = font.render(str(frame_count), False, (255, 255, 255))
        timer = 0
        frame_count = 0
    else:
        frame_count += 1

    screen.blit(fps, (10, 10))

    return

# All the other stuff
def get_player_input():   # Returns array of keys pressed

    global print_keys
    global keys_down

    keys_were_down = []
    for i in keys_down:
        keys_were_down.append(i[0])

    # Array to hold all input events as ints
    keys = []

    #   Mouse   #
    # Grabs mouse down events
    mouse_events = pg.mouse.get_pressed()

    # Checks mouse events and adds a negative value to the list. negative values are reserved for mouse actions
    for click in enumerate(mouse_events):
        if click[1]:
            keys.append([click[0] - 3, array_contains(keys_were_down, click[0])])

    #   Keyboard   #
    # Gets a list of bools for if every key is pressed or not
    all_keys = pg.key.get_pressed()

    # Checks all keys for down, and adds the index of the keydown to the return value for input handling
    for key in enumerate(all_keys):
        if key[1]: 
            keys.append([key[0], array_contains(keys_were_down, key[0])])
    
    # Optionally prints the keys down, used to get key ids
    if print_keys:
        print(keys)

    # This returns an array of all the keys pressed as their numerical id, returns [] if no keys pressed.
    return keys

def handle_input():   # Do all necessary actions based on played input

    global dt
    global tri_mode
    global keys_down
    global mouse_left_was_down

    keys_down = get_player_input()

    controls = json.load(open("controls.json", 'r'))

    distance_moved = camera.movement_speed * dt

    for key in keys_down:

        # Movement
        cam_mov_vector = [0, 0]

        if key[0] == controls["left"]:
            cam_mov_vector[0] -= distance_moved
        elif key[0] == controls["right"]:
            cam_mov_vector[0] += distance_moved
        elif key[0] == controls["forward"]:
            cam_mov_vector[1] += distance_moved
        elif key[0] == controls["backward"]:
            cam_mov_vector[1] -= distance_moved
        elif key[0] == controls["up"]:
            camera.y += distance_moved
        elif key[0] == controls["down"]:
            camera.y -= distance_moved

        # Change (x, z) movement vector based on camera yaw rotation so the forward key always goes forwards
        cam_mov_vector = rotate_2d(cam_mov_vector, -camera.yaw)
        camera.x += cam_mov_vector[0]
        camera.z += cam_mov_vector[1]

        # Other
        if key[0] == controls["toggle_tri_mode"] and not key[1]:
            tri_mode = not tri_mode

    if tri_mode:

        mouse_left_down = pg.mouse.get_pressed()[0]

        if mouse_left_down and not mouse_left_was_down:
            create_tri_from_ui()
            mouse_left_was_down = True
        elif not mouse_left_down:
            mouse_left_was_down = False
        return
    
    global current_tri
    current_tri = []
    
    # Mouse Movement
    global dmouse_pos
    if pg.mouse.get_pressed()[0]:
        if dmouse_pos[0] != 0:
            camera.yaw = angle_rollover(camera.yaw - (dmouse_pos[0] / 10), 360)
        if dmouse_pos[1] != 0:
            camera.pitch = angle_rollover(camera.pitch - (dmouse_pos[1] / 10), 360)
        mouse_left_was_down = True

    # Change camera pitch to be in the range 270, 90
    if camera.pitch > 90 and camera.pitch <= 180:
        camera.pitch = 90
    if camera.pitch < 270 and camera.pitch > 180:
        camera.pitch = 270

    return

def new_cube(pos, size):   # Returns array of instances of new_point

    points = []

    # Set up all possible (x, y, z) values
    edgesx = [pos[0] - size, pos[0] + size]
    edgesy = [pos[1] - size, pos[1] + size]
    edgesz = [pos[2] - size, pos[2] + size]

    # Loop through all (x, y, z) and append them to a list as instances of new_point
    for x in edgesx:
        for y in edgesy:
            for z in edgesz:
                points.append(new_point(x, y, z))

    return points

def get_screen_pos(point, restrict_to_window = True):   # Returns a the location on the screen of a point in 3d space. Returns None if point is not in fov

    screen_pos = [0, 0]

    # Get the points location relative to the rotation of the camera
    # This is done so all math can be done with facing angles (0, 0) for simplicity
    # Plus it makes checking if the point is behind the player trivial
    relative = rotate_3d(point, (camera.yaw, camera.pitch), camera)

    # Check if point is behind camera
    if relative.z < camera.z:
        return None

    # x angle from camera to points location after accounting for cam rotation
    anglex = get_angle((relative.x, relative.z), (camera.x, camera.z))
    anglex = round(anglex, 2)

    # y angle from camera to points location after accounting for cam rotation
    dy = relative.y - camera.y
    dist = distance((camera.x, camera.z), (relative.x, relative.z))
    angley = get_angle((dy, dist))
    angley = round(360 - angley, 2)

    # Gets a float from 0-1 indicating how far from the left of the window the point should be drawn
    in_range_x = in_angle(display.bounds.left, display.bounds.right, anglex)
    in_range_y = in_angle(display.bounds.top, display.bounds.bottom, angley)

    # Get where the point would be if the window was wide enough to show it, 
    # Only do this if restrict_to_window was false AND the point is not already on the screen
    if not restrict_to_window and in_range_x == None and in_range_y == None:

        in_range_x = in_angle(-180, 180, anglex)
        in_range_y = in_angle(-180, 180, anglex)

        screen_pos[0] = (in_range_x * (3 * display.width)) - display.width
        screen_pos[1] = (in_range_y * (3 * display.height)) - display.height

        return screen_pos

    # Give back the points (x, y) location in the window if it is in both the x and y fov of the camera
    elif in_range_x != None and in_range_y != None:
        screen_pos[0] = in_range_x * display.width
        screen_pos[1] = in_range_y * display.height
        return screen_pos
    
    return None

def get_dot(point, draw = True) -> tuple:   # Gets and returns screen position of a point. optionally draws the point as a circle

    global screen

    screen_pos = get_screen_pos(point)

    if screen_pos == None:
        return
    
    if point.hovered == True:
        r = 4
    else:
        r = 2

    if draw:
        # Draw dot
        pg.draw.circle(screen, (255, 255, 255), screen_pos, r)

        # Write any label associated with the point on top of it
        global font
        font = pg.font.SysFont('arial', 14)
        point_label = font.render(point.label, False, (255, 255, 255))
        screen.blit(point_label, (screen_pos[0] - 5, screen_pos[1] - 20))

    return screen_pos

def draw_tri(p1, p2, p3) -> bool:

    pos1 = get_screen_pos(p1, False)
    pos2 = get_screen_pos(p2, False)
    pos3 = get_screen_pos(p3, False)

    if pos1 == None and pos2 == None and pos3 == None:
        return None

    if True:
        pass

    global screen

    pg.draw.polygon(screen, (255, 255, 255), [pos1, pos2, pos3], width=0)

    return True

def create_tri_from_ui():

    global points, tris
    global current_tri
    global tri_mode

    for p in points:
        if p.hovered == True:
            #p.label = "p" + str(len(current_tri) + 1)
            current_tri.append(p)
            if len(current_tri) == 3:
                tris.append(current_tri)
                tri_mode = False
    
    print(current_tri)

    return

# The big boy main function
def main():

    # Fill and load all global variables
    init_vars()
    global screen
    global frame_counter
    global points, tris
    global screen_dots

    running = True

    while running:
        
        events = pg.event.get()

        update_dt()
        update_mouse_pos()

        handle_input()

        screen.fill((0, 0, 0))

        for point in points:
            point_pos = get_dot(point, True)
            if point_pos != None:
                if distance(tuple(point_pos), mouse_pos) < 5:
                    point.hovered = True
                else:
                    point.hovered = False

        for tri in tris:
            draw_tri(tri[0], tri[1], tri[2])

        draw_fps()

        pg.display.update()

        #print(str(camera.yaw) + ", " + str(camera.pitch))

        frame_counter += 1

        # Stop running if tab is closed
        for event in events:
            if event.type == 32787:
                running = False

    return

# Check if file is being run as main
if __name__ == "__main__":
    main()
