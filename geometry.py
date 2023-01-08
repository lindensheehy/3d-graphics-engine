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
    def __init__(self, p1: Vec3, p2: Vec3, p3: Vec3):
        self.p1 = p1
        self.p2 = p2
        self.p3 = p3
        v1 = Vec3(self.p1.x - self.p2.x, self.p1.y - self.p2.y, self.p1.z - self.p2.z)
        v2 = Vec3(self.p1.x - self.p3.x, self.p1.y - self.p3.y, self.p1.z - self.p3.z)
        self.normal = v1.cross_product(v2)

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

    def facing_vec(self, vec: Vec3 = Vec3(0, 1, 0)):
        '''
        Returns a float between 1 and 0 representing how similar the direction the triangles normal vector is to a given vector
        '''
        angle = min(vec.angle_to(self.normal), vec.angle_to(self.normal.scale(-1)))
        return m.num_between(angle, 0, 180)

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

    for i in [pos.x, size.x + pos.x]:
        ret.add(Tri3(
            Vec3(i, pos.y, pos.z), 
            Vec3(i, pos.y, pos.z + size.z), 
            Vec3(i, pos.y + size.y, pos.z)
        ))
        ret.add(Tri3(
            Vec3(i, pos.y + size.y, pos.z + size.z), 
            Vec3(i, pos.y, pos.z + size.z), 
            Vec3(i, pos.y + size.y, pos.z)
        ))

    for i in [pos.y, size.y + pos.y]:
        ret.add(Tri3(
            Vec3(pos.x, i, pos.z), 
            Vec3(pos.x, i, pos.z + size.z), 
            Vec3(pos.x + size.x, i, pos.z)
        ))
        ret.add(Tri3(
            Vec3(pos.x + size.x, i, pos.z + size.z), 
            Vec3(pos.x, i, pos.z + size.z), 
            Vec3(pos.x + size.x, i, pos.z)
        ))

    for i in [pos.z, size.z + pos.z]:
        ret.add(Tri3(
            Vec3(pos.x, pos.y, i), 
            Vec3(pos.x + size.x, pos.y, i), 
            Vec3(pos.x, pos.y + size.y, i)
        ))
        ret.add(Tri3(
            Vec3(pos.x + size.x, pos.y + size.y, i), 
            Vec3(pos.x + size.x, pos.y, i), 
            Vec3(pos.x, pos.y + size.y, i)
        ))

    return ret

def restrict_tri(tri: Tri2, bounds: Bounds2 = Bounds2(Vec2(0, 0), Vec2(1500, 750))) -> list:
    '''
    Returns a list of Vec2's for the shape tri makes after being bound
    '''

    if None in tri:
        print(tri)
        raise Exception("One of the points in the triangle was None")

    verticies = set()
    poly = []

    # Checks all points in the triangle and finds the verticies of the shape that should be visible on the screen
    for p in tri:

        out = False
        other_points = set(tri)
        other_points.remove(p)

        # Handles points beyond the left of the screen
        if p.x < bounds.low.x:
            out = True
            for other in other_points:
                if other.x < bounds.low.x:
                    continue
                place = m.num_between(bounds.low.x, p.x, other.x)
                newy = (p.y - (place * (p.y - other.y)))
                newy = max(0, min(750, newy))
                verticies.add(Vec2(bounds.low.x, newy))

        # Handles points beyond the right of the screen
        elif p.x > bounds.high.x:
            out = True
            for other in other_points:
                if other.x > bounds.high.x:
                    continue
                place = m.num_between(bounds.high.x, other.x, p.x)
                newy = (p.y - ((1 - place) * (p.y - other.y)))
                newy = max(0, min(750, newy))
                verticies.add(Vec2(bounds.high.x, newy))


        # Handles points beyond the bottom of the screen
        if p.y < bounds.low.y:
            out = True
            for other in other_points:
                if other.y < bounds.low.y:
                    continue
                place = m.num_between(bounds.low.y, p.y, other.y)
                newx = (p.x - (place * (p.x - other.x)))
                newx = max(0, min(1500, newx))
                verticies.add(Vec2(newx, bounds.low.y))

        # Handles points beyond the top of the screen
        elif p.y > bounds.high.y:
            out = True
            for other in other_points:
                if other.y > bounds.high.y:
                    continue
                place = m.num_between(bounds.high.y, other.y, p.y)
                newx = (p.x - ((1 - place) * (p.x - other.x)))
                newx = max(0, min(1500, newx))
                verticies.add(Vec2(newx, bounds.high.y))

        if not out:
            verticies.add(p)

    # Ensures verticies are in the proper order so they are shown as a closed shape
    

    return tuple(verticies)

if __name__ == "__main__":
    pass
