'''
Filename: ActionList
Author: Nathan D (nathan.delcampo@digipen.edu)
Date: 10/15/23

Desc: Class for keeping track of current list of actions being taken
      by the ship

'''
from kesslergame import KesslerController
from typing import Dict, Tuple
from module.action import Action, action_type


class ActionList:
    """
    Desc: The ActionList class represents a list of actions to be taken, where each action is associated
            with an asteroid ID and can be marked as urgent or not.
    """
    def __init__(self):
        self.actions = []  # list of actions to take
        # should contain asteroid id and action to take

    def take_action(self, action: action_type, ID, urgent=False):
        '''Adds a action to the end of the action list

        Args:
            action (action_type): An enum denoting the action to be taken
            ID (int): An integer denoting the index of the asteroid in the asteroid list
            actionData (tuple): A tuple containing the data for said action,
            EX: Shoot (turn_rate, bool), dodge (turn_rate, thrust, etc)
            urgent (bool): A flag that sets the action as important or not, auto false

        Returns:
            length (int): the current length of the list and therefore the place int the action queue
            -1 if the action was already in the list
        '''
        # create action
        action = Action(action, ID)

        # check if action is already in list
        if (action in self.actions):
            print("ACTION ALREADY IN LIST")
            return -1

        if (urgent):
            # insert at beginning
            self.actions.insert(0, action)
            return 0
        else:
            # append normally
            self.actions.append(action)
            return len(self.actions)

    def finish_current_action(self):
        '''Pops the first action from the action list if exists,
           does nothing if first doesnt exist.

        Args: N/A

        Returns:
            Error Code (int): 1 if successful, -1 if not successful or nothing to pop
        '''
        if (self.actions[0]):
            self.actions.pop(0)
            return 1
        return -1

    def get_current_action(self):
        '''Returns the current action being taken (first in list)

        Args: N/A

        Returns:
            Action of the asteroid
        '''
        if (self.actions[0]):
            return self.actions[0]
        else:
            return None

    def get_current_action_id(self):
        '''Returns the current action being taken (first in list)

        Args: N/A

        Returns:
            Action of the asteroid
        '''
        if (self.actions[0]):
            return self.actions[0].ID
        else:
            return None

    def is_empty(self):
        '''Returns a bool depending on the state of the action list

        Args: N/A

        Returns:
            Bool
        '''
        if not self.actions:
            return True
        else:
            return False
