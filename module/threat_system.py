"""
File: data.py
Name: Samuel Mbugua (sam.mbugua@digipen.edu)
Date: 11/9/2023

Contributors: Nathan D (nathan.delcampo@digipen.edu)

Desc: Contains ThreatSystem class which
      calculates the threat level of asteroids based on their distance

"""

import math
import numpy as np
import skfuzzy as fuzz
import json

from typing import Dict
from skfuzzy import control as ctrl
from module.data import AsteroidData, ShipData

# The `TargetingSystem` class is a Python class that represents a targeting system for a game, which
# calculates the threat level of asteroids based on their distance and angle from the ship and returns
# a dictionary of the 10 most threatening asteroids.
class TargetingSystem:
    def __init__(self) -> None:
        self.asteroids = None
        self._fis = self.create_thread_fis
        self.distances = {}

    def update(self, ship_state: Dict, game_state: Dict):
        '''The function updates the ship state, game state, and asteroid list.
        
        Parameters
        ----------
            ship_state : Dict
                A dictionary containing the current state of the ship. This could include information such as
                the ship's position, velocity, health, and any other relevant attributes.
            game_state : Dict
                The `game_state` parameter is a dictionary that contains information about the current state of
                the game. It may include information such as the position and velocity of the ship, the positions
                and velocities of asteroids, the score, the level, and any other relevant information needed to
                update the game.
        
        '''
        self.ship = ship_state
        self.game = game_state
        self.asteroids = game_state["asteroids"]

    def __load_config(self):
        file = "threats_config.json"


        with open(file, "r") as f:
            data = json.load(f)

            return data
            

    @property
    def create_thread_fis(self):
        """Creats a fuzzy control system for getting threat level based on
        the asteroids distance from ship and angle.

        Returns:
            ControlSystemSimulation: Fuzzy control system simulation created from the function.
        """

        distance = ctrl.Antecedent(np.arange(0, 1000.0, 10), "distance")
        angle = ctrl.Antecedent(np.arange(-180, 180, 1), "angle")
        threat_level = ctrl.Consequent(np.arange(-1, 1, 0.05), "threat_level")

        # distance.automf(
        #     3, variable_type="", invert=True, names=["close", "near", "far"]
        # )

        # Ranges for the Antecedents and Consequent

        # distance.automf(3, names=['close', 'near', 'far'])
        
        
        config_data = self.__load_config()
        

        distance["close"] = fuzz.trimf(distance.universe, config_data['distances']['close'])
        distance["near"] = fuzz.trimf(distance.universe, config_data['distances']['near'])
        distance["far"] = fuzz.trimf(distance.universe, config_data['distances']['far'])

        angle["acute"] = fuzz.trimf(angle.universe, config_data['angle']['acute'])
        angle["right"] = fuzz.trimf(angle.universe, config_data['angle']['right'])
        angle["obtuse"] = fuzz.trimf(angle.universe, config_data['angle']['obtuse'])

        threat_level["low"] = fuzz.trimf(
            threat_level.universe, [-1.0, -1.0, 0.0])
        threat_level["medium"] = fuzz.trimf(
            threat_level.universe, [-1.0, 0.0, 1.0])
        threat_level["high"] = fuzz.trimf(
            threat_level.universe, [0.0, 1.0, 1.0])

        # Rules for calculating threat level

        rule1 = ctrl.Rule(distance["far"] &
                          angle["acute"], threat_level["low"])
        rule2 = ctrl.Rule(distance["far"] &
                          angle["right"], threat_level["low"])
        rule3 = ctrl.Rule(distance["far"] &
                          angle["obtuse"], threat_level["low"])
        rule4 = ctrl.Rule(distance["near"] &
                          angle["acute"], threat_level["high"])
        rule5 = ctrl.Rule(distance["near"] &
                          angle["right"], threat_level["medium"])
        rule6 = ctrl.Rule(distance["near"] &
                          angle["obtuse"], threat_level["medium"])
        rule7 = ctrl.Rule(distance["close"] &
                          angle["acute"], threat_level["high"])
        rule8 = ctrl.Rule(distance["close"] &
                          angle["right"], threat_level["high"])
        rule9 = ctrl.Rule(distance["close"] &
                          angle["obtuse"], threat_level["medium"])

        rules = [rule1, rule2, rule3, rule4, rule5, rule6, rule7, rule8, rule9]

        fis1_ctrl = ctrl.ControlSystem(rules)

        # The control system simulation for computing the threat_level
        return ctrl.ControlSystemSimulation(fis1_ctrl)

    @property
    def get_threats_ids(self) -> dict:
        '''The `get_threats_ids` function calculates the threat level of asteroids based on their distance
        and angle from the ship, and returns a dictionary of the 10 most threatening asteroids.

        Returns
        -------
            The method `get_threats_ids` returns a dictionary containing the index of asteroids that are
            posing a threat, along with their corresponding threat level.

        '''
        asteroids_ids = {}
        self.distances = {}

        for i in range(len(self.asteroids)):
            asteroid = AsteroidData(self.asteroids[i], self.ship)
            ship = ShipData(self.ship)
            # 1. Calculate Vector from ship to asteroid

            # 3. Distance of asteroid and ship
            distance = math.dist(
                asteroid.position, ship.position)

            """
                # if distance < 250 and len(asteroids_ids) < 10:
                #     asteroids_ids.append(i)
                #     print(f"DISTANCE: {distance}\n")
                # else:
                #     if i in asteroids_ids:
                #         asteroids_ids.remove(i)

                # MAX ANGLE = +-180
                # MAX DISTANCE = 1100

                # print(f"V1: {distance}", end="\r")
            """

            # Clamps distance to max(1000)
            if distance > 900:
                distance = 900

            # Calculates the threat level from -1 to 1
            self._fis.input["distance"] = distance
            self._fis.input["angle"] = asteroid.angle
            self._fis.compute()

            """
                # print(
                #     f"THEAD_LEVEL: {self._fis.output['threat_level'].round(2)}, ANGLE: {angle}, DISTANCE: {distance}",
                #     end="\r",
                # )
            """

            # 4. Set the 10 most threatening in a list
                

            if self._fis.output["threat_level"] >= 0.5:
                asteroids_ids[i] = self._fis.output["threat_level"]
             
            if distance <= 250:   
                self.distances[i] = distance
            
                
           

                # print(f"ANGLE: {asteroid.angle}, DISTANCE: {distance}\n")
                
                
            
            # print(f"THEAD_LEVEL: {self._fis.output['threat_level']}\n")
            """
                # print(f"ANGLE: {angle}")
                # if angle < 50.0 and distance < 250.0 and len(asteroids_ids) < 10:
                #     asteroids_ids.append(i)
                #     # print(f"ANGLE: {angle}, DISTANCE: {distance}\n")

                # else:
                #     if i in asteroids_ids:
                #         asteroids_ids.remove(i)

            """

        self.distances = dict(sorted(self.distances.items(),
                                     key=lambda x: (x[1], x[0])))

        return asteroids_ids  # Index of asteroid that is posing a threat

