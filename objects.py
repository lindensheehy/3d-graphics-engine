from vectors_lib.vectors import Vec2, Vec3
from geometry import Mesh

'''
This file contains code for objects which appear in the program such as boxes spheres enemies terrain of anything else
Each type of object has thier own instances set. Super classes instances sets will also contain thier childrens instances
'''

class Object:
    '''
    general super class for all types of objects
    This class contains some empty functions. The reason for this is so that child classes can overwrite these.
    This is done so that a specific function which may not pertain to certain types can still be called for all objects
    This is also done so each object class can decide for themselves how to handle certain events
    '''

    # Set of objects which currently exist
    instances = set()

    # Constructor
    def __init__(self, pos: Vec3, mesh: Mesh):
        '''
        Create the object and add it to the instances set
        '''
        self.mesh = mesh
        self.pos = pos
        print(f"Object Created at {self.pos}")
        Object.instances.add(self)

    # Built in function overrides
    def __del__(self):
        '''
        remove the object being deleted from the instances set
        Runs auotmatically on "del object"
        '''
        print(f"Object Deleted at {self.pos}")
        Object.instances.remove(self)

    # Instance functions
    def move(self, move_vec: Vec3, move_center = True):
        '''
        Moves the object along some vector
        '''
        if move_center:
            self.pos += move_vec

        for tri in self.mesh.tris:
            tri.move(move_vec)

        return self

    def rotate(self, yaw, pitch, roll, around: Vec3 = None, move_center = True):
        '''
        rotates the object around some point
        if no point it given to rotate around, it will rotate around its own center
        '''

        if move_center and around is not None:
            self.pos.rotate(yaw, pitch, roll, around)

        if around is None:
            around = self.pos
        
        for tri in self.mesh.tris:
            tri.rotate(yaw, pitch, roll, around)

        return self

    def add_force(self, force: Vec3):
        '''   EMPTY   '''
        return
    
    def set_force(self, force: Vec3):
        '''   EMPTY   '''
        return
    
    def do_physics(self, delta_time: float):
        '''   EMPTY   '''
        return

    def collides(self, other) -> bool:
        '''
        Returns true if the and part of self lies within other
        Returns false otherwise
        '''

        return False

    # Class functions
    def count():
        '''
        return the number of objects which currently exist
        '''
        return len(Object.instances)
    
    def all():
        '''
        return all the instances of objects as a list
        '''
        return list(Object.instances)
    
class PhysicsObject(Object):
    '''
    Type of object which can be moved using forces
    '''

    # Set of physics objects which currently exist
    instances = set()

    # Constructor
    def __init__(self, pos: Vec3, mesh: Mesh, mass: float, gravity: Vec3 = Vec3(0, 0, 0)):
        super().__init__(pos, mesh)
        self.mass = mass
        self.velocity = Vec3(0, 0, 0)
        self.acceleration = Vec3(0, 0, 0)
        self.gravity = gravity

    # Instance Functions
    def add_force(self, force: Vec3):
        '''
        Adds a force to the object. changes the aceleration inversely based on the objects mass
        '''
        self.acceleration += force / self.mass

    def set_force(self, force: Vec3):
        '''
        Sets the force of the object
        '''
        self.acceleration = force / self.mass

    def do_physics(self, delta_time: float):
        '''
        Changes the velocity and position of the object for the given delta_time
        '''
        self.velocity += (self.acceleration + self.gravity) * delta_time
        self.pos += self.velocity * delta_time
        self.mesh.move(self.velocity * delta_time)

    # Class Functions
    def count():
        '''
        return the number of physics objects which currently exist
        '''
        return len(PhysicsObject.instances)
    
    def all():
        '''
        return all the instances of physics objects as a list
        '''
        return list(PhysicsObject.instances)


if __name__ == "__main__":
    obj = Object(Vec3(0, 0, 0), Mesh([]))
    obj.move(Vec3(1, 2, 3))
    print(obj.pos)