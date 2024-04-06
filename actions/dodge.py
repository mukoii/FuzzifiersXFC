"""
File: dodge.py
Name: Samuel Mbugua (sam.mbugua@digipen.edu)
Date: 11/9/2023

Desc: Contains dodge class which handles the dodging of
        the asteroid for the ship
"""

import itertools
import json
import math
import random
import numpy as np

from module.data import ShipData
from module.data import AsteroidData
from module.pathfinding import PathFinding


class DodgeAgent:
    def __init__(self) -> None:
        self.__load_config()
        self.get_random_var()
        self.actor = Actor()
        self.critic = Critic()

    def get_random_var(self):
        '''The function `get_random_var` selects a random variable and its corresponding value from a given
        dataset.
        
        '''
        
        # Uses found data from threats_config to get variable
        item = random.sample(self.data.items(), 1)
        name, item_vals = item[0]

        chosen_vals = random.sample(self.data[name].items(), 1)[0]
        chosen_val = random.sample(chosen_vals[1], 1)[0]
        val_index = self.data[name][chosen_vals[0]].index(chosen_val)

        self.random_var = [name, chosen_vals[0], chosen_val, val_index]

    def update_var(self, value: float):
        '''The function `update_var` updates a variable in a data structure and saves the updated
        configuration.
        
        '''
    
        type = self.random_var[0]
        name = self.random_var[1]
        val = self.random_var[2]
        index = self.random_var[3]

        # # Actor suggests an action
        # action = self.actor.suggest_action(val)
        
        # # Critic evaluates the action
        # value = self.critic.evaluate(action)

        # Update the variable based on the value from critic
        updated_val = val + value
        
        print("VALUE: ", value, " UPDATED: ", updated_val, " CHOSEN: ", val)
        
        
        # Keeps new variable from breaking Fuzzy Fis
        flag = self.check_valid(type, name, index, updated_val)
         
        if not flag:
            self.update_var(updated_val)

        if flag:
            self.data[type][name][index] = updated_val
            self.save_config()

    def check_valid(self, type, name, index, _val):
        '''The function `check_valid` checks if a given value is valid based on its index in a nested data
        structure.
        
        Parameters
        ----------
        type
            The "type" parameter represents the type of data being checked. It could be a string or an
        integer, depending on how the data is structured in the "self.data" object.
        name
            The parameter "name" is a string that represents the name of the data.
        index
            The index parameter represents the position of the value in a list or array. It is used to
        access the neighboring values in order to perform validity checks on the given value.
        _val
            The parameter `_val` represents the value that needs to be checked for validity.
        
        Returns
        -------
            a boolean value. It returns True if the value is valid according to the conditions specified in
        the code, and False otherwise.
        
        '''
        
        val = _val

        match (index):
            case 0:
                if val > self.data[type][name][index + 1]:
                    return False
            case 1:
                if val < self.data[type][name][index - 1]:
                    return False

                if val > self.data[type][name][index + 1]:
                    return False
            case 2:
                if val < self.data[type][name][index - 1]:
                    return False

        return True

    def __load_config(self):
        file = "threats_config.json"

        with open(file, "r") as f:
            self.data = json.load(f)

    def save_config(self):
        file = "threats_config.json"

        type = self.random_var[0]
        name = self.random_var[1]
        index = self.random_var[3]

        with open(file, "w+") as f:
            json.dump(self.data, f, indent=2)

        print(
            f"Saved: {type}:{name}: {self.data[type][name][index]} -> {self.random_var[2]}"
        )

        # self.get_random_var()


class Actor:
    def suggest_action(self, current_value):
        # Actor suggests an action, for example, return a random value
        return random.uniform(-5, 5)


class Critic:
    def evaluate(self, action):
        # Critic evaluates the action, for example, return a value based on some criteria
        return action * 0.5  # Simple evaluation for demonstration


# The `Dodge` class contains methods to calculate the thrust rate, turn rate, and take action for a
# ship to avoid an asteroid.
class Dodge:
    def __init__(self):
        self.pathFinding = PathFinding()
        self.__ID = None

    # def distance_point_to_segment(self, x, y, x1, y1, x2, y2):
    #     """
    #     Calculate the distance between a point (x, y) and a line segment defined by two points (x1, y1) and (x2, y2)
    #     """
    #     dx = x2 - x1
    #     dy = y2 - y1
    #     if dx == dy == 0:  # The segment's start and end points coincide
    #         return math.hypot(x - x1, y - y1)

    #     t = ((x - x1) * dx + (y - y1) * dy) / (dx * dx + dy * dy)

    #     if t < 0:
    #         px, py = x1, y1
    #     elif t > 1:
    #         px, py = x2, y2
    #     else:
    #         px, py = x1 + t * dx, y1 + t * dy

    #     return math.hypot(x - px, y - py)

    # def is_in_range(self, objectx, objecty, x, y, rearx, reary):
    #     """
    #     Check if an object (objectx, objecty) is within the range defined by two points (x, y) and (rearx, reary)
    #     """
    #     distance_from_segment = self.distance_point_to_segment(objectx, objecty, x, y, rearx, reary)
    #     distance_from_start = math.hypot(objectx - x, objecty - y)
    #     distance_from_end = math.hypot(objectx - rearx, objecty - reary)

    #     max_distance = max(math.hypot(x - rearx, y - reary), math.hypot(x - rearx, y - reary))

    #     return distance_from_segment <= max_distance
    
    
    def thrust_rate(self, asteroid: AsteroidData, ship: ShipData):
        """The function calculates the thrust rate based on the velocity and position of an asteroid and a
        ship, and returns the thrust value.

        Parameters
        ----------
            asteroid : AsteroidData
                The "asteroid" parameter is an instance of the "AsteroidData" class, which contains information
                about the asteroid such as its position, velocity, and angle.
            ship : ShipData
                The ship parameter is an instance of the ShipData class, which contains information about the
                ships 'position, velocity, and angle'.

        Returns
        -------
            the calculated thrust value.

        """

        thrust = 0

        # Values from the ship and asteroid used for calculating acceleration
        v_f = np.linalg.norm(asteroid.velocity)
        v_i = np.linalg.norm(ship.velocity)
        distance = math.dist(asteroid.position, ship.position)

        # Acceleration fromula from vf^2 = vi^2 + 2a(dx)
        # a = vf^2 - vi^2/ 2(dx)

        # Dividing acceleration by to to dampen the speed
        acceleration = ((pow(v_f, 2) - pow(v_i, 2)) / (2 * distance) ) / 15

        thrust = 480 * acceleration  # Max ship thurst is 480

        if thrust > 480:
            thrust = 480

        facing = self.__get_facing(ship)
        quad = self.__get_quadrant(
            asteroid.vector_to_ship[0], asteroid.vector_to_ship[1]
        )
        

        # if self.is_in_range(asteroid.pos.x, asteroid.pos.y, ship.pos.x, ship.pos.y, self.ship_path[1][0], self.ship_path[1][1]):
        #     thrust = 0
        #     print("GONNA CRASH STOPPPPP Behind")
        # elif self.is_in_range(asteroid.pos.x, asteroid.pos.y, ship.pos.x, ship.pos.y, self.ship_path[0][0], self.ship_path[0][1]):
        #     thrust = 0
        #     print("GONNA CRASH STOPPPPP Front")
        # else:
        match facing:
            case "U":
                if quad == 4 or quad == 3:
                    thrust *= -1
            case "D":
                if quad == 2 or quad == 1:
                    thrust *= -1
            case "L":
                if quad == 4 or quad == 1:
                    thrust *= -1
            case "R":
                if quad == 2 or quad == 3:
                    thrust *= -1

        # print(f"\nThrust: {thrust}")
        # if ship.pos.y - asteroid.pos.y < 0 and -135 > ship.angle < -45:
        #     thrust *= -1

        return thrust

    def turn_rate(self, asteroid: AsteroidData, ship: ShipData):
        """The function calculates the turn rate of a ship based on the velocity and position of an
        asteroid.

        Parameters
        ----------
            asteroid : AsteroidData
                The `asteroid` parameter is an instance of the `AsteroidData` class, which contains information
                about the asteroid such as its 'position, velocity, and size'.
            ship : ShipData
                The `ship` parameter is an instance of the `ShipData` class, which contains information about
                the ships 'position, velocity, and angle'.

        Returns
        -------
            the calculated turn rate.

        """
        turn_rate = 0

        # Values from the ship and asteroid used for calculating acceleration
        v_f = np.linalg.norm(asteroid.velocity)
        v_i = np.linalg.norm(ship.velocity)
        distance = math.dist(asteroid.position, ship.position)

        # Acceleration fromula from vf^2 = vi^2 + 2a(dx)
        # a = vf^2 - vi^2/ 2(dx)

        # Dividing acceleration by to to dampen the speed
        acceleration = ((pow(v_f, 2) - pow(v_i, 2)) / (2 * distance)) / 10

        turn_rate = acceleration * 180  # Max ship thurst is 480

        facing = self.__get_facing(ship)
        quad = self.__get_quadrant(
            asteroid.vector_to_ship[0], asteroid.vector_to_ship[1]
        )

        if turn_rate > 180:
            turn_rate = 180
        elif turn_rate < -180:
            turn_rate = -180

      
        match facing:
            case "U":
                if quad == 4 and quad == 3:
                    turn_rate *= -1
            case "D":
                if quad == 2 and quad == 1:
                    turn_rate *= -1
            case "L":
                if quad == 4 and quad == 1:
                    turn_rate *= -1
            case "R":
                if quad == 2 and quad == 3:
                    turn_rate *= -1
                    
        # turn_rate = 0

        # print(f"ASTEROID: {test}")

        # print(f"THRUST: {turn_rate}, \nACCEL: {acceleration}")
        return turn_rate

    def take_action(
        self, ship_state: dict, asteroids: dict, distances: dict, threats: dict
    ) -> [float, float, bool]:
        """The function takes in ship state, asteroid data, IDs, and distances, and calculates the thrust
        and turn rate for the ship based on the closest asteroid.

        Parameters
        ----------
            ship_state : dict
                The `ship_state` parameter represents the current state of the ship. It contains information
                such as the ship's position, velocity, orientation, and fuel level.
            asteroids : dict
                The "asteroids" parameter is a list of dictionaries, where each dictionary represents the state
                of an asteroid. Each dictionary contains information such as the position, velocity, and size of
                the asteroid.
            ids : dict
                The `ids` parameter is a dictionary that maps asteroid IDs to their corresponding indices in
                the `asteroids` list. This is used to easily access specific asteroids in the `asteroids` list
                based on their ID.
            distances : dict
                The `distances` parameter is a dictionary that contains the distances between the ship and each
                asteroid. It is used to determine the closest asteroid to the ship.

        Returns
        -------
            the values of `thrust` and `turn_rate`.

        """

        thrust = 0
        turn_rate = 0

        ship = ShipData(ship_state)
        asteroid = None
        n = 3

        closest_n = dict(itertools.islice(distances.items(), n))
        if len(closest_n) > 0:
            closest_val = list(closest_n.values())[0]
            closest_key = list(closest_n.keys())[0]
    
        for key, val in closest_n.items():
        
            if (threats):
                is_close = threats.get(key)
            else:
                is_close = 0
        
            if val <= 120 and is_close and is_close >= 0.5:
                if (len(closest_n) > 0):
                    if (val >= closest_val):
                        self.pathFinding.path_find(asteroids[closest_key], ship_state, closest_key)
                        if self.pathFinding(closest_key).collision:
                            asteroid = AsteroidData(asteroids[closest_key], ship_state)
                    else:
                        asteroid = AsteroidData(asteroids[key], ship_state)
                        
                else:
                    asteroid = AsteroidData(asteroids[key], ship_state)
     
            
        # self.ship_path = self.pathFinding.path_find_ship(ship, 2)
        # for key, value in distances.items():

        #     # print(f"KEY: {key}, ID: {self.__ID}", end='\n')
        #     # if self.__ID in dict(itertools.islice(distances.items(), 2)):
        #     if self.pathFinding(key).collision:
        #     #     # print(f"COLLISION: {self.__ID}, {value}")
        #         # print(self.pathFinding(key).collision)
        #         if value <= list(distances.values())[0]:
        #             # print(asteroids[key], " ", self.ship_path, end='\r')
            
            # print(ship.pos.x)

        if asteroid:
            thrust = self.thrust_rate(asteroid, ship)
            turn_rate = self.turn_rate(asteroid, ship)
            return thrust, turn_rate, True
        else:
            return thrust, turn_rate, False

    def __get_facing(self, ship: ShipData):
        """The function returns the direction the ship is facing based on its angle.

        Parameters
        ----------
            ship : ShipData
                The parameter `ship` is of type `ShipData`.

        Returns
        -------
            a string indicating the direction the ship is facing. The possible return values are "R" for
            right, "U" for up, "L" for left, and "D" for down.

        """
        angle = ship.angle
        # print("ANGLE: ", ship.angle, end='\n')
        if 0 <= angle < 45 or 315 <= angle <= 360:
            return "R"
        elif 45 <= angle < 135:
            return "U"
        elif 135 <= angle < 225:
            return "L"
        elif 225 <= angle < 315:
            return "D"

    def __get_quadrant(self, x: float, y: float):
        """The function __get_quadrant determines the quadrant of a point on a Cartesian plane based on its x
        and y coordinates.

        Parameters
        ----------
            x : float
                The x parameter represents the x-coordinate of a point in a Cartesian coordinate system.
            y : float
                The parameter `y` represents the y-coordinate of a point in a Cartesian coordinate system.

        Returns
        -------
            the quadrant number based on the given x and y coordinates.

        """
        if x > 0:
            if y > 0:
                return 1
            else:
                return 4
        else:
            if y > 0:
                return 2
            else:
                return 3
