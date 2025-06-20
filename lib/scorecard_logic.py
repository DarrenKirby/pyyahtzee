"""
Defines the core scorecard logic for Yahtzee game, independent of any UI.
"""
from typing import Dict, List, Optional, Set, Tuple


class ScorecardLogic:
    """
    Core scorecard logic which keeps track of player scores and scoring calculations
    """

    def __init__(self, player_name: str):
        self.player_name = player_name
        self.has_upper_bonus = False
        self.upper_bonus_counted = False
        self.upper_cats = ['Ones', 'Twos', 'Threes', 'Fours', 'Fives', 'Sixes']
        self.upper_sub = 0
        self.lower_cats = ['Three of a Kind', 'Four of a Kind', 'Full House',
                           'Small Straight', 'Large Straight', 'Yahtzee', 'Chance']
        self.lower_sub = 0
        self.scores: Dict[str, Optional[int]] = {
            category: None for category in self.upper_cats + self.lower_cats
        }
        # Keep track of dice throws for display purposes
        self.throws: Dict[str, Optional[List[int]]] = {
            category: None for category in self.upper_cats + self.lower_cats
        }
        self.total_score =.0
        self.plus_minus = 0
        self.yahtzee_bonus = 0
        
    def calculate_score(self, dice_values: List[int], category: Optional[str]) -> int:
        """
        A pure function which takes a list of dice values and a category, and returns the score.
        """
        if not category:
            return 0
            
        counts = [dice_values.count(i) for i in range(1, 7)]
        sorted_dice = sorted(dice_values)
        
        if category in ['Ones', 'Twos', 'Threes', 'Fours', 'Fives', 'Sixes']:
            category_value = self.upper_cats.index(category) + 1
            return category_value * dice_values.count(category_value)
            
        if category == 'Three of a Kind':
            return sum(dice_values) if any(count >= 3 for count in counts) else 0
            
        if category == 'Four of a Kind':
            return sum(dice_values) if any(count >= 4 for count in counts) else 0
            
        if category == 'Full House':
            return 25 if 2 in counts and 3 in counts else 0
            
        if category == 'Small Straight':
            return 30 if any(
                {x, x + 1, x + 2, x + 3}.issubset(set(sorted_dice)) for x in range(1, 4)
            ) else 0
            
        if category == 'Large Straight':
            return 40 if sorted_dice == [1, 2, 3, 4, 5] or sorted_dice == [2, 3, 4, 5, 6] else 0
            
        if category == 'Yahtzee':
            return 50 if any(count == 5 for count in counts) else 0
            
        # 'Chance' or any other category
        return sum(dice_values)
        
    def calc_plus_minus_str(self) -> str:
        """
        Calculates the 'plus/minus' on the upper bonus, and returns in string form.
        """
        if self.plus_minus == 0:
            return 'even'
        if self.plus_minus > 0:
            return f'up {self.plus_minus}'
        return f'down {abs(self.plus_minus)}'
        
    def _calc_plus_minus(self, category: str, score: int) -> None:
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
        
    def is_category_used(self, category: str) -> bool:
        """
        Checks if a category has already been used
        """
        return self.scores[category] is not None
        
    def update_score(self, dice_values: List[int], category: str) -> None:
        """
        Updates the score attached to a category, and updates the subtotals.
        """
        # Don't update if category already has a score
        if self.scores[category] is not None:
            return
            
        # Handle Yahtzee bonus and joker rules
        if len(set(dice_values)) == 1 and self.scores['Yahtzee']:
            # We have an additional yahtzee
            if self.scores['Yahtzee'] > 0:
                # Yahtzee has not been scratched
                self.yahtzee_bonus += 1
                
                # Store the true dice for display
                true_dice = sorted(dice_values.copy())
                
                # For 'Joker' categories we just modify the dice values
                # to an appropriate value so the scoring logic works correctly
                if category == 'Full House':
                    self.throws[category] = true_dice
                    dice_values = [1, 1, 2, 2, 2]
                elif category == 'Small Straight':
                    self.throws[category] = true_dice
                    dice_values = [1, 2, 3, 4, 6]
                elif category == 'Large Straight':
                    self.throws[category] = true_dice
                    dice_values = [1, 2, 3, 4, 5]
                    
                # Add Yahtzee bonus
                self.yahtzee_bonus += 1
                self.lower_sub += 100

        # Store the dice values for display purposes
        if self.throws[category] is None:
            self.throws[category] = sorted(dice_values)
            
        # Calculate and store the score
        score = self.calculate_score(dice_values, category)
        self.scores[category] = score
        
        # Update subtotals
        if category in self.upper_cats:
            self._calc_plus_minus(category, score)
            self.upper_sub += score
        elif category in self.lower_cats:
            self.lower_sub += score
            
        # Check for upper bonus
        if not self.upper_bonus_counted and self.upper_sub >= 63:
            self.has_upper_bonus = True
            self.upper_bonus_counted = True
            self.upper_sub += 35
            
        # Tally total score
        self.total_score = self.upper_sub + self.lower_sub
        
    def final_tally(self) -> int:
        """
        Returns the final score.
        """
        return self.total_score
        
    def get_all_categories(self) -> List[str]:
        """
        Returns all categories
        """
        return self.upper_cats + self.lower_cats
