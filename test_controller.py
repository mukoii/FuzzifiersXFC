# -*- coding: utf-8 -*-
# Copyright © 2022 Thales. All Rights Reserved.
# NOTICE: This file is subject to the license agreement defined in file 'LICENSE', which is part of
# this source code package.

from kesslergame import KesslerController
from typing import Dict, Tuple
from module.threat_system import TargetingSystem
from module.pathfinding import PathFinding
from actions.shoot import Shoot
from actions.dodge import Dodge
from module.triangle_find import TriangleFind
from module.action_list import ActionList, action_type
from multiprocessing import Queue
from concurrent.futures import ThreadPoolExecutor

# The TestController class is a game character controller that determines the actions to be taken by a
# ship in a game based on the current ship state and game state.
class TestController(KesslerController):
    def __init__(self):
        '''The function initializes various components of a game character, including a targeting system,
        pathfinding, shooting, dodging, and an action list.

        '''
        self.eval_frames = 0
        self.threat_system = TargetingSystem()
        self.pathFinding = PathFinding()
        self.shoot = Shoot()
        self.dodge = Dodge()
        
        self.action_list = ActionList()  # CURRENT ONLY WORKS WITH DODGE
        self.jobs = []

        # input the width and angle of the triangle
        self.idle = TriangleFind(30, 200)
    
    def get_ids(self, result_queue):
        """
        The function "get_ids" retrieves threat IDs from the threat system and puts them into a result
        queue.
        
        :param result_queue: The `result_queue` parameter is a queue object that is used to store the
        result of the `get_ids` method. It allows the method to pass the `ids` variable to another part
        of the code for further processing or retrieval
        """
        ids = self.threat_system.get_threats_ids
        result_queue.put(ids)

    def actions(self, ship_state: Dict, game_state: Dict) -> Tuple[float, float, bool, bool]:
     # The `actions` function is a method that is called at each time step by a controller. It
     # determines the actions to be taken by a ship in a game based on the current ship state and game
     # state.

        # THIS VALUE IS HARD CODED DUE TO ME NOT BEING ABLE TO UNDERSTAND HOW TO GET IT
        # FROM KESSLERGAME
        deltatime = 1.0/30.0
        fire = False
        drop_mine = False
        turn_rate = 0
        thrust = 0
        new_turn_rate = 0
        asteroids = game_state['asteroids']
        self.threat_system.update(ship_state, game_state)

        ids = {}
        
        # Initialize a queue to store results
        result_queue = Queue()

        # Use ThreadPoolExecutor for concurrent execution in the ThreatSystem
        with ThreadPoolExecutor(max_workers=12, thread_name_prefix="ThreatSystem") as executor:
            # Submit a task to retrieve IDs asynchronously
            future = executor.submit(self.get_ids, result_queue)

        # Wait for the task to complete and retrieve the results
        future.result()
        ids = result_queue.get()

        # Close the result queue after processing
        result_queue.close()

        if len(self.threat_system.distances.keys()) > 0:
            first_index = list(self.threat_system.distances.keys())[0]
        else:
            first_index = 0
        


        # print(self.threat_system.distances)
        turn_rate = 0
        fire = False
        # print(f"ASTEROIDS: {len(asteroids)}",end='\r')
        # if len(ids) > 0 :

        shootingData = self.shoot.shoot_at(game_state["asteroids"][first_index],
                                            ship_state, first_index)
        # print(f"IDS: {self.threat_system.distances}")

        # INSERT FUZZY LOGIC HERE LATER, (SHOOT OR DODGE)

        # get the first index in the threat ids


        # if the action list is empty then try to append shooting action
        if (self.action_list.is_empty()):
            self.action_list.take_action(action_type.Shoot, first_index)

        # get shooting data based on action

        # get current action asteroid ID
        ID = self.action_list.get_current_action_id()
        # The line `print(ID, self.threat_system.distances)` is printing the ID of the current
        # action asteroid and the distances of all threats from the ship. It is used for debugging
        # purposes to check the values of these variables during the execution of the code.
        # print(ID, self.threat_system.distances)

        

        dodgingData = self.dodge.take_action(
            ship_state, asteroids, self.threat_system.distances, ids)
        
        # print("DODGING: " , dodgingData[2])
        # if data returned then turn
        if (shootingData):
            # print("TARGET FOUND: ", ID)
            # print("POS: ", (game_state["asteroids"][ID])["position"])
            # print("SHOOTING DATA: ", shootingData[0])
            # if not dodgingData[2]:
            if not dodgingData[2]:
                new_turn_rate += shootingData[0]

            fire = shootingData[1]

            if (shootingData[1]):
                self.action_list.finish_current_action()

        # COMMENT OUT DODGE ALGORITHM UNTIL I CAN ADJUST IT FOR ACTION LIST
        if (dodgingData):
            # if (dodgingData[2] == False):
            self.action_list.take_action(action_type.Dodge, ID)
            thrust = dodgingData[0] 
            
            new_turn_rate += dodgingData[1] / 2
                
                
            if (dodgingData[2]):
                self.action_list.finish_current_action()
            # else:
            #     if not (self.action_list.is_empty()):
            #         self.action_list.finish_current_action()


        if new_turn_rate > 180:
            new_turn_rate = 180
        elif new_turn_rate < -180:
            new_turn_rate = -180

        turn_rate = new_turn_rate
        # print("TURN RATE: ", turn_rate)
        '''new_thrust, dodge_turn_rate = self.dodge.update(
            ship_state, asteroids, ids.keys())

        for key, value in ids.items():
            self.pathFinding.path_find(
                asteroids[key], ship_state, key)

            # print(self.pathFinding(key).collision)
            if self.pathFinding(key).collision:
                self.dodge.take_action(
                    asteroids[key], ship_state, key, ids.keys())

            

            
            if new_thrust == 0:          
                thrust = 0
            else:
                thrust = 0
                thrust += new_thrust'''

        # no threats, just shoot random asteroid
        # else:
            # # use triangle_find to find asteroids in direction
            # facingAsteroids = self.idle.triangle_find(game_state["asteroids"])
            

            # # if found any loop through shoot first in list
            # # if (facingAsteroids):
            # #     # if action list is empty
            # #     if (self.action_list.is_empty()):
            # #         # loop through every asteroid in list (will break on certain condition)
            # #         for i in range(len(facingAsteroids)):
            #             # get shooting data
            # shootingData = self.shoot.shoot_at(game_state["asteroids"][facingAsteroids[first_index]], ship_state,
            #                                     facingAsteroids[first_index])

            # # if there is valid information
            # if (shootingData):
            #     # take action
            #     self.action_list.take_action(
            #         action_type.Shoot, facingAsteroids[first_index])
            #     # set shooting data
            #     turn_rate = shootingData[0] * 10
            #     fire = shootingData[1]

            #     # if can shoot immedietly then finish action
            #     if (shootingData[1]):
            #         self.action_list.finish_current_action()
            #                 # break

            # # if action list is not empty
            # else:
            #     # get current action asteroid ID
            #     ID = self.action_list.get_current_action_id()

            #     # get shootingdata of that asteroid
            #     shootingData = self.shoot.shoot_at(
            #         game_state["asteroids"][ID], ship_state, ID)
            #     if (shootingData):
            #         turn_rate = shootingData[0] * 10
            #         fire = shootingData[1]

            #         if (shootingData[1]):
            #             self.action_list.finish_current_action()

            # else:
            #     # else just idly turn
            #     turn_rate = 100
            #     thrust = 10

        self.idle.update(ship_state)
        self.shoot.update(deltatime)
        self.threat_system.distances = {}

        self.eval_frames += 1
        # turn_rate = 0
        # thrust = 0
        
        '''
        turn_rate = 0
        thrust = 1000
        drop_mine = True
        '''
        # fire = False

        return thrust, turn_rate, fire, drop_mine

    @property
    def name(self) -> str:
        return "Fuzzifiers"

