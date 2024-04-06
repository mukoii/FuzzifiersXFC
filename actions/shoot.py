'''
Filename: shoot
Author: Nathan D (nathan.delcampo@digipen.edu)
Date: 11/9/23

Contributors: Samuel Mbugua (sam.mbugua@digipen.edu)

Desc: Contains shoot class which handles the shooting of
the ship at asteroids

'''
from typing import Dict, Tuple
from shapely.geometry import LineString
from shapely.geometry import Point
from shapely.geometry import Polygon
import math
import numpy as np


# The Shoot class provides methods for calculating the angle to turn and whether to shoot at an
# asteroid in a game.
class Shoot:
    def __init__(self):
        self.shot_at = []

    def shoot_at(self, asteroid: Dict, ship: Dict, index):
        '''
        Desc:
            Given an asteroid, find the turning distance needed
                to turn the ship toward said asteroid, and if the  
                asteroid should shoot at said asteroid

            Asteroid is also added to the shot_at list to stop
                asteroid from being shot twice and missing

        Params:
            asteroid: A dict containg the information of the asteroid
            ship: A dict containing the information about the ship
            index: The index of the asteroid is the overall asteroid dict

        Returns: 
            A tuple, containing the angle to turn, and a bool deciding 
                if the ship should shoot
        '''

        # get asteroid data
        asteroidPos = asteroid["position"]
        velocity = asteroid["velocity"]

        # get ship data
        shipPos = ship["position"]
        shipAngle = ship["heading"]

        # get distance between ship and asteroid
        distance = Point(shipPos[0], shipPos[1]).distance(
            Point(asteroidPos[0], asteroidPos[1]))

        # get estimated time to for bullet to hit
        estimateBulletTime = distance/800

        # get angle vector
        angleVector = self.__get_angle_vector(
            asteroidPos[0], asteroidPos[1], shipPos[0], shipPos[1])

        # check if ship is already facing towards asteroid (within 15 degrees)
        if (math.isclose(angleVector["angle"], shipAngle, abs_tol=15)):

            # calculate new position slightly ahead of asteroid
            asteroidHitPos = (asteroidPos[0] + (estimateBulletTime * velocity[0] * 1.25),
                              asteroidPos[1] + (estimateBulletTime * velocity[1] * 1.25))

            # get new angle vector
            newAngleVector = self.__get_angle_vector(
                asteroidHitPos[0], asteroidHitPos[1], shipPos[0], shipPos[1])

            abs_tol = 10 if asteroid['size'] > 1 else 5

            # if already racing really close (within 5) shoot
            if (math.isclose(angleVector["angle"], shipAngle, abs_tol=abs_tol)):
                # Try to add to shoot list
                if (self.__add_to_shot_list(index, estimateBulletTime) == False):
                    # RETURN None for shooting to goto next
                    return None
                
                # return turn distance needed
                return (newAngleVector["angle"] - shipAngle/abs_tol, True)
            else:
                # else don't shoot
                return (newAngleVector["angle"] - shipAngle, False)

        # else if they are close but angles are on opposite sides of 360 (-5, 355)
        elif math.isclose((max(angleVector["angle"], shipAngle) - 360.0), min(angleVector["angle"], shipAngle), abs_tol=10):
            # calculate new position slightly ahead of asteroid
            asteroidHitPos = (asteroidPos[0] + (estimateBulletTime * velocity[0] * 1.5),
                              asteroidPos[1] + (estimateBulletTime * velocity[1] * 1.5))

            # get new angle vector
            newAngleVector = self.__get_angle_vector(
                asteroidHitPos[0], asteroidHitPos[1], shipPos[0], shipPos[1])


            # Try to add to shoot list
            if (self.__add_to_shot_list(index, estimateBulletTime) == False):
                # RETURN None for shooting to goto next
                return None

            # subtract 360 from the bigger angle to make math easier
            if (max(newAngleVector['angle'], shipAngle) == shipAngle):
                shipAngle -= 360.0
            else:
                newAngleVector['angle'] -= 360.0

            # return turn distance needed
            return (newAngleVector["angle"] - shipAngle, True)

        # get vector of ship angle to get angle needed to turn
        shipAngleVector = (math.cos(math.radians(shipAngle)),
                           math.sin(math.radians(shipAngle)))

        # get angle in radians
        angle = math.acos(np.dot(angleVector["vector"], shipAngleVector) /
                          (np.linalg.norm(angleVector["vector"]) * np.linalg.norm(shipAngleVector)))

        # convert to degrees
        angle = math.degrees(angle)

        if (angle > 180):
            return (-180, False)
        else:
            return (180, False)

    def __add_to_shot_list(self, index, travel_time):
        '''
        Desc:
            Appends the given index of an asteroid and
                the estimated time to hit to the shot_at list 
                if not already there

        Parameters:
            index: The index of the asteroid in the overall list
            travel_time: The estimated travel time of the bullet to the
                asteroid

        Returns: 
            False if result found, True if not found and added
        '''

        result = True

        # search for asteroid in the list
        for asteroid in self.shot_at:
            if (asteroid[0] == index):
                result = False
                break

        # if found
        if (result):
            self.shot_at.append([index, travel_time])

        return result

    def update(self, deltatime=1/30):
        ''' 
        
        Desc:
            Updates all asteroids in shot_at list, expected 
                to be called every game update

        Parameters: 
            deltatime: The time that happens each game update

        Returns: N/A
        '''

        # print("CURRENT SHOT AT: ", self.shot_at)
        for asteroid in self.shot_at:
            # print("ASTEROID: ", asteroid)
            asteroid[1] -= deltatime
            # access only the travel_time value
            if (asteroid[1] <= 0):
                # if travel time is 0 then remove
                self.shot_at.remove(asteroid)

    def __get_quadrant(self, x, y):
        '''
        Desc:
            Given a point return the quadrant that point is in

        Parameters:
            x: The x pos of the point
            y: The y pos of the point

        Returns: 
            Int of quadrant
        '''
        if (x > 0):
            if (y > 0):
                return 1
            else:
                return 4
        else:
            if (y > 0):
                return 2
            else:
                return 3

    def __get_angle_vector(self, x1, y1, x2, y2):
        ''' 
        Desc:
            Given 2 sets of points find the angle from point 1 to point 2

        Parameters:
            x1: The x pos of the first point
            y1: The y pos of the first point
            x2: The x pos of the second point
            y2: The y pos of the second point

        Returns: 
            A dict with the angle and the vector 
        '''
        # get vector from point1 to point2
        vector = (x1 - x2, y1 - y2)

        # get angle in degrees
        angle = math.degrees(math.atan(vector[1]/vector[0]))

        quadrant = self.__get_quadrant(vector[0], vector[1])

        # fix angle based on quadrant
        if (quadrant == 2 or quadrant == 3):
            angle += 180
        elif (quadrant == 4):
            angle += 360

        # return vector and angle in a dict
        return {"vector": vector, "angle": angle}
