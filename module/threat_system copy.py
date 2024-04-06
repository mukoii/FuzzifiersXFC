import math
import numpy as np
import skfuzzy as fuzz

from typing import Dict, Tuple
from skfuzzy import control as ctrl
from GAME.module.data import AsteroidData, ShipData
from multiprocessing import Pool, freeze_support, current_process
from functools import partial
import os

class TargetingSystem:
    def __init__(self) -> None:
        self.asteroids = None
        self._fis = self.create_thread_fis
        self.distances = {}

    def update(self, ship_state: Dict, game_state: Dict):
        """Used to get new ship states and game states.

        Args:
            ship_state (Dict): Dictionary of every state avalible in ship ex.(position)
            game_state (Dict): Dictionary of every thing avalibe in game ex.(asteroids)
        """
        self.ship = ship_state
        self.game = game_state
        self.asteroids = game_state["asteroids"]

    @property
    def create_thread_fis(self):
        """Creats a fuzzy control system for getting threat level based on
        the asteroids distance from ship and angle.

        Returns:
            ControlSystemSimulation: Fuzzy control system simulation created from the function.
        """

        distance = ctrl.Antecedent(np.arange(0, 1000.0, 10), "distance")
        angle = ctrl.Antecedent(np.arange(0, 180, 0.5), "angle")
        threat_level = ctrl.Consequent(np.arange(-1, 1, 0.05), "threat_level")

        # distance.automf(
        #     3, variable_type="", invert=True, names=["close", "near", "far"]
        # )

        # Ranges for the Antecedents and Consequent
        distance["close"] = fuzz.trimf(distance.universe, [0.0, 250.0, 500.0])
        distance["near"] = fuzz.trimf(distance.universe, [250.0, 500.0, 750.0])
        distance["far"] = fuzz.trimf(distance.universe, [500.0, 750.0, 1000.0])

        angle["acute"] = fuzz.trimf(angle.universe, [0.0, 30.0, 60.0])
        angle["right"] = fuzz.trimf(angle.universe, [30.0, 60.0, 90.0])
        angle["obtuse"] = fuzz.trimf(angle.universe, [60.0, 90.0, 180.0])

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
        ship = ShipData(self.ship)

        asteroids_ids = {}
        multiprocessing_data = []

        # get data of asteroids into a list
        for i in range(len(self.asteroids)):
            asteroid = AsteroidData(self.asteroids[i], self.ship)
            
            multiprocessing_data.append((asteroid.position, asteroid.angle))

        # Create a partial function
        partial_func = partial(self.compute_threat, shipPos=ship.position)

        # Get the number of CPU cores so 
        # we don't make more processes than cpu can handle
        num_cores = os.cpu_count()
        
        # print("Pooling")

        result = []
        # check that only main is pooling
        if current_process().name == 'MainProcess':
            # freeze support in main process to prevent runtime errors
            freeze_support()
            # try variable to error check
            try:
                print("ATTEMPTING POOL")
                # pool to compute data
                with Pool(min(3, num_cores)) as pool:
                    result = list(pool.imap(partial_func, multiprocessing_data, chunksize=1))

                    print("RESULT: ",result)
                    
                print("FINISH POOL")
                # check for any process that somehow escaped?

                current = current_process()
                process_name = current.name
                print("CURRENT PROCESS PAST POOL", process_name)

            except Exception as e:
                print(f"Error processing data in paralell: {e}")
        else:
            current = current_process()
            process_name = current.name
            print("NOT IN MAIN, IN: ", process_name)

        if (current_process().name is not 'MainProcess'):
            os._exit()

        # loop through again to get threat level
        for i in range(len(result)):
            if result[i] >= 0.5:
                if i in asteroids_ids:
                    asteroids_ids.pop(i)
                if i in self.distances:
                    self.distances.pop(i)

                if len(asteroids_ids) < 10:
                    asteroids_ids[i] = result[i]

                    # get distance
                    asteroid = AsteroidData(self.asteroids[i], self.ship)

                    distance = math.dist(asteroid.position, ship.position)
                    if (distance <= 150):
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

    def compute_threat(self, asteroidPos, asteroidAngle, shipPos):
        '''Function to be multiprocessed to
        '''
        # 1. Calculate Vector from ship to asteroid
        self._fis = self.create_thread_fis()
        
        # 3. Distance of asteroid and ship
        distance = math.dist(
            asteroidPos, shipPos)

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
        if distance > 1000:
            distance = 1000

        # Calculates the threat level from -1 to 1
        self._fis.input["distance"] = distance
        self._fis.input["angle"] = asteroidAngle
        self._fis.compute()

        """
                # print(
                #     f"THEAD_LEVEL: {self._fis.output['threat_level'].round(2)}, ANGLE: {angle}, DISTANCE: {distance}",
                #     end="\r",
                # )
        """

        print("THREAT: ", self._fis.output["threat_level"])

        return self._fis.output["threat_level"]