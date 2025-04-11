"""
Defines the Dice() class responsible for rolling and displaying dice
"""
from random import randint
import pygame
from common import SCREEN, POOL_TABLE_GREEN, RED, pause, i_to_d


class Dice:
    """
    A dice class which implements random throwing and keeps track
    of dice state. The draw method maps the dice values to dice
    images and displays them on the screen.
    """

    def __init__(self):
        # List to hold the current dice values
        self.rolled = []
        # Dictionary to hold the rects and selection state for each die.
        # Uses keys 1-5. Each value is [rect, selected_bool]
        self.slots = {}
        self.rolls_left = 3

    def roll_dice(self) -> None:
        """
        Rolls dice. If this is the first roll, fill self.rolled with 5 dice;
        otherwise, re-roll only dice that aren't selected.
        """
        # First roll: initialize all dice
        if not self.rolled:
            self.rolled = [randint(1, 6) for _ in range(5)]
        else:
            # For subsequent rolls, replace dice that aren't selected.
            # Note: keys in slots are 1-indexed, so dice i is at index i-1.
            for i in range(5):
                if i + 1 not in self.slots or not self.slots[i + 1][1]:
                    self.rolled[i] = randint(1, 6)

    def animate_roll(self) -> None:
        """
        Sequentially draws newly rolled dice to the screen.
        """
        pygame.draw.rect(SCREEN, POOL_TABLE_GREEN, [535, 95, 360, 80])
        pygame.display.flip()
        d_pos = {
            1: (540, 100),
            2: (610, 100),
            3: (680, 100),
            4: (750, 100),
            5: (820, 100)
        }

        new_slots = {}
        for i, die in enumerate(self.rolled):
            # Preserve selection state if already exists; otherwise default to False.
            if i + 1 in self.slots:
                new_slots[i + 1] = [None, self.slots[i + 1][1], die]
            else:
                new_slots[i + 1] = [None, False, die]
        # Update slots to the new dictionary.
        self.slots = new_slots

        for k, v in self.slots.items():
            if v[1]:
                rect = SCREEN.blit(i_to_d[v[2]], d_pos[k])
                v[0] = rect
                pygame.draw.rect(SCREEN, RED, rect, 5)
        pygame.display.flip()
        for k, v in self.slots.items():
            if not v[1]:
                pause(1000)
                rect = SCREEN.blit(i_to_d[v[2]], d_pos[k])
                v[0] = rect
                pygame.display.flip()

    def draw(self) -> None:
        """
        Draws the dice to the screen without animation.
        """
        pygame.draw.rect(SCREEN, POOL_TABLE_GREEN, [535, 95, 360, 80])
        x = 540
        new_slots = {}
        for i, die in enumerate(self.rolled):
            # Draw the die and get its rect.
            rect = SCREEN.blit(i_to_d[die], (x, 100))
            # Preserve selection state if already exists; otherwise default to False.
            if i + 1 in self.slots:
                new_slots[i + 1] = [rect, self.slots[i + 1][1]]
            else:
                new_slots[i + 1] = [rect, False]
            x += 70
        # Update slots to the new dictionary.
        self.slots = new_slots
