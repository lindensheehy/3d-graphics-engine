'''
All code in here works but is not needed for the current version
Keeping it in case I want anything in the future
'''

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


class new_point:
    def __init__(self, pos: Vec3):
        self.pos = pos
        self.hovered = False
        global_.points.append(self)


def get_dot(point, draw = True) -> tuple:   # Gets and returns screen position of a point. optionally draws the point as a circle

    screen_pos = get_screen_pos(point.pos)

    if screen_pos == None:
        return

    if draw:

        if point.hovered:
            r = 4
        else:
            r = 2

        pg.draw.circle(global_.screen, (255, 255, 255), screen_pos, r)

    return screen_pos


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


# Works fine but is far slower than the new version
def restrict_tri(tri: tuple = ((0, 0), (0, 0), (0, 0)), bounds: tuple = ((0, 1500), (0, 750))) -> list:
    '''
    Returns a list of tuples of x and y coordinates for the shape of the triangle after being bound
    '''

    if None in tri:
        print(tri)
        raise Exception("One of the points in the triangle was None")

    # If either all points are inside the bounds or all are outside, return tri
    if m.in_bounds(tri[0], bounds) and m.in_bounds(tri[1], bounds) and m.in_bounds(tri[2], bounds):
        return tri
    if (not m.in_bounds(tri[0], bounds)) and (not m.in_bounds(tri[1], bounds)) and (not m.in_bounds(tri[2], bounds)):
        return tri

    # Variable initiation
    new_points = []

    border = [line_equation(dy = 750), line_equation(dy = 750, ox = 1500), line_equation(dx = 1500, oy = 750), line_equation(dx = 1500)]

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
            p = m.collision(dx, dy, ox, oy, i.dx, i.dy, i.ox, i.oy)
            try:
                if m.in_bounds(p, point_bounds):
                    new_points.append(p)
            except TypeError:
                pass
    
    poly = []

    for p in tri:
        if m.in_bounds(p, bounds):
            poly.append(p)

    poly += new_points

    return poly


# Was used for the restrict_tri function, but its an extremely overcomplicated way of solving the problem
def collision(dx1: float, dy1: float, ox1: float, oy1: float, dx2: float, dy2: float, ox2: float, oy2: float) -> tuple:
        '''
        dx and dy represent the slope of the line
        ox and oy represent a point on the line, the offset from (0, 0)
        Returns a tuple (x, y) of a point where two lines collide
        y = (m1 * x) + b1  and  y = (m2 * x) + b2
        Returns None if lines do not collide
        '''

        # Building First Equation:  y = eq1.m * (x - eq1.ox) + eq1.oy
        eq1_is_vertical = False
        eq1 = line_equation(dx1, dy1, ox1, oy1)

        if eq1.m == None:
            eq1_is_vertical = True


        # Building Second Equation:  y = eq2.m * (x - eq2.ox) + eq2.oy
        eq2_is_vertical = False
        eq2 = line_equation(dx2, dy2, ox2, oy2)

        if eq2.m == None:
            eq2_is_vertical = True


        # If Both lines are vertical, there is no collision
        if eq1_is_vertical and eq2_is_vertical:
            return None

        # Solve for x by substitution
        if eq1_is_vertical:
            x = eq1.ox  # If equation 1 is vertical, the x must be equal to ox1
        elif eq2_is_vertical:
            x = eq2.ox   # If equation 2 is vertical, the x must be equal to ox2
        else:
            try:
                # This huge equation is just a reformed version of:  m1 * (x - ox1) + oy1 = m2 * (x - ox2) + oy2, where x is isolated
                x = ((eq2.oy + (eq1.m * eq1.ox)) - (eq1.oy + (eq2.m * eq2.ox))) / (eq1.m - eq2.m)
            except ZeroDivisionError:
                # The slopes of both lines are equal, meaning no collision
                return None

        # Solve for y based on x using eq1
        try:
            y = eq1.m * (x - eq1.ox) + eq1.oy
        except TypeError:
            y = eq2.m * (x - eq2.ox) + eq2.oy

        return (x, y)


# Class function for Vec3. works well for projection related rotation but not so much for any other purpose
def rotate(self, yaw: float = 0, pitch: float = 0, around = None):
    '''
    (Vec3, float, float, Vec3) -> Vec3
    Rotates self by a yaw and pitch around some point and returns the new location
    '''

    try:

        if around == None:
            around = Vec3(0, 0, 0)

        # If yaw is not 0, rotate point about the y axis
        if yaw != 0:
            self.x, self.z = Vec2(self.x, self.z).rotate(yaw, Vec2(around.x, around.z))

        # If pitch is not 0, rotate point about the x axis
        # Because yaw rotation is done first, camera pitch axis always lines up with rotation around the x axis
        if pitch != 0:
            self.z, self.y = Vec2(self.z, self.y).rotate(pitch, Vec2(around.z, around.y))

        return self

    except TypeError:
        raise Exception(f"\n{self}.rotate2d(yaw = {yaw}, pitch = {pitch}, around = {around})\nInvalid Arguments")
