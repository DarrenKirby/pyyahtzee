"""
Defines the core dice logic for Yahtzee game, independent of any UI.
"""
from random import randint
from typing import List, Dict, Tuple, Any


class DiceLogic:
    """
    Core dice logic responsible for rolling and tracking dice state
    """

    def __init__(self):
        # List to hold the current dice values (1-6)
        self.rolled: List[int] = []
        # Whether each die is held (True) or not (False)
        self.held: List[bool] = [False] * 5
        # Remaining rolls in this turn
        self.rolls_left = 3

    def roll_dice(self) -> None:
        """
        Rolls dice. If this is the first roll, generate 5 dice values;
        otherwise, re-roll only dice that aren't held.
        """
        # First roll: initialize all dice
        if not self.rolled:
            self.rolled = [randint(1, 6) for _ in range(5)]
        else:
            # For subsequent rolls, replace dice that aren't held
            for i in range(5):
                if not self.held[i]:
                    self.rolled[i] = randint(1, 6)

    def toggle_hold(self, die_index: int) -> None:
        """
        Toggle whether a die is held or not
        """
        if 0 <= die_index < 5:  # Ensure index is valid
            self.held[die_index] = not self.held[die_index]

    def set_hold(self, die_index: int, held: bool) -> None:
        """
        Set whether a die is held or not
        """
        if 0 <= die_index < 5:  # Ensure index is valid
            self.held[die_index] = held

    def reset(self) -> None:
        """
        Resets the dice for a new turn
        """
        self.rolled = []
        self.held = [False] * 5
        self.rolls_left = 3
