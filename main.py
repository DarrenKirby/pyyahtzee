"""
Main entry point for the Yahtzee game
"""
import pygame
from lib.game_ui import YahtzeeUI

# Initialize pygame
pygame.init()

if __name__ == "__main__":
    # Start the game UI
    YahtzeeUI()
