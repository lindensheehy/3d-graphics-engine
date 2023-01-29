import math

class Vec2:
    '''
    Class used for 2 dimensional vectors or positions
    Contains functions which allow it to be treated similar to a tuple but with attributes x y z for readability
    '''

    # Constructor
    def __init__(self, x: float, y: float):
        '''
        Creates an object with a given (x, y) as well as a magnitude (length)
        '''
        self.x, self.y = x, y
        self.magnitude = math.sqrt((x ** 2) + (y ** 2))

    # Built in function overrides
    def __repr__(self):
        '''
        Returns a string representing the Vec2 object
        Runs by default when a Vec2 object gets printed
        '''
        return f"Vec2({self.x}, {self.y})"

    def __hash__(self):
        '''
        Allows sets to properly use Vec3 objects
        '''
        return hash(self.__repr__())

    def __eq__(self, other):
        '''
        Allows Vec2 objects to be compared. If both x and y components are equal it will return True
        '''
        try:
            return (self.x == other.x) and (self.y == other.y)
        except AttributeError:
            return False

    def __add__(self, other):
        '''
        (Vec2, Vec2) -> Vec2
        Allows Vec2 objects to perform vector addition
        '''
        x = self.x + other.x
        y = self.y + other.y
        return Vec3(x, y)

    def __sub__(self, other):
        '''
        (Vec2, Vec2) -> Vec2
        Allows Vec2 objects to perform vector subtraction
        '''
        x = self.x - other.x
        y = self.y - other.y
        return Vec2(x, y)

    def __mul__(self, other):
        '''
        (Vec2, float) -> Vec2
        Overrides python multiplication to do the vector scale function
        '''
        return self.scale(other)

    def __iter__(self):
        '''
        This function allows the Vec3 object to be treated as a tuple (x, y)
        '''
        yield self.x
        yield self.y

    # Class functions
    def copy(self):
        '''
        Returns a vector with the same components in a new memory location
        '''
        return Vec2(self.x, self.y)

    def scale(self, factor):
        '''
        (Vec2, float) -> Vec2
        Scales the vector by a given factor
        '''
        self.x *= factor
        self.y *= factor
        return self

    def distance_to(self, other):
        '''
        Returns the distance between one position and another
        '''
        return math.sqrt(((self.x - other.x) ** 2) + ((self.y - other.y) ** 2))

    def in_bounds(self, bounds: tuple) -> bool:
        '''
        Bounds is given as a tuple of 2 points serving as a min and then max respectively
        Returns True if the given point lies within the bounding box specified
        Returns False otherwise
        '''
        return (
            self.x > bounds[0][0] and
            self.y > bounds[0][1] and
            self.x < bounds[1][0] and
            self.y < bounds[1][1]
        )

    def dot_product(self, other) -> float:
        '''
        (Vec2, Vec2) -> float
        Returns the dot product of the two vectors
        '''
        return (self.x * other.x) + (self.y * other.y)

    def rotate(self, degrees: float, around = None):
        '''
        Rotates self some number of degrees about another point and returns the new self
        COUNTER CLOCKWISE
        '''

        # Check to make sure all parameters are the proper type, and throw a specific error if not.
        try:

            if degrees == 0:
                return self

            # Make the around parameter be the origin if no argument was passed
            if around == None:
                around = Vec2(0, 0)

            # Relative (x, y) location to the "around" point
            rel = Vec2(self.x - around.x, self.y - around.y)

            # Trig values
            sin = math.sin(math.radians(degrees))
            cos = math.cos(math.radians(degrees))

            # New components
            self.x = (cos * rel.x) - (sin * rel.y) + around.x
            self.y = (cos * rel.y) + (sin * rel.x) + around.y

            return self

        except TypeError:
            raise Exception(f"\n{self}.rotate2d(degrees = {degrees}, around = {around})\nInvalid Arguments")

class Vec3:
    '''
    Class used for 3 dimensional vectors or positions
    Contains functions which allow it to be treated similar to a tuple but with attributes x y z for readability
    '''

    # Constructor
    def __init__(self, x: float, y: float, z: float):
        '''
        Creates an object with a given (x, y, z) as well as a magnitude (length)
        '''
        self.x, self.y, self.z = x, y, z
        self.magnitude = math.sqrt((x ** 2) + (y ** 2) + (z ** 2))

    # Built in function overrides
    def __repr__(self) -> str:
        '''
        Returns a string representing the Vec3 object
        Runs by default when a Vec3 object gets printed
        '''
        return f"Vec3({self.x}, {self.y}, {self.z})"

    def __hash__(self):
        '''
        Allows sets to properly use Vec3 objects
        '''
        return hash(self.__repr__())

    def __eq__(self, other):
        '''
        Allows Vec3 objects to be compared. If all x, y and z components are equal it will return True
        '''
        try:
            return (self.x == other.x) and (self.y == other.y) and(self.z == other.z)
        except AttributeError:
            return False

    def __add__(self, other):
        '''
        (Vec3, Vec3) -> Vec3
        Allows Vec3 objects to perform vector addition
        '''
        x = self.x + other.x
        y = self.y + other.y
        z = self.z + other.z
        return Vec3(x, y, z)

    def __sub__(self, other):
        '''
        (Vec3, Vec3) -> Vec3
        Allows Vec3 objects to perform vector subtraction
        '''
        x = self.x - other.x
        y = self.y - other.y
        z = self.z - other.z
        return Vec3(x, y, z)

    def __mul__(self, other):
        '''
        (Vec3, float) -> Vec3
        Overrides python multiplication to do the vector scale function
        '''
        return self.scale(other)

    def __iter__(self):
        '''
        This function allows the Vec3 object to be treated as a tuple (x, y, z)
        '''
        yield self.x
        yield self.y
        yield self.z

    # Class functions
    def copy(self):
        '''
        Returns a vector with the same components in a new memory location
        '''
        return Vec3(self.x, self.y, self.z)

    def scale(self, factor: float):
        '''
        (Vec3, float) -> Vec3
        Scales the vector by a given factor
        '''
        self.x *= factor
        self.y *= factor
        self.z *= factor
        return self

    def normalise(self, magnitude: float = 1):
        '''
        (Vec3, float)
        Changes the magnitude of the vector while keeping the porportions of each component
        '''
        self.x *= magnitude / self.magnitude
        self.y *= magnitude / self.magnitude
        self.z *= magnitude / self.magnitude
        return

    def distance_to(self, other):
        '''
        Returns the distance between one position and another
        '''
        return math.sqrt(((self.x - other.x) ** 2) + ((self.y - other.y) ** 2) + ((self.z - other.z) ** 2))

    def in_bounds(self, bounds: tuple) -> bool:
        '''
        Bounds is given as a tuple of 2 points serving as a min and then max respectively
        Returns True if the given point lies within the bounding box specified
        Returns False otherwise
        '''
        return (
            self.x > bounds[0][0] and
            self.y > bounds[0][1] and
            self.z > bounds[0][2] and
            self.x < bounds[1][0] and
            self.y < bounds[1][1] and
            self.z < bounds[1][2]
        )

    def dot_product(self, other) -> float:
        '''
        (Vec3, Vec3) -> float
        Returns the dot product of two vectors
        '''
        return (self.x * other.x) + (self.y * other.y) + (self.z * other.z)
    
    def cross_product(self, other):
        '''
        (Vec3, Vec3) -> Vec3
        Returns the cross product of self and other which will be a vector perpendicular to the given ones
        '''
        x = (self.y * other.z) - (self.z * other.y)
        y = (self.z * other.x) - (self.x * other.z)
        z = (self.x * other.y) - (self.y * other.x)
        return Vec3(x, y, z)

    def angle_to(self, other) -> float:
        '''
        (Vec3, Vec3) -> float
        Returns the angle between 2 vectors in 3d space (along the plane they share)
        '''
        try:
            return math.degrees(math.acos((self.dot_product(other)) / (self.magnitude * other.magnitude)))
        except ZeroDivisionError:
            print("divided by zero")
            return 0

    def rotate(self, yaw: float = 0, pitch: float = 0, around = None):
        '''
        (Vec3, float, float, Vec3) -> Vec3
        Rotates self by a yaw and pitch around some point and returns the new location
        '''

        try:

            if around == None:
                around = Vec3(0, 0, 0)

            if yaw != 0:
                self.x, self.z = Vec2(self.x, self.z).rotate(yaw, Vec2(around.x, around.z))

            # If pitch is not 0, rotate point about the x axis
            # Because yaw rotation is done first, camera pitch axis always lines up with rotation around the x axis
            if pitch != 0:
                self.z, self.y = Vec2(self.z, self.y).rotate(pitch, Vec2(around.z, around.y))

            # If pitch is not 0, rotate point along the plane shared between the vector and the y axis
            if pitch != 0:

                dist_from_y_axis = math.sqrt((self.x - around.x) ** 2 + (self.z - around.z) ** 2)

                pitch_vec = Vec2(dist_from_y_axis, self.y)
                pitch_vec.rotate(pitch)

                self.x *= pitch_vec.x / dist_from_y_axis
                self.z *= pitch_vec.x / dist_from_y_axis
                self.y = pitch_vec.y

            return self

        except TypeError:
            raise Exception(f"\n{self}.rotate2d(yaw = {yaw}, pitch = {pitch}, around = {around})\nInvalid Arguments")