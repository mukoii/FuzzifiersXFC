'''
Filename: Data
Author: Sam, Nathan
Date: 3/10/24

Desc: Data classes for containg relevant data of various objects in
kessler_game

'''
from typing import Dict, Tuple
import math
import numpy as np

class Position:
    """
    Desc: Class that contains positional data
    """
    def __init__(self, position):
        self.__position = position

    @property
    def x(self):
        return self.__position[0]

    @property
    def y(self):
        return self.__position[1]

    @property
    def position(self):
        return self.__position


class AsteroidData:
    """
    Desc: Class that contains various pieces of relevant data
        from the asteroid kessler_game object
    """
    def __init__(self,  asteroid: Dict, ship_state: Dict):
        self.__angle: float = None
        self.pos:  Position = None
        self.__velocity = None
        self.__vector_to_ship = None
        self.__ship = None
        self.update(asteroid, ship_state)

    @property
    def angle(self) -> float:
        return self.__angle

    @property
    def position(self):
        return self.pos.position

    @property
    def velocity(self):
        return self.__velocity

    @property
    def vector_to_ship(self):
        return self.__vector_to_ship

    def update(self, asteroid: Dict, ship_state: Dict):
        '''
        Desc: Updates the current data in the AsteroidData class

        Parameters: asteroid - The kessler_game data object of the asteroid
                    ship_state - The ship object from kessler_game

        Returns: N/A
        '''
        # Get adata
        self.__ship = ShipData(ship_state)
        self.__velocity = asteroid['velocity']
        self.pos = Position(asteroid['position'])

        # Get a vector from asteroid to ship
        vector_to_ship = (
            self.__ship.pos.x - self.pos.x,
            self.__ship.pos.y - self.pos.y,
            # self.asteroids[i]["position"][0] - self.ship["position"][0],
            # self.asteroids[i]["position"][1] - self.ship["position"][1],
        )

        # Get angle between ship and asterid
        angle = math.acos(
            np.dot(vector_to_ship, self.__velocity)
            / (
                np.linalg.norm(vector_to_ship)
                * np.linalg.norm(self.__velocity)
            )
        )

        # Update variables
        self.__vector_to_ship = vector_to_ship
        self.__angle = math.degrees(angle)


# Class for containing data for mines
class MineData:
    """
    Desc: Class that contains various pieces of relevant data
        from the mine kessler_game object
    """
    def __init__(self, mine : Dict, ship : Dict):  
        self.angle : float = None  
        self.pos : Position = None
        self.__vector_to_ship = None
        self.__ship = None
        self.mask: AsteroidData = None
        self.time_left = None
        self.update(mine, ship)
        self.__create_mask

    @property
    def angle(self) -> float:
        return self.__angle

    @property
    def time_left(self):
        return self.time_left

    @property
    def position(self):
        return self.pos.position

    @property
    def vector_to_ship(self):
        return self.__vector_to_ship
    
    def update(self, mine: Dict, ship_state: Dict):
        '''
        Desc: Updates the current data in the MineData class

        Parameters: mine - The kessler_game data object of the mine
                    ship_state - The ship object from kessler_game

        Returns: N/A
        '''
        self.__ship = ShipData(ship_state)
        self.pos = Position(mine['position'])
        self.time_left = mine["remaining_time"]

        vector_to_ship = (
            self.__ship.pos.x - self.pos.x,
            self.__ship.pos.y - self.pos.y,
            # self.asteroids[i]["position"][0] - self.ship["position"][0],
            # self.asteroids[i]["position"][1] - self.ship["position"][1],
        )

        angle = math.acos(
            np.dot(vector_to_ship, self.__velocity)
            / (
                np.linalg.norm(vector_to_ship)
                * np.linalg.norm(self.__velocity)
            )
        )

        self.__vector_to_ship = vector_to_ship
        self.__angle = math.degrees(angle)

    def __create_mask(self, ship_state: Dict):
        '''
        Desc: Creates an AsteroidData class so the mine can be "masked" as a ship

        Parameters: ship_state - The ship object from kessler_game

        Returns: N/A
        '''
        # Create fake asteroid data with relevant data
        asteroid = {"position": tuple(self.position),
                    "velocity": tuple(0,0)
                    }
        
        mask = AsteroidData(asteroid, ship_state)
    

class ShipData:
    """
    Desc: Class that contains various pieces of relevant data
        from the ship kessler_game object
    """
    def __init__(self, ship_state: Dict):
        self.__angle = None
        self.pos: Position
        self.__velocity = None
        self.update(ship_state)

    @property
    def angle(self) -> float:
        return self.__angle

    @property
    def position(self):
        return self.pos.position

    @property
    def velocity(self):
        return self.__velocity

    def update(self, ship_state: Dict):
        '''
        Desc: Updates the current data in the ShipData class

        Parameters: ship_state - The ship object from kessler_game

        Returns: N/A
        '''
        self.__angle = ship_state['heading']
        self.pos = Position(ship_state['position'])
        self.__velocity = ship_state['velocity']
