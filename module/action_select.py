'''
Filename: action_select
Author: David Mann (david.mann@digipen.edu)

'''
from state import State
from typing import Dict
import numpy as np
import skfuzzy as fuzz
from skfuzzy import control as ctrl 

class AsteroidFits:
    def __init__(self) -> None:
        self.distance
        self.turn_angle
        self.angle_to_ship
    

def State_Fit(state:State):

    '''
    rules 
    -1 = dodge
    0 = idle 
    1 = shoot

    small turn_angle = shoot
    close distance + small angle_to_ship = dodge
    far distance + high turn_angle = idle

    highest absolute value = target
    '''

    asteroid1:AsteroidFits
    asteroid2:AsteroidFits
    asteroid3:AsteroidFits


    asteroid1.distance = ctrl.Antecedent
    asteroid2.distance = ctrl.Antecedent
    asteroid3.distance = ctrl.Antecedent

    asteroid1.turn_angle = ctrl.Antecedent(np.arange(-180, 180, 1), "turn angle1")
    asteroid2.turn_angle = ctrl.Antecedent(np.arange(-180, 180, 1), "turn angle2")
    asteroid3.turn_angle = ctrl.Antecedent(np.arange(-180, 180, 1), "turn angle3")

    asteroid1.angle_to_ship = ctrl.Antecedent(np.arange(-180, 180, 1), "ship path1")
    asteroid2.angle_to_ship = ctrl.Antecedent(np.arange(-180, 180, 1), "ship path2")
    asteroid3.angle_to_ship = ctrl.Antecedent(np.arange(-180, 180, 1), "ship path3")

    

    state.asteroids[0]

def Action_Select(state: State):

