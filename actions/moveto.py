from typing import Dict, Tuple
from shapely.geometry import Point
import math
import numpy as np

class MoveTo:
    def __init__(self):
        self = self

    def __get_turn_distance(self, x, y, ship: Dict, align = None):
        # get ship data
        shipPos = ship["position"]
        shipAngle = ship["heading"]

        # get vector to the position
        vectorToPos = (x - shipPos[0], y - shipPos[1])

        # get angle of pos
        posAngle = math.atan(vectorToPos[1]/vectorToPos[0])

        if (math.isclose(shipAngle, posAngle, abs_tol=90)):
            # get vector of ship angle to get angle needed to turn
            shipAngleVector = (math.cos(math.radians(shipAngle)), math.sin(math.radians(shipAngle)))

            # get angle in radians
            angle = math.acos(np.dot(vectorToPos, shipAngleVector) /
                         (np.linalg.norm(vectorToPos) * np.linalg.norm(shipAngleVector)))
        
            # convert to degrees
            angle = math.degrees(angle)

            return angle

        

       