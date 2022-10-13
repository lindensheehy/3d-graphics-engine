import math


# These are all the raw number manipulation functions
# Some math function are still in main becuase they rely on 
# 

class line_equation:
    def __init__(self, dx: float = 0, dy: float = 0, ox: float = 0, oy: float = 0):
        self.dx = dx
        self.dy = dy
        self.ox = ox
        self.oy = oy
        try:
            self.m = dy / dx
        except ZeroDivisionError:
            self.m = None

class my_math_functions:
    
    def num_between(num: float, low: float, high: float, newlowm: float = 0, newhigh: float = 1) -> float:
        '''
        By default, returns a float between 1 and 0 representing how far towards the high end num is
        newlow and newhigh can be changed to give a different range for the output
        Returns None if num is not between low and high
        '''
        if num >= low and num <= high:
            return (num - low) / (high - low)
        return None

    def rollover(num: float, min: float = 0, max: float = 360) -> float:
        '''
        Changes angles so they are always within 0-360.  
        (-10) -> 350
        (370) -> 10
        '''
        new_num = num

        while True:
            if new_num > max:
                new_num -= (max - min)
            elif new_num < min:
                new_num += (max - min)
            else:
                break

        return new_num

    def in_angle(low: float, high: float, num: float) -> float:
        '''
        Takes 3 angles as input ranging from 0-360, and returns a decimal representing how far towards high the val is. 
        Returns None if val is not between low and high
        (300, 60, 0) -> 0.5
        '''
        # Adjust degree values by increments of decrements of 360 so math can be done
        if low > high and num > high:
            low -= 360
            num -= 360
        if low > high and num < low:
            high += 360
            num += 360

        # Return
        return my_math_functions.num_between(num, low, high)
    
    def in_bounds(p: tuple, bounds: tuple) -> bool:
        '''
        p is an any length tuple and bounds is a tuple with the same length of length 2 tuple representing bounds
        For example: (p = (10, 40), bounds = ((0, 20), (10, 70))) -> True
        Returns True if the given point lies within the bounding box specified
        Returns False otherwise
        '''
        for i in enumerate(p):
            if i[1] < bounds[i[0]][0] or i[1] > bounds[i[0]][1]:
                return False

        return True

    def distance(point1: tuple, point2: tuple = (0, 0)) -> float:
        '''
        Returns distance between 2 points in any dimensional space represented as tuples.
        ((0, 3), (0, 0)) -> 3.0
        '''
        # Distance between 2 points with unlimited components.
        if type(point1) is tuple and type(point2) is tuple:
            sum = 0
            for i in range(len(point1)):
                sum += abs(point1[i] - point2[i]) ** 2
            return math.sqrt(sum)

    def get_angle(point: tuple, angle_from: tuple = (0, 0)) -> float:
        '''
        Returns the angle from the Y axis to p2 relative to p1
        ((1, 1), (0, 0)) -> 45.0
        '''
        p1x, p1y = angle_from
        p2x, p2y = point

        # All cases where the 2 points share a coordinate, meaning the angle will be a multiple of 90
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
            # This SHOULD never be reached, but its here just in case
            angle = 0

        # Adjust the angle based on the quadrant the point lies in. Range 0-360
        if p2y < p1y:
            angle = 180 - angle
        if p2x < p1x:
            angle = 360 - angle
        
        # If none of the above apply, the angle lies in quadrant 1 meaning there is no adjustment needed.

        return angle

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

    def restrict_tri(tri: tuple = ((0, 0), (0, 0), (0, 0)), bounds: tuple = ((0, 1500), (0, 750))) -> list:
        if None in tri:
            print(tri)
            raise Exception("One of the points in the triangle was None")
        '''
        Returns a list of tuples of x and y coordinates for the shape of the triangle after being bound
        '''
        m = my_math_functions
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
