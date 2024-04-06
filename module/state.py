'''
Filename: state
Author: David Mann (david.mann@digipen.edu)

'''

import math
from typing import Dict

class Asteroid_State:
    def __init__(self, ):
        self.distance_from_ship
        self.angle_from_ship
    
    def SetDistance(self, distance):
        self.distance_from_ship = distance
    
    def SetAngle(self, angle):
        self.angle_from_ship = angle

    def GetDistance(self):
        return self.distance_from_ship
    
    def GetAngle(self):
        return self.angle_from_ship

class State:
    def __init__(self):
        self.asteroids = []
        self.ship

    def SetState(self, game_state: Dict, ship_state: Dict):
        self.ship = ship_state
        for asteroid in game_state.get('Asteroids'):
            distance = math.dist(asteroid.position, ship_state.position)
            if len(self.asteroids) < 3:
                self.asteroids.append(asteroid)
            else:
                for i in range(len(self.asteroids)):
                    if distance < math.dist(self.asteroids[i], ship_state.position):
                        self.asteroids[i] = asteroid
                        break
