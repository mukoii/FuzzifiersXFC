# -*- coding: utf-8 -*-

from typing import Dict, Tuple
from kesslergame import KesslerController
import math
import threading
import time
import keyboard


class KeyboardController(KesslerController):

    def __init__(self):
        pass

    def actions(self, ship_state: Dict, game_state: Dict) -> Tuple[float, float, bool, bool]:
        """
        Read in the current gamepad state, and create the appropriate actions
        """

        thrust = 0
        turn_rate = 0
        fire = False
        drop_mine = False

        if keyboard.is_pressed("W"):
            thrust = 200
        if keyboard.is_pressed("S"):
            thrust = -200

        if keyboard.is_pressed("D"):
            turn_rate = -90
        if keyboard.is_pressed("A"):
            turn_rate = 90

        if keyboard.is_pressed("SPACE"):
            fire = True

        return thrust, turn_rate, fire, drop_mine

    @property
    def name(self) -> str:
        return "Keyboard Controller"



