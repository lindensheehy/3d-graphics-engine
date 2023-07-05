import math

class Vec2:
    '''
    Class used for 2 dimensional vectors (effectively just a set of 2d coordinates)
    Contains functions which allow it to be treated similar to a tuple but with attributes x and y for readability
    '''

    # Constructor
    def __init__(self, x: float, y: float):
        '''
        Creates an object with a given (x, y) as well as a magnitude (length)
        '''

        try:
            self.x = float(x)
            self.y = float(y)
        except ValueError:
            raise Exception(f"Cannot create Vec2 object with x = {x} ({type(x)}), and y={y} ({type(y)})")

        self.magnitude = math.sqrt((self.x ** 2) + (self.y ** 2))

    # Built in function overrides
    def __repr__(self):
        '''
        Returns a string representing the Vec2 object
        Runs by default when a Vec2 object gets printed
        '''
        return f"Vec2({self.x}, {self.y})"

    def __hash__(self):
        '''
        Allows sets to properly use Vec2 objects
        '''
        return hash(self.__repr__())

    def __eq__(self, other):
        '''
        Allows Vec2 objects to be compared ( using == ). If both x and y components are equal it will return True
        '''
        try:
            return (self.x == other.x) and (self.y == other.y)
        except AttributeError:
            # other must not be a Vec2 object
            return False

    def __add__(self, other):
        '''
        (Vec2, Vec2) -> Vec2
        Allows Vec2 objects to perform vector addition
        '''
        try:
            x = self.x + other.x
            y = self.y + other.y
        except AttributeError:
            raise Exception(f"Cannot add type {type(self)} and type {type(other)} (both should be type Vec2)")
        
        return Vec2(x, y)

    def __sub__(self, other):
        '''
        (Vec2, Vec2) -> Vec2
        Allows Vec2 objects to perform vector subtraction
        '''
        try:
            x = self.x - other.x
            y = self.y - other.y
        except AttributeError:
            raise Exception(f"Cannot subtract type {type(self)} and type {type(other)} (both should be type Vec2)")
        
        return Vec2(x, y)

    def __mul__(self, other: float):
        '''
        (Vec2, float) -> Vec2
        Overrides python multiplication to do the vector scale function
        '''

        try:
            factor = float(other)
        except ValueError:
            raise Exception(f"Cannot multiply Vec2 by {other} (type {type(other)}) (should be type int or float)")

        return self.copy().scale(factor)
        
    def __truediv__(self, other: float):
        '''
        (Vec2, float) -> Vec2
        Overrides python division to do vector scaling by a factor of 1/other
        '''
        try:
            factor = 1 / float(other)
        except ValueError:
            raise Exception(f"Cannot divide Vec2 by {other} (type {type(other)}) (should be type int or float)")
        
        return self.copy().scale(factor)

    def __iter__(self):
        '''
        This function allows the Vec2 object to be treated as a tuple (x, y)
        '''
        yield self.x
        yield self.y

    # Instance functions
    def copy(self):
        '''
        Returns a vector with the same components in a new memory location
        '''
        return Vec2(self.x, self.y)

    def scale(self, factor: float):
        '''
        (Vec2, float) -> Vec2
        Scales the vector by a given factor
        '''
        try:
            self.x *= float(factor)
            self.y *= float(factor)
            self.magnitude *= float(factor)
        except ValueError:
            raise Exception(f"Cannot scale a Vec2 object by a factor of: {factor} ({type(factor)})")
        
        return self

    def normalise(self, magnitude: float = 1):
        '''
        Sets the vectors magnitude to a given value (1 by default) while maintaining the same proportions
        '''

        try:
            self.scale( magnitude / self.magnitude )
        except ValueError:
            raise Exception(f"Cannot normalise Vec2 to a magnitude of {magnitude} (type {type(magnitude)}) (should be type int or float)")

        return self

    def distance_to(self, other):
        '''
        (Vec2, Vec2) -> Vec2
        Returns the distance between one position and another
        '''

        try:
            return math.sqrt(((self.x - other.x) ** 2) + ((self.y - other.y) ** 2))
        except AttributeError:
            raise Exception(f"Cannot get distance between Vec2 type and {type(other)} type")

    def midpoint(self, other):
        '''
        Returns the midpoint between 2 vectors. Just averages out the 2 components
        '''
        try:
            return Vec2(
                (self.x + other.x) / 2,
                (self.y + other.y) / 2 
            )
        except AttributeError:
            raise Exception(f"Cant find midpoint between Vec3 and type {type(other)}")

    def in_bounds(self, bounds: tuple) -> bool:
        '''
        (Vec2, (Vec2, Vec2)) -> bool
        Bounds is given as a tuple of 2 Vec2 objects serving as a min and then max
        Returns True if the given point lies within the bounding box specified
        Returns False otherwise
        '''

        if (len(bounds) != 2):
            raise Exception(f"the list 'bounds' is not of length 2: bounds = {bounds}")

        low = bounds[0]
        high = bounds[1]

        if (type(low) != Vec2) or (type(high) != Vec2):
            raise Exception(f"({low} - {high}) is not a valid set of bounds (both endpoints must be Vec2 objects) (currently low ({type(low)} and high ({type(high)})))")
        
        if (low.x > high.x) or (low.y > high.y):
            raise Exception(f"Each coordinate of the low endpoint must be less than its high endpoint counterpart. low = {low} , high = {high}")

        return (
            self.x > low.x and
            self.y > low.y and
            self.x < high.x and
            self.y < high.y
        )

    def dot_product(self, other) -> float:
        '''
        (Vec2, Vec2) -> float
        Returns the dot product of the two vectors
        '''

        if (type(other) != Vec2):
            raise Exception(f"Cannot find dot product of Vec2 and {type(other)}")

        return (self.x * other.x) + (self.y * other.y)

    def rotate(self, degrees: float, around = None):
        '''
        (Vec2, float, Vec2) -> Vec2
        Rotates self some number of degrees about another point and returns the new self
        COUNTER CLOCKWISE
        '''

        # Check to make sure all parameters are the proper type, and throw a specific error if not.
        try:

            if degrees == 0:
                return self

            # Make the around parameter be the origin if no argument was passed
            if around is None:
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
