"""
Core game logic for Yahtzee, independent of any UI.
"""
from typing import List, Dict, Optional, Tuple
import os
from .dice_logic import DiceLogic
from .scorecard_logic import ScorecardLogic

# Maximum number of rounds in a game
MAX_ROUNDS = 13
# High score file
HS_FILE = "high_score.txt"


class YahtzeeGame:
    """
    Core game logic for Yahtzee
    """
    
    def __init__(self):
        self.player1_name = ""
        self.player2_name = ""
        self.player1_scorecard: Optional[ScorecardLogic] = None
        self.player2_scorecard: Optional[ScorecardLogic] = None
        self.current_round = 0
        self.high_scores: List[Tuple[int, str, str]] = []
        self.active_dice = DiceLogic()
        self.read_high_scores()
    
    def setup_new_game(self, player1_name: str, player2_name: str) -> None:
        """
        Set up a new game with player names
        """
        self.player1_name = player1_name
        self.player2_name = player2_name
        self.player1_scorecard = ScorecardLogic(player1_name)
        self.player2_scorecard = ScorecardLogic(player2_name)
        self.current_round = 0
        self.active_dice = DiceLogic()
    
    def reset_turn(self) -> None:
        """
        Reset dice for a new turn
        """
        self.active_dice.reset()
    
    def is_game_over(self) -> bool:
        """
        Check if the game is over
        """
        return self.current_round >= MAX_ROUNDS
    
    def next_round(self) -> None:
        """
        Advance to the next round
        """
        self.current_round += 1
    
    def get_winner(self) -> Tuple[str, int, int]:
        """
        Returns the winner's name and both scores
        """
        if not self.player1_scorecard or not self.player2_scorecard:
            return ("No game in progress", 0, 0)
        
        p1_score = self.player1_scorecard.final_tally()
        p2_score = self.player2_scorecard.final_tally()
        
        if p1_score > p2_score:
            return (self.player1_name, p1_score, p2_score)
        else:
            return (self.player2_name, p2_score, p1_score)
    
    def process_turn_ai(self, scorecard: ScorecardLogic) -> str:
        """
        Process an AI turn and return the chosen category
        """
        # Roll the dice
        self.active_dice.roll_dice()
        self.active_dice.rolls_left -= 1
        
        # Roll up to 3 times
        while self.active_dice.rolls_left > 0:
            # Simple strategy: hold dice with the most common value
            counts: Dict[int, int] = {}
            for die in self.active_dice.rolled:
                counts[die] = counts.get(die, 0) + 1
                
            common_value, _ = max(counts.items(), key=lambda x: x[1])
            
            for i, die in enumerate(self.active_dice.rolled):
                self.active_dice.set_hold(i, die == common_value)
                
            # Roll dice if rolls are still available
            self.active_dice.roll_dice()
            self.active_dice.rolls_left -= 1
            
        # After rolling, choose the best scoring category
        best_category = ""
        best_score = -1
        
        for category in scorecard.get_all_categories():
            if not scorecard.is_category_used(category):
                score = scorecard.calculate_score(self.active_dice.rolled, category)
                if score > best_score:
                    best_score = score
                    best_category = category
        
        # Update the scorecard with the chosen category
        scorecard.update_score(self.active_dice.rolled, best_category)
        
        return best_category
    
    def read_high_scores(self) -> None:
        """
        Read high scores from a file
        """
        self.high_scores = []
        try:
            if os.path.exists(HS_FILE):
                with open(HS_FILE, 'r', encoding='utf-8') as f:
                    for line in f:
                        items = line.strip().split(",")
                        if len(items) >= 3:
                            self.high_scores.append((int(items[0]), items[1], items[2]))
        except (IOError, ValueError) as e:
            print(f"Could not read from high score file: {e}")
    
    def write_high_scores(self) -> None:
        """
        Write the top 10 high scores to a file
        """
        # Add current game scores if available
        if self.player1_scorecard and self.player2_scorecard:
            p1_score = self.player1_scorecard.final_tally()
            p2_score = self.player2_scorecard.final_tally()
            self.high_scores.append((p1_score, self.player1_name, self.player2_name))
            self.high_scores.append((p2_score, self.player2_name, self.player1_name))
        
        # Sort and write top 10
        sorted_scores = sorted(self.high_scores, reverse=True)
        try:
            with open(HS_FILE, 'w', encoding='utf-8') as f:
                for score in sorted_scores[:10]:
                    line = f"{score[0]},{score[1]},{score[2]}\n"
                    f.write(line)
        except IOError as e:
            print(f"Could not write to high score file: {e}")
    
    def get_sorted_high_scores(self, limit: int = 10) -> List[Tuple[int, str, str]]:
        """
        Get sorted high scores
        """
        return sorted(self.high_scores, reverse=True)[:limit]
