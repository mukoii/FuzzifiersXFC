'''
Filename: cone_find.py
Author: Nathan D (nathan.delcampo@digipen.edu)
Date: 11/13/2023
Desc: Given ship position and angle, create a 'pyramid' polygon
in that direction and find all asteroids in that direction

'''
from shapely import Polygon, Point, affinity
from typing import Dict, Tuple
import math


class TriangleFind:
    '''
    Desc: Finds all asteroids within a 30 degree angle of a ship by casting a large shapely triangle
        and checking for collision with all asteroids
    
    '''

    def __init__(self, angle, length):
        # The acute angle of the isoceles triangle
        self.triangle = self.__create_triangle__(angle, length)
        self.rotation = 0
        self.asteroids = []

    def __create_triangle__(self, angle, length):
        '''
        Desc: Creates a shapely triangle at a certain angle

        Parameters: angle - The angle to create the triangle
                    length - The height of a triangle

        Returns: The shapely triangle
        '''
        # get other angles, same since isoceles
        otherAngles = (180 - angle) / 2

        # get other side lengths
        otherSideLength = length * \
            math.sin(math.radians(otherAngles)) / math.sin(math.radians(angle))

        # get area
        area = (otherSideLength**2 * math.sin(math.radians(angle))) / 2

        # get height
        height = 2 * area / length

        # get other points based on height
        x1, y1 = 0, 0  # first point
        x2, x3 = height, height  # height away from point
        y2 = length / 2  # length away from height
        y3 = length / -2

        return Polygon([(x1, y1), (x2, y2), (x3, y3)])

    def __rotate(self, angle):
        '''
        Desc: Rotate triangle to a specific angle around the 'tip' 

        Parameters: angle - The angle to rotate by

        Returns: N/A
        '''
        self.triangle = affinity.rotate(self.triangle,
                                        angle,
                                        origin=(
                                            self.triangle.exterior.coords[0]),
                                        use_radians=False)

    def update(self, ship: Dict):
        '''
        Desc: Update triangle based on ship state
            ALWAYS CALL BEFORE FINDING ASTEROIDS

        Parameters: ship - The ship object

        Returns: N/A
        '''
        # get amount triangle should rotate
        rotateAngle = ship["heading"] - self.rotation

        # rotate
        self.__rotate(rotateAngle)
        # print("CURRENT TRIANGLE ANGLE: ", self.rotation)
        # print("TURN BY: ", rotateAngle)
        # print("SHIP ROTATION: ", ship["heading"])
        # update rotation var
        self.rotation = ship["heading"]

        # triangle 'tip' pos
        trianglePos = self.triangle.exterior.coords[0]

        shipPos = ship["position"]

        # print("SHIP POS: ", shipPos)

        # get difference
        xdiff = shipPos[0] - trianglePos[0]
        ydiff = shipPos[1] - trianglePos[1]

        # move triangle
        self.triangle = affinity.translate(self.triangle,
                                           xoff=xdiff,
                                           yoff=ydiff)

        # print("CURRENT TRIANGLE POINTS: ", self.triangle)

    def triangle_find(self, asteroids: Dict):
        '''
        Desc: Find any asteroids in the triangle by creating a shapely Point using their position
            and then using collision feature to check if they are within the 30 degree angle

        Parameter: asteroids - The dict of all asteroids in the game

        Returns: The list of indexes of asteroids that are within 30 degrees of ship
        '''
        # create a list of the indexes of asteroids
        intersectionAsteroids = []

        # Check intersections of each asteroid
        for i in range(len(asteroids)):
            # get asteroid
            asteroid = asteroids[i]

            # get position
            pos = asteroid["position"]

            # if intersection
            # MAYBE MULTIPROCESS THIS?
            if self.__check_intersection(pos[0], pos[1]):
                # append
                intersectionAsteroids.append(i)

        # return the list of indexes
        return intersectionAsteroids

    def __check_intersection(self, x, y):
        '''
        Desc: Checks a given position against the triangle

        Parameters: x - The x pos
                    y - The y pos

        Returns: True or false based on if intersecting
        '''
        # turn point into shapely point
        asteroid = Point(x, y)

        # check intersection and return
        if (self.triangle.intersection(asteroid)):
            return True
        else:
            return False
