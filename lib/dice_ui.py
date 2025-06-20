"""
UI components for dice visualization
"""
import pygame
from .dice_logic import DiceLogic
from .ui_common import SCREEN, POOL_TABLE_GREEN, RED, int_to_die, pause


class DiceUI:
    """
    Visual representation of dice
    """
    
    def __init__(self, dice_logic: DiceLogic):
        self.dice_logic = dice_logic
        # Dictionary to hold the rects for each die
        self.dice_rects = [None] * 5
        # Standard positions for drawing dice
        self.positions = [
            (540, 100),
            (610, 100),
            (680, 100),
            (750, 100),
            (820, 100)
        ]
    
    def draw(self) -> None:
        """
        Draws the dice to the screen without animation
        """
        # Clear previous dice area
        pygame.draw.rect(SCREEN, POOL_TABLE_GREEN, [535, 95, 360, 80])
        
        # Draw each die
        for i, die_value in enumerate(self.dice_logic.rolled):
            if i < len(self.positions):
                rect = SCREEN.blit(int_to_die[die_value], self.positions[i])
                self.dice_rects[i] = rect
                
                # Draw selection border if the die is held
                if self.dice_logic.held[i]:
                    pygame.draw.rect(SCREEN, RED, rect, 5)
    
    def animate_roll(self) -> None:
        """
        Sequentially draws newly rolled dice to the screen with animation
        """
        # Clear the dice area
        pygame.draw.rect(SCREEN, POOL_TABLE_GREEN, [535, 95, 360, 80])
        pygame.display.flip()
        
        # First draw the held dice
        for i, (die_value, is_held) in enumerate(zip(self.dice_logic.rolled, self.dice_logic.held)):
            if is_held:
                rect = SCREEN.blit(int_to_die[die_value], self.positions[i])
                self.dice_rects[i] = rect
                pygame.draw.rect(SCREEN, RED, rect, 5)
        
        pygame.display.flip()
        
        # Then animate the non-held dice
        for i, (die_value, is_held) in enumerate(zip(self.dice_logic.rolled, self.dice_logic.held)):
            if not is_held:
                pause(1000)
                rect = SCREEN.blit(int_to_die[die_value], self.positions[i])
                self.dice_rects[i] = rect
                pygame.display.flip()
    
    def get_die_at_pos(self, pos: tuple[int, int]) -> int:
        """
        Returns the index of the die at the given position, or -1 if none
        """
        for i, rect in enumerate(self.dice_rects):
            if rect and rect.collidepoint(pos):
                return i
        return -1
