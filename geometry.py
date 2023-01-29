from vectors import Vec2, Vec3
from mathfuncs import my_math_functions as m

class Bounds2:
    '''
    Object to define bounds for 2d space
    '''
    def __init__(self, low: Vec2, high: Vec2):
        self.low = low
        self.high = high
    
    def __repr__(self):
        return f"Bounds between {self.low} and {self.high}"

    def __iter__(self):
        yield (self.low.x, self.low.y)
        yield (self.high.x, self.high.y)
        
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
        x = (self.p1.x + self.p1.x + self.p1.x) / 3
        y = (self.p1.y + self.p1.y + self.p1.y) / 3
        z = (self.p1.z + self.p1.z + self.p1.z) / 3
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

class Mesh:
    def __init__(self):
        self.tris = []

    def add(self, new: Tri3):
        self.tris.append(new)

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
