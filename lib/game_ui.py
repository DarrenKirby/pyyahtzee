"""
UI controller for the Yahtzee game
"""
import sys
import pygame
from typing import Optional, List, Tuple

from .game_logic import YahtzeeGame
from .dice_logic import DiceLogic
from .scorecard_logic import ScorecardLogic
from .dice_ui import DiceUI
from .scorecard_ui import ScorecardUI
from .button import Button
from .ui_common import (
    SCREEN, POOL_TABLE_GREEN, WHITE, BLACK, FONT, BUTTON_WIDTH, BUTTON_HEIGHT,
    HUMAN_IMAGE, BOT_IMAGE, WIDTH, RED, pause, AI_TURN_DELAY
)


class YahtzeeUI:
    """
    Handles all the UI for the Yahtzee game
    """

    def __init__(self):
        """
        Initialize the UI
        """
        self.game = YahtzeeGame()
        self.clock = pygame.time.Clock()
        self.new_players = False

        # Initialize scorecards UI (they'll be properly set up in init_new_game)
        self.pl1_card_ui: Optional[ScorecardUI] = None
        self.pl2_card_ui: Optional[ScorecardUI] = None
        self.dice_ui: Optional[DiceUI] = None

        # Get player info and start a new game
        self.pl1_name, self.pl2_name = self._get_players()
        self._init_new_game()

    def _init_new_game(self) -> None:
        """
        Initialize a new game
        """
        if self.new_players:
            self.pl1_name, self.pl2_name = self._get_players()

        self.new_players = False

        # Initialize game logic
        self.game.setup_new_game(self.pl1_name, self.pl2_name)

        # Set up UI components
        self.pl1_card_ui = ScorecardUI(50, 300, self.game.player1_scorecard)

        # Only set up second player UI if not in practice mode
        if self.pl2_name:  # Practice mode has empty pl2_name
            self.pl2_card_ui = ScorecardUI(775, 300, self.game.player2_scorecard)
        else:
            self.pl2_card_ui = None

        self.dice_ui = DiceUI(self.game.active_dice)

        # Start game loop
        self.run()

    def _draw_screen(self) -> None:
        """
        Draw the background and scorecards
        """
        SCREEN.fill(POOL_TABLE_GREEN)

        if self.pl1_card_ui:
            self.pl1_card_ui.draw()

        if self.pl2_card_ui:  # Only draw if exists (not practice mode)
            self.pl2_card_ui.draw()

        pygame.display.flip()

    def human_turn(self, scorecard: ScorecardLogic, scorecard_ui: ScorecardUI) -> None:
        """
        Handle a human player's turn
        """
        # Reset the dice for a new turn
        self.game.reset_turn()
        dice = self.game.active_dice
        dice_ui = self.dice_ui
        name = scorecard.player_name

        rolled_once = False
        rolled = False
        roll_button = Button((370, 100), (BUTTON_WIDTH, BUTTON_HEIGHT), "ROLL")

        while True:
            if dice.rolls_left > 0:
                text = f"{name}'s turn. {dice.rolls_left} roll"
                text += f"{'' if dice.rolls_left == 1 else 's'} left"
                # Draw 'roll' button
                pos = pygame.mouse.get_pos()
                roll_button.draw(pos)
            else:
                text = f"No more rolls, {name}. Pick a scoring category..."

            surface = FONT.render(text, True, WHITE)
            text_rect = surface.get_rect(topleft=(50, 50))
            # Add some width to the rect for consistent clearing
            text_rect.width += 20
            pygame.draw.rect(SCREEN, POOL_TABLE_GREEN, text_rect)
            SCREEN.blit(surface, (50, 50))
            pygame.display.flip()

            event = pygame.event.wait()
            if event.type == pygame.QUIT:
                sys.exit()

            if event.type == pygame.KEYDOWN and event.key == pygame.K_r:
                # 'r' key pressed: roll the dice
                rolled_once = True
                rolled = True

            pos = pygame.mouse.get_pos()

            # Handle roll button
            if roll_button.handle_event(event, pos):
                rolled_once = True
                rolled = True

            if rolled:
                if dice.rolls_left > 0:
                    dice.roll_dice()
                    dice.rolls_left -= 1
                else:
                    # No more rolls
                    break

                # Animate the dice roll
                if dice_ui:
                    dice_ui.animate_roll()
                pygame.display.flip()
                rolled = False
                continue

            if event.type == pygame.MOUSEBUTTONDOWN:
                pos = pygame.mouse.get_pos()

                # Check if a die was clicked
                if dice_ui:
                    die_index = dice_ui.get_die_at_pos(pos)
                    if die_index >= 0:
                        dice.toggle_hold(die_index)

                # Only allow category selection if dice have been rolled
                if rolled_once:
                    for category in scorecard.get_all_categories():
                        if (not scorecard.is_category_used(category) and 
                            scorecard_ui.is_category_clicked(pos, category)):
                            scorecard.update_score(dice.rolled, category)
                            return

            # Redraw dice
            if dice_ui:
                dice_ui.draw()
            pygame.display.flip()
  
    def ai_turn(self, scorecard: ScorecardLogic) -> None:
        """
        Handle the AI player's turn
        """
        # Reset dice for a new turn
        self.game.reset_turn()
        dice = self.game.active_dice
        dice_ui = self.dice_ui
        name = scorecard.player_name

        # Show initial state
        text = f"{name}'s turn. {dice.rolls_left} roll"
        text += f"{'' if dice.rolls_left == 1 else 's'} left"
        player_name = FONT.render(text, True, WHITE)
        SCREEN.blit(player_name, (50, 50))
        pygame.display.flip()

        # First roll
        dice.roll_dice()
        dice.rolls_left -= 1
        if dice_ui:
            dice_ui.animate_roll()

        # Process remaining rolls
        while dice.rolls_left > 0:
            # Display current status
            text = f"{name}'s turn. {dice.rolls_left} roll"
            text += f"{'' if dice.rolls_left == 1 else 's'} left"
            player_name = FONT.render(text, True, WHITE)
            text_rect = player_name.get_rect(topleft=(50, 50))
            text_rect.width += 20
            pygame.draw.rect(SCREEN, POOL_TABLE_GREEN, text_rect)
            SCREEN.blit(player_name, (50, 50))
            pygame.display.flip()

            # Let the game logic decide which dice to hold
            # The AI logic is now in the game logic
            # Simple strategy: hold dice with the most common value
            counts = {}
            for die in dice.rolled:
                counts[die] = counts.get(die, 0) + 1

            common_value, _ = max(counts.items(), key=lambda x: x[1])

            for i, die in enumerate(dice.rolled):
                dice.set_hold(i, die == common_value)

            # Redraw dice with held selections
            if dice_ui:
                dice_ui.draw()
            pygame.display.flip()

            # Wait so human can see the held dice
            pause(AI_TURN_DELAY)

            # Roll the dice
            if dice.rolls_left > 0:
                dice.roll_dice()
                dice.rolls_left -= 1

                # Animate the dice roll
                if dice_ui:
                    dice_ui.animate_roll()
                pygame.display.flip()

                # Pause again
                pause(AI_TURN_DELAY)

        # Let the game logic choose the best category
        chosen_category = self.game.process_turn_ai(scorecard)

        # Display chosen category
        text = f"Yahtzee Bot selects {chosen_category} for {scorecard.scores[chosen_category]} points."
        surface = FONT.render(text, True, WHITE)
        text_rect = surface.get_rect(topleft=(50, 50))
        pygame.draw.rect(SCREEN, POOL_TABLE_GREEN, text_rect)
        SCREEN.blit(surface, (50, 50))
        pygame.display.flip()

        # Pause for a moment
        pause(AI_TURN_DELAY)

    def _pl2_turn(self) -> None:
        """
        Handle player 2's turn (human or AI)
        """
        if not self.game.player2_scorecard or not self.pl2_card_ui:
            return

        if self.pl2_name == "Yahtzee Bot":
            self.ai_turn(self.game.player2_scorecard)
        else:
            self.human_turn(self.game.player2_scorecard, self.pl2_card_ui)

    def _game_over(self) -> None:
        """
        Show game over screen with options
        """
        # Get winner info
        winner, winner_score, loser_score = self.game.get_winner()

        # Write high scores to file
        self.game.write_high_scores()

        # Draw game over screen
        self._draw_screen()
        winner_font = pygame.font.SysFont("Arial", 56)

        # Different message for practice mode
        if not self.pl2_name:  # Practice mode
            text = winner_font.render(f"Game Complete! Score: {winner_score}", True, BLACK)
        else:
            text = winner_font.render(f"{winner} WINS!!!!", True, BLACK)
        SCREEN.blit(text, (50, 50))

        # Create option buttons
        ng_button = Button((670, 50), (BUTTON_WIDTH, BUTTON_HEIGHT), "(P)lay again")
        np_button = Button((840, 50), (BUTTON_WIDTH + 20, BUTTON_HEIGHT), "(N)ew Game Mode")
        hs_button = Button((1030, 50), (BUTTON_WIDTH + 60, BUTTON_HEIGHT), "(V)iew High Scores")
        q_button = Button((1260, 50), (BUTTON_WIDTH, BUTTON_HEIGHT), "(Q)uit")

        pygame.display.flip()

        while True:
            pos = pygame.mouse.get_pos()

            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    sys.exit()

                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_q:
                        sys.exit()
                    elif event.key == pygame.K_p:
                        self._init_new_game()
                    elif event.key == pygame.K_n:
                        self.new_players = True
                        self._init_new_game()
                    elif event.key == pygame.K_v:
                        self._view_high_scores()

                if ng_button.handle_event(event, pos):
                    self._init_new_game()
                if np_button.handle_event(event, pos):
                    self.new_players = True
                    self._init_new_game()
                if hs_button.handle_event(event, pos):
                    self._view_high_scores()
                if q_button.handle_event(event, pos):
                    sys.exit()

            ng_button.draw(pos)
            np_button.draw(pos)
            hs_button.draw(pos)
            q_button.draw(pos)
            pygame.display.flip()

    def _view_high_scores(self) -> None:
        """
        Display high scores screen
        """
        SCREEN.fill(POOL_TABLE_GREEN)
        big_font = pygame.font.SysFont("Arial", 54)
        text = big_font.render("High Scores", True, BLACK)
        SCREEN.blit(text, (500, 80))

        # Draw horizontal lines
        pygame.draw.line(SCREEN, BLACK, (0, 225), (WIDTH, 225), 10)
        pygame.draw.line(SCREEN, BLACK, (0, 775), (WIDTH, 775), 5)

        # Get high scores
        high_scores = self.game.get_sorted_high_scores()
        x, y = 500, 350

        for i, (score, name, opponent) in enumerate(high_scores):
            # Name
            t = f"{i + 1}. {name}"
            text = FONT.render(t, True, WHITE)
            SCREEN.blit(text, (x, y + (i * 30)))

            # Opponent
            t = f"vs. {opponent}"
            text = FONT.render(t, True, WHITE)
            SCREEN.blit(text, (x + 300, y + (i * 30)))

            # Score
            t = f"{score}"
            text = FONT.render(t, True, WHITE)
            SCREEN.blit(text, (x + 600, y + (i * 30)))

        pygame.display.flip()

        # Create navigation buttons
        ng_button = Button((370, 800), (BUTTON_WIDTH, BUTTON_HEIGHT), "(P)lay again")
        np_button = Button((540, 800), (BUTTON_WIDTH + 20, BUTTON_HEIGHT), "(N)ew Game Mode")
        q_button = Button((730, 800), (BUTTON_WIDTH, BUTTON_HEIGHT), "(Q)uit")

        while True:
            pos = pygame.mouse.get_pos()

            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    sys.exit()

                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_q:
                        sys.exit()
                    elif event.key == pygame.K_p:
                        self._init_new_game()
                    elif event.key == pygame.K_n:
                        self.new_players = True
                        self._init_new_game()

                if ng_button.handle_event(event, pos):
                    self._init_new_game()
                if np_button.handle_event(event, pos):
                    self.new_players = True
                    self._init_new_game()
                if q_button.handle_event(event, pos):
                    sys.exit()

            ng_button.draw(pos)
            np_button.draw(pos)
            q_button.draw(pos)
            pygame.display.flip()

    def _get_players(self) -> Tuple[str, str]:
        """
        Get player names and types
        """
        game_mode = None
        hs_button = Button((700, 800), (BUTTON_WIDTH + 60, BUTTON_HEIGHT), "(V)iew High Scores")

        while game_mode is None:
            pos = pygame.mouse.get_pos()
            SCREEN.fill((255, 248, 220))

            question = "Select game mode:"
            question_surface = FONT.render(question, True, BLACK)
            SCREEN.blit(question_surface, (50, 50))

            # Option 1: Practice/Solitaire
            practice_text = "(P)ractice Mode - Play by yourself"
            practice_surface = FONT.render(practice_text, True, BLACK)
            SCREEN.blit(practice_surface, (50, 150))

            # Option 2: Human vs Human
            human_text = "(H)uman vs Human"
            human_surface = FONT.render(human_text, True, BLACK)
            SCREEN.blit(human_surface, (50, 200))

            # Option 3: Human vs Bot
            bot_text = "(B)ot vs Human"
            bot_surface = FONT.render(bot_text, True, BLACK)
            SCREEN.blit(bot_surface, (50, 250))

            # Draw the images for visual clarity
            hum_rect = SCREEN.blit(HUMAN_IMAGE, (200, 400))
            bot_rect = SCREEN.blit(BOT_IMAGE, (700, 400))
            hs_button.draw(pos)
            pygame.display.flip()

            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit()

                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_p:
                        game_mode = "practice"
                    elif event.key == pygame.K_h:
                        game_mode = "human"
                    elif event.key == pygame.K_b:
                        game_mode = "bot"
                    elif event.key == pygame.K_v:
                        self._view_high_scores()

                if event.type == pygame.MOUSEBUTTONDOWN:
                    pos = pygame.mouse.get_pos()
                    if hum_rect.collidepoint(pos):
                        game_mode = "human"
                    elif bot_rect.collidepoint(pos):
                        game_mode = "bot"

                if hs_button.handle_event(event, pos):
                    self._view_high_scores()

        # Get player name(s) based on mode
        if game_mode == "practice":
            pl1_name = self._get_text_input("Enter Your Name:")
            pl2_name = ""  # No second player in practice mode
        elif game_mode == "human":
            pl1_name = self._get_text_input("Enter Player One's Name:")
            pl2_name = self._get_text_input("Enter Player Two's Name:")
        else:  # bot mode
            pl1_name = self._get_text_input("Enter Your Name:")
            pl2_name = "Yahtzee Bot"

        return pl1_name, pl2_name

    def _get_text_input(self, prompt: str) -> str:
        """
        Get user-entered text for player names
        """
        input_text = ""
        active = True

        while active:
            SCREEN.fill(POOL_TABLE_GREEN)
            prompt_surface = FONT.render(prompt, True, WHITE)
            input_surface = FONT.render(input_text, True, WHITE)
            SCREEN.blit(prompt_surface, (50, 50))
            SCREEN.blit(input_surface, (50, 100))
            pygame.display.flip()

            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit()

                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_RETURN:
                        active = False  # finish input
                    elif event.key == pygame.K_BACKSPACE:
                        input_text = input_text[:-1]
                    else:
                        input_text += event.unicode

        return input_text

    def run(self) -> None:
        """
        Main game loop
        """
        while True:
            if self.game.is_game_over():
                self._game_over()

            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    sys.exit()

            # Draw the main game screen
            self._draw_screen()

            # Player 1's turn (human)
            if self.game.player1_scorecard and self.pl1_card_ui:
                self.human_turn(self.game.player1_scorecard, self.pl1_card_ui)

            # Redraw and pause
            self._draw_screen()

            # Only do player 2's turn if not in practice mode
            if self.pl2_name:  # Practice mode has empty pl2_name
                pause(1500)
                self._pl2_turn()
                self._draw_screen()

            # Next round
            self.game.next_round()

            # Limit FPS
            self.clock.tick(60)
