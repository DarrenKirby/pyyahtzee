"""
Defines class Button() which prints a text button to the screen.
"""
import pygame
from .ui_common import BLUE, DARK_GRAY, SCREEN, DARK_BLUE, LIGHT_GRAY, WHITE, FONT


class Button:
    """
    A button class responsible for drawing a button, and tracking state.
    """

    def __init__(self, pos: tuple[int, int], size: tuple[int, int], text: str):
        self.x, self.y = pos
        self.width, self.height = size
        self.text = text
        self.color = BLUE
        self.shadow_color = DARK_GRAY
        self.pressed = False

    def draw(self, m_pos: tuple[int, int]) -> None:
        """
        Draws a button to the supplied position.
        """
        x_offset, y_offset = (2, 2) if not self.pressed else (0, 0)

        # Draw shadow
        pygame.draw.rect(SCREEN,
                         self.shadow_color,
                         (self.x + 4, self.y + 4, self.width, self.height),
                         border_radius=8)

        # Draw button (change color if hovered)
        button_color = DARK_BLUE if self.pressed \
            else (LIGHT_GRAY if self.is_hovered(m_pos) else self.color)
        pygame.draw.rect(SCREEN, button_color,
                         (self.x + x_offset, self.y + y_offset, self.width, self.height),
                         border_radius=8)

        # Render text
        text_surface = FONT.render(self.text, True, WHITE)
        text_rect = text_surface.get_rect(
            center=(self.x + self.width // 2 + x_offset, self.y + self.height // 2 + y_offset)
        )
        SCREEN.blit(text_surface, text_rect)

    def is_hovered(self, m_pos: tuple[int, int]):
        """
        Returns boolean indicating if the button is being hovered on.
        """
        return (self.x <= m_pos[0] <= self.x +
                self.width and self.y <= m_pos[1] <= self.y + self.height)

    def handle_event(self, event: pygame.event.Event, m_pos: tuple[int, int]) -> bool:
        """
        Returns true if the button was pressed.
        """
        if event.type == pygame.MOUSEBUTTONDOWN and self.is_hovered(m_pos):
            self.pressed = True
        elif event.type == pygame.MOUSEBUTTONUP:
            if self.pressed and self.is_hovered(m_pos):
                self.pressed = False
                return True
            self.pressed = False
        return False
