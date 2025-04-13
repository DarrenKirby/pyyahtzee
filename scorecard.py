"""
Defines the Scoreboard() class which tracks and displays a players score.
"""
from typing import Dict
import pygame
from common import SCREEN, BLACK, WIDTH, HEIGHT, WHITE, FONT, int_to_mini_die


class Scorecard:
    """
    Scorecard class which keeps track of player scores, draws them to the screen,
    detects category selection, and scores a turn.
    """

    def __init__(self, x: int, y: int, player_name: str):
        self.x = x
        self.y = y
        self.player_name = player_name
        self.u_bonus = False
        self.upper_bonus_counted = False
        self.upper_cats = ['Ones', 'Twos', 'Threes', 'Fours', 'Fives', 'Sixes']
        self.upper_sub = 0
        self.lower_cats = ['Three of a Kind', 'Four of a Kind', 'Full House',
                           'Small Straight', 'Large Straight', 'Yahtzee', 'Chance']
        self.lower_sub = 0
        self.scores: Dict[str, int | None]
        self.scores = {category: None for category in self.upper_cats + self.lower_cats}
        self.throws: Dict[str, list[int] | None]
        self.throws = {category: None for category in self.upper_cats + self.lower_cats}
        self.total_score = 0
        self.plus_minus = 0
        self.yahtzee_bonus = 0

    def final_tally(self) -> int:
        """
        Returns the final score.
        """
        return self.total_score

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
        text = name_font.render(self.player_name, True, BLACK)
        SCREEN.blit(text, (self.x, self.y - 60))

        # Print total score
        text = name_font.render(str(self.total_score), True, BLACK)
        SCREEN.blit(text, (self.x + 575, self.y - 60))
        # Print score for each category
        for i, (category, score) in enumerate(self.scores.items()):
            category_text = FONT.render(category, True, WHITE)
            score_text = FONT.render(str(score) if score is not None else "-", True, WHITE)
            SCREEN.blit(category_text, (self.x, self.y + i * 40))
            SCREEN.blit(score_text, (self.x + 200, self.y + i * 40))
            # Print the 'mini dice'
            if score is not None:
                x = self.x + 400
                # noinspection PyTypeChecker
                for idx, n in enumerate(self.throws[category]):
                    SCREEN.blit(int_to_mini_die[n], (x + idx * 40, self.y + i * 40))

        sub_text = f"Upper section subtotal: {self.upper_sub}  (+/- {self.__calc_plus_minus_s()})"
        t = FONT.render(sub_text, True, BLACK)
        SCREEN.blit(t, (self.x, self.y + 530))
        sub_text = f"Lower section subtotal: {self.lower_sub}"
        t = FONT.render(sub_text, True, BLACK)
        SCREEN.blit(t, (self.x, self.y + 560))

    def is_clicked(self, pos: tuple[int, int], category: str) -> bool:
        """
        Returns true when a category is clicked.
        """
        index = list(self.scores.keys()).index(category)
        cond1 = self.x < pos[0] < self.x + 300
        cond2 = self.y + index * 40 < pos[1] < self.y + (index + 1) * 40
        return cond1 and cond2

    def calculate_score(self, dice_values: list, category: str | None) -> int:
        """
        A pure function which takes a list of dice values and a category, and returns the score.
        """
        counts = [dice_values.count(i) for i in range(1, 7)]
        dice_values = sorted(dice_values)
        if category in ['Ones', 'Twos', 'Threes', 'Fours', 'Fives', 'Sixes']:
            return dice_values.count(list(self.scores.keys()).index(category) + 1) * (
                    list(self.scores.keys()).index(category) + 1)
        if category == 'Three of a Kind':
            return sum(dice_values) if any(count >= 3 for count in counts) else 0
        if category == 'Four of a Kind':
            return sum(dice_values) if any(count >= 4 for count in counts) else 0
        if category == 'Full House':
            return 25 if 2 in counts and 3 in counts else 0
        if category == 'Small Straight':
            return 30 if any(
                {x, x + 1, x + 2, x + 3}.issubset(set(dice_values)
                                                  ) for x in range(1, 4)) else 0
        if category == 'Large Straight':
            return 40 if dice_values == [1, 2, 3, 4, 5] or dice_values == [2, 3, 4, 5, 6] else 0
        if category == 'Yahtzee':
            return 50 if any(count == 5 for count in counts) else 0
        # 'Chance':
        return sum(dice_values)

    def __calc_plus_minus_s(self) -> str:
        """
        Calculates the 'plus/minus' on the upper bonus, and returns in string form.
        """
        if self.plus_minus == 0:
            return 'even'
        if self.plus_minus > 0:
            return f'up {self.plus_minus}'
        return f'down {abs(self.plus_minus)}'

    def __calc_plus_minus_n(self, category: str, score: int) -> None:
        """
        Calculates the 'plus/minus' and assigns to an instance variable.
        """
        par = {
            'Ones': 3,
            'Twos': 6,
            'Threes': 9,
            'Fours': 12,
            'Fives': 15,
            'Sixes': 18
        }
        self.plus_minus += (score - par[category])

    def update_score(self, dice_values: list, category: str) -> None:
        """
        Updates the score attached to a category, and updates the subtotals.
        """
        if (len(set(dice_values)) == 1) and (self.scores['Yahtzee']):
            # We have an additional yahtzee
            if not self.scores['Yahtzee'] == 0:
                # Yahtzee has not been scratched
                self.yahtzee_bonus += 1
                # For 'Joker' categories we just modify the dice values
                # to an appropriate value so that program control can
                # flow to the scoring block below. However, we keep the
                # true dice values for the 'mini dice' output.
                if category == 'Full House':
                    # Pycharm bug makes this necessary
                    # noinspection PyTypeChecker
                    self.throws[category] = sorted(dice_values)
                    dice_values = [1, 1, 2, 2, 2]
                elif category == 'Small Strait':
                    # Pycharm bug makes this necessary
                    # noinspection PyTypeChecker
                    self.throws[category] = sorted(dice_values)
                    dice_values = [1, 2, 3, 4, 6]
                elif category == 'Large Straight':
                    # Pycharm bug makes this necessary
                    # noinspection PyTypeChecker
                    self.throws[category] = sorted(dice_values)
                    dice_values = [1, 2, 3, 4, 5]
                # Add Yahtzee bonus
                self.yahtzee_bonus += 1
                self.lower_sub += 100

        if self.scores[category] is None:
            if self.throws[category] is None:
                # Pycharm bug makes this necessary
                # noinspection PyTypeChecker
                self.throws[category] = sorted(dice_values)
            score = self.calculate_score(dice_values, category)
            # Pycharm bug makes this necessary
            # noinspection PyTypeChecker
            self.scores[category] = score
            # Update upper and lower subtotals
            if category in self.upper_cats:
                self.__calc_plus_minus_n(category, score)
                self.upper_sub += score
            if category in self.lower_cats:
                self.lower_sub += score
            # Check for upper bonus
            if not self.upper_bonus_counted:
                if self.upper_sub >= 63:
                    self.u_bonus = True
                    self.upper_bonus_counted = True
                    self.upper_sub += 35
            # Tally total score
            self.total_score = self.upper_sub + self.lower_sub
