import math

class my_math_functions:
    
    def num_between(num: float, low: float, high: float) -> float:
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
        if p2y > p1y:
            angle = 180 - angle
        if p2x > p1x:
            angle = 360 - angle
        
        # If none of the above apply, the angle lies in quadrant 1 meaning there is no adjustment needed.

        return angle

    def smooth(x: float, y1: float, y2: float):
        '''
        returns a value in between y1 and y2 based on the value of x, such that  { 0 <= x <= 1 }
        function will act similar to a sin wave with slope nearing 0 at each bound and being steepest at x=0.5
        '''
