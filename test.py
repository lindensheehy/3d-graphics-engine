'''
This file contributes nothing to the project.
I only have this here to test things which are too complex to be run in a cmd line
'''

class A:
    def __init__(self, val):
        self.val = val
    
    def func(self, multi: float):
        print(self.val * multi)
        return

class B(A):
    def __init__(self, val, val2):
        super().__init__(val)
        self.val2 = val2

    def func2(self):
        print(self.val + self.val2)

class C:
    def __init__(self, val: A):
        self.val = val

if __name__ == "__main__":
    a = A(10)
    a.func(3)

    b = B(10, 2)
    b.func(2)
    b.func2()