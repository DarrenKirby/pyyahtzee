"""
UI components for scorecard visualization
"""
import pygame
from typing import Optional, Tuple
from .scorecard_logic import ScorecardLogic
from .ui_common import SCREEN, BLACK, WIDTH, HEIGHT, WHITE, FONT, int_to_mini_die


class ScorecardUI:
    """
    Visual representation of a scorecard
    """

    def __init__(self, x: int, y: int, scorecard_logic: ScorecardLogic):
        self.x = x
        self.y = y
        self.scorecard_logic = scorecard_logic
        # Keep track of rectangles for hit detection
        self.category_rects = {}

    def draw(self) -> None:
        """
        Draws a scorecard to the screen.
        """
        # Draw horizontal lines
        pygame.draw.line(SCREEN, BLACK, (0, self.y - 75), (WIDTH, self.y - 75), 10)
        pygame.draw.line(SCREEN, BLACK, (0, self.y - 10), (WIDTH, self.y - 10), 5)
        pygame.draw.line(SCREEN, BLACK, (0, self.y + 520), (WIDTH, self.y + 520), 5)

        # Draw vertical line
        pygame.draw.line(SCREEN, BLACK, (725, self.y - 75), (725, HEIGHT), 10)

        # Print player name
        name_font = pygame.font.SysFont("Arial", 36)
        text = name_font.render(self.scorecard_logic.player_name, True, BLACK)
        SCREEN.blit(text, (self.x, self.y - 60))

        # Print total score
        text = name_font.render(str(self.scorecard_logic.total_score), True, BLACK)
        SCREEN.blit(text, (self.x + 575, self.y - 60))

        # Print score for each category
        for i, category in enumerate(self.scorecard_logic.scores):
            score = self.scorecard_logic.scores[category]
            category_text = FONT.render(category, True, WHITE)
            score_text = FONT.render(str(score) if score is not None else "-", True, WHITE)

            # Store the rectangle for this category for hit detection
            category_rect = pygame.Rect(self.x, self.y + i * 40, 300, 40)
            self.category_rects[category] = category_rect

            # Draw the category and score
            SCREEN.blit(category_text, (self.x, self.y + i * 40))
            SCREEN.blit(score_text, (self.x + 200, self.y + i * 40))

            # Print the 'mini dice'
            if score is not None and self.scorecard_logic.throws[category] is not None:
                x = self.x + 400
                for idx, n in enumerate(self.scorecard_logic.throws[category]):
                    SCREEN.blit(int_to_mini_die[n], (x + idx * 40, self.y + i * 40))

        # Draw subtotals
        sub_text = f"Upper section subtotal: {self.scorecard_logic.upper_sub}  (+/- {self.scorecard_logic.calc_plus_minus_str()})"
        t = FONT.render(sub_text, True, BLACK)
        SCREEN.blit(t, (self.x, self.y + 530))

        sub_text = f"Lower section subtotal: {self.scorecard_logic.lower_sub}"
        t = FONT.render(sub_text, True, BLACK)
        SCREEN.blit(t, (self.x, self.y + 560))

    def is_category_clicked(self, pos: Tuple[int, int], category: str) -> bool:
        """
        Checks if a category was clicked
        """
        if category in self.category_rects:
            return self.category_rects[category].collidepoint(pos)
        return False
