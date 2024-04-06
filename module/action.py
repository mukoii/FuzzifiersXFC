'''
Filename: Action
Author: Nathan D (nathan.delcampo@digipen.edu)
Date: 10/15/23

Desc: Class for keeping track of the types of actions

'''
from enum import Enum


# The class "action_type" defines two enum values, "Shoot" and "Dodge".
class action_type(Enum):
    Shoot = "Shoot"
    Dodge = "Dodge"

# The `Action` class stores the type of action being taken and the asteroid on which the action is
# being performed.


class Action:
    def __init__(self, action: action_type, asteroid):
        # store the type of action and on what asteroid said action is being taken on
        self.actionType = action
        self.ID = asteroid
