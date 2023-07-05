import math
from vectors_lib.Vec2 import Vec2
from vectors_lib.Vec3 import Vec3
from mathfuncs import my_math_functions as m

class Bounds2:
    '''
    Object to define bounds for 2d space
    '''
    def __init__(self, low: Vec2, high: Vec2):
        self.low = low
        self.high = high
    
    def __repr__(self):
        return f"Bounds2({self.low} - {self.high})"

    def __iter__(self):
        yield self.low
        yield self.high
        
class Bounds3:
    '''
    Object to define bounds for 3d space
    '''
    def __init__(self, low: Vec3, high: Vec3):
        self.low = low
        self.high = high

    def __repr__(self):
        return f"Bounds between {self.low} and {self.high}"

    def __iter__(self):
        yield (self.low.x, self.low.y, self.low.z)
        yield (self.high.x, self.high.y, self.high.z)

class Tri2:
    '''
    Class used for representing triangles as sets of 3 points in 2d space
    '''
    def __init__(self, p1: Vec2, p2: Vec2, p3: Vec2):
        self.p1 = p1
        self.p2 = p2
        self.p3 = p3

    def __repr__(self) -> str:
        '''
        Returns a string representing the Tri2 object
        Runs by default when a Tri2 object gets printed
        '''
        return f"Tri2({self.p1}, {self.p2}, {self.p3})"

    def __iter__(self):
        '''
        This function allows the Tri2 object to be treated as a tuple (p1, p2, p3)
        '''
        yield self.p1
        yield self.p2
        yield self.p3

class Tri3:
    '''
    Class used for representing triangles as sets of 3 points in 3d space
    '''
    def __init__(self, p1: Vec3, p2: Vec3, p3: Vec3, normal: Vec3 = None):
        self.p1 = p1
        self.p2 = p2
        self.p3 = p3
        v1 = Vec3(self.p1.x - self.p2.x, self.p1.y - self.p2.y, self.p1.z - self.p2.z)
        v2 = Vec3(self.p1.x - self.p3.x, self.p1.y - self.p3.y, self.p1.z - self.p3.z)
        if normal == None:
            self.normal = v1.cross_product(v2)
        else:
            self.normal = normal
        self.normal.normalise()

    def __repr__(self) -> str:
        '''
        Returns a string representing the Tri3 object
        Runs by default when a Tri3 object gets printed
        '''
        return f"Tri3({self.p1}, {self.p2}, {self.p3})"

    def __iter__(self):
        '''
        This function allows the Tri2 object to be treated as a tuple (p1, p2, p3)
        '''
        yield self.p1
        yield self.p2
        yield self.p3

    def center(self):
        '''
        Returns the center of the triangle as a Vec3
        '''
        x = (self.p1.x + self.p2.x + self.p3.x) / 3
        y = (self.p1.y + self.p2.y + self.p3.y) / 3
        z = (self.p1.z + self.p2.z + self.p3.z) / 3
        return Vec3(x, y, z)

    def facing_vec(self, vec: Vec3 = Vec3(0, 1, 0)):
        '''
        Returns a float between 1 and 0 representing how similar the direction the triangles normal vector is to a given vector
        '''
        normal = self.normal.copy()
        angle = min(vec.angle_to(normal), vec.angle_to(normal.scale(-1)))
        return m.num_between(angle, 0, 180)

    def is_facing(self, vec: Vec3 = Vec3(0, 1, 0)) -> bool:
        return vec.angle_to(self.normal) >= 90

    def perimeter(self):
        '''
        returns the length of all the sides of the triangle
        '''

        vertices = [self.p1, self.p2, self.p3, self.p1]
        perimeter = 0

        for i in range(3):
            perimeter += vertices[i].distance_to(vertices[i + 1])

        return perimeter

    def move(self, move_vec: Vec3):
        self.p1 += move_vec
        self.p2 += move_vec
        self.p3 += move_vec

    def rotate(self, yaw, pitch, roll, around: Vec3 = Vec3(0, 0, 0)):
        self.p1.rotate(yaw, pitch, roll, around)
        self.p2.rotate(yaw, pitch, roll, around)
        self.p3.rotate(yaw, pitch, roll, around)
        self.normal.rotate(yaw, pitch, roll)

class Mesh:
    def __init__(self, tri_list: list = list(), max_draw_dist: float = -1):
        self.tris = tri_list
        self.max_draw_dist = max_draw_dist

    def add(self, new: Tri3):
        self.tris.append(new)

    def downsize_tris(self, max_perimeter: float = 100):
        '''
        Makes all the traingles in the mesh have a max perimeter of some value
        ideally this would do area rather than perimeter but perimeter if effectively very similar and much faster to calculate
        This makes it so that big polygons can be partially drawn rather than only being drawn when the whole shape is in the fov
        '''

        run_again = False
        new_tris = list()

        for tri in self.tris:

            perimeter = tri.perimeter()

            # If the perimeter of any triangle is more than double the max allowed, the function will need to run again
            # in order to downsize the triangle to under the max perimeter (downsizing halves the perimeter)
            if perimeter > max_perimeter * 2:
                run_again = True

            # Splits up the triangle into 4 smaller ones if the perimeter is too high
            if perimeter > max_perimeter:

                # Get the midpoints between all vertices
                midpoint12 = tri.p1.midpoint(tri.p2)
                midpoint23 = tri.p2.midpoint(tri.p3)
                midpoint31 = tri.p3.midpoint(tri.p1)

                # Instantiate the new triangles
                newtri1 = Tri3(tri.p1, midpoint12, midpoint31, tri.normal)      # triangle near p1
                newtri2 = Tri3(tri.p2, midpoint12, midpoint23, tri.normal)      # triangle near p2
                newtri3 = Tri3(tri.p3, midpoint23, midpoint31, tri.normal)      # triangle near p3
                newtri4 = Tri3(midpoint12, midpoint23, midpoint31, tri.normal)  # triangle formed in the center of the other 3

                # Add the new sub triangles to the new tri list
                new_tris.append(newtri1)
                new_tris.append(newtri2)
                new_tris.append(newtri3)
                new_tris.append(newtri4)

            else:
                new_tris.append(tri)

        self.tris = new_tris
        
        if run_again:
            self.downsize_tris(max_perimeter)
        
        return

        if count < 1:
            return self

        new_tris = list()

        for tri in self.tris:

            tri_tuple = tuple(tri)

            split_up = False

            for i in range(3):
                if (tri_tuple[i].distance_to(tri_tuple[m.rollover(i + 1, 0, 2)])) > side_length:
                    split_up = True
                    midpoint = tri_tuple[i].midpoint(tri_tuple[m.rollover(i + 1, 0, 2)])

                    # This looks complicated but its just using the rollover function to get the other verticies of the triangle
                    # Both new tris have the midpoint, the third unused vertex and each have one of the other verticies on either end of the midpoint
                    new_tri1 = Tri3(midpoint, tri_tuple[m.rollover(i + 2, -1, 2)], tri_tuple[i], tri.normal)
                    new_tri2 = Tri3(midpoint, tri_tuple[m.rollover(i + 2, -1, 2)], tri_tuple[m.rollover(i + 1, -1, 2)], tri.normal)

                    new_tris.append(new_tri1)
                    new_tris.append(new_tri2)
                    break

            if not split_up:
                new_tris.append(tri)

        self.tris = new_tris

        self.reduce_tris(side_length, count - 1)

class Noise2:
    def __init__(self, start: float, height: float, grid_size: float):
        self.start = start
        self.height = height
        self.grid_size = grid_size

    def get(self, pos: Vec2):
        '''
        returns the height of the noise at a given x, y
        '''

        x1 = math.floor(pos.x)
        x2 = math.ceil(pos.x)
        y1 = math.floor(pos.y)
        y2 = math.ceil(pos.y)

        dx = pos.x - math.floor(pos.x)
        dy = pos.y = math.floor(pos.y)

def rect_prism(size: Vec3, pos: Vec3 = Vec3(0, 0, 0)) -> Mesh:
    '''
    Returns a mesh containing a set of triangles which make up a rectangular prism
    The pos parameter means the starting corner of the prism, and the rectangle will be the area volume occupied by the vector size
    '''

    ret = Mesh()

    for i, normal in [[pos.x,  -size.x], [size.x + pos.x, size.x]]:
        ret.add(Tri3(
            Vec3(i, pos.y, pos.z), 
            Vec3(i, pos.y, pos.z + size.z), 
            Vec3(i, pos.y + size.y, pos.z),
            Vec3(normal, 0, 0)
        ))
        ret.add(Tri3(
            Vec3(i, pos.y + size.y, pos.z + size.z), 
            Vec3(i, pos.y, pos.z + size.z), 
            Vec3(i, pos.y + size.y, pos.z),
            Vec3(normal, 0, 0)
        ))

    for i, normal in [[pos.y, -size.y], [size.y + pos.y, size.y]]:
        ret.add(Tri3(
            Vec3(pos.x, i, pos.z),
            Vec3(pos.x, i, pos.z + size.z),
            Vec3(pos.x + size.x, i, pos.z),
            Vec3(0, normal, 0)
        ))
        ret.add(Tri3(
            Vec3(pos.x + size.x, i, pos.z + size.z), 
            Vec3(pos.x, i, pos.z + size.z), 
            Vec3(pos.x + size.x, i, pos.z),
            Vec3(0, normal, 0)
        ))

    for i, normal in [[pos.z, -size.z], [size.z + pos.z, size.z]]:
        ret.add(Tri3(
            Vec3(pos.x, pos.y, i), 
            Vec3(pos.x + size.x, pos.y, i), 
            Vec3(pos.x, pos.y + size.y, i),
            Vec3(0, 0, normal)
        ))
        ret.add(Tri3(
            Vec3(pos.x + size.x, pos.y + size.y, i), 
            Vec3(pos.x + size.x, pos.y, i), 
            Vec3(pos.x, pos.y + size.y, i),
            Vec3(0, 0, normal)
        ))

    return ret

def restrict_tri(tri: Tri2, bounds: Bounds2 = Bounds2(Vec2(0, 0), Vec2(1500, 750))) -> list:
    '''
    Returns a list of Vec2's for the shape tri makes after being bound
    '''

    if None in tri:
        print(tri)
        raise Exception("One of the points in the triangle was None")

    verticies = list()
    poly = list()

    # Checks all points in the triangle and finds the verticies of the shape that should be visible on the screen
    points = tuple(tri)

    for index, point in enumerate(points):

        out = False

        # Handles points beyond the left of the screen
        if point.x < bounds.low.x:
            out = True
            for other in [points[(index + 2) % 3], points[(index + 1) % 3]]:
                if other.x < bounds.low.x:
                    continue
                place = m.num_between(bounds.low.x, point.x, other.x)
                newy = (point.y - (place * (point.y - other.y)))
                newy = max(0, min(750, newy))
                verticies.append(Vec2(bounds.low.x, newy))

        # Handles points beyond the right of the screen
        elif point.x > bounds.high.x:
            out = True
            for other in [points[(index + 2) % 3], points[(index + 1) % 3]]:
                if other.x > bounds.high.x:
                    continue
                place = m.num_between(bounds.high.x, other.x, point.x)
                newy = (point.y - ((1 - place) * (point.y - other.y)))
                newy = max(0, min(750, newy))
                verticies.append(Vec2(bounds.high.x, newy))


        # Handles points beyond the bottom of the screen
        if point.y < bounds.low.y:
            out = True
            for other in [points[(index + 2) % 3], points[(index + 1) % 3]]:
                if other.y < bounds.low.y:
                    continue
                place = m.num_between(bounds.low.y, point.y, other.y)
                newx = (point.x - (place * (point.x - other.x)))
                newx = max(0, min(1500, newx))
                verticies.append(Vec2(newx, bounds.low.y))

        # Handles points beyond the top of the screen
        elif point.y > bounds.high.y:
            out = True
            for other in [points[(index + 2) % 3], points[(index + 1) % 3]]:
                if other.y > bounds.high.y:
                    continue
                place = m.num_between(bounds.high.y, other.y, point.y)
                newx = (point.x - ((1 - place) * (point.x - other.x)))
                newx = max(0, min(1500, newx))
                verticies.append(Vec2(newx, bounds.high.y))

        if not out:
            verticies.append(point)

    return tuple(verticies)

if __name__ == "__main__":
    pass
