"""
Main file for the Yahtzee game which defines player turns and a main app loop.
"""
import sys
import pygame
from dice import Dice
from scorecard import Scorecard
from button import Button
from common import BUTTON_WIDTH, BUTTON_HEIGHT, FONT, WHITE, SCREEN, POOL_TABLE_GREEN
from common import HUMAN_IMAGE, BOT_IMAGE, HS_FILE, MAX_ROUNDS, RED, pause, BLACK, WIDTH, AI_TURN_DELAY

# pylint: disable=no-member
pygame.init()


class PlayerTurn:
    """
    Defines methods for a human player turn and an AI player turn.
    """

    @staticmethod
    def human_turn(scorecard: Scorecard) -> None:
        """
        Functionality for a human player turn.
        """
        dice = Dice()
        name = scorecard.player_name
        # Check if player has rolled at least once
        rolled_once = False
        # Check if the player has rolled
        rolled = False
        button = Button((370, 100), (BUTTON_WIDTH, BUTTON_HEIGHT), "ROLL")
        while True:
            if dice.rolls_left > 0:
                text = f"{name}'s turn. {dice.rolls_left} roll"
                text += f"{'' if dice.rolls_left == 1 else 's'} left"
                # Draw 'roll' button
                pos = pygame.mouse.get_pos()
                button.draw(pos)
            else:
                text = f"No more rolls, {name}. Pick a scoring category..."
            surface = FONT.render(text, True, WHITE)
            text_rect = surface.get_rect(topleft=(50, 50))
            # Add some width to the rect, as '1 roll left'
            # does not cover same area as '2 rolls left'
            text_rect[2] += 20
            # Draw background covering the text area
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
            clicked = button.handle_event(event, pos)
            if clicked:
                rolled_once = True
                rolled = True
            if rolled:
                if dice.rolls_left > 0:
                    dice.roll_dice()
                    dice.rolls_left -= 1
                else:
                    # No more rolls.
                    break

                dice.animate_roll()
                pygame.display.flip()
                rolled = False
                continue
            if event.type == pygame.MOUSEBUTTONDOWN:
                # Check if the click is on a die or category
                pos = pygame.mouse.get_pos()
                for v in dice.slots.values():
                    if v[0].collidepoint(pos):
                        if not v[1]:
                            # We can directly assign to v as the underlying
                            # list is mutable and passed by reference.
                            v[1] = True
                        else:
                            v[1] = False
                # Disable choosing a category if the dice have not been rolled
                if not rolled_once:
                    continue
                for category in scorecard.scores:
                    if (scorecard.is_clicked(pos, category) and
                            scorecard.scores[category] is None):
                        scorecard.update_score(dice.rolled, category)
                        return

            dice.draw()
            for v in dice.slots.values():
                if v[1]:
                    pygame.draw.rect(SCREEN, RED, v[0], 5)
            pygame.display.flip()

    @staticmethod
    def ai_turn(scorecard: Scorecard) -> None:
        """
        Functionality for an AI player 2. Very naïve currently.
        """
        dice = Dice()
        name = scorecard.player_name

        text = f"{name}'s turn. {dice.rolls_left} roll"
        text += f"{'' if dice.rolls_left == 1 else 's'} left"
        player_name = FONT.render(text, True, WHITE)
        SCREEN.blit(player_name, (50, 50))
        pygame.display.flip()

        # AI rolling phase
        dice.roll_dice()
        dice.rolls_left -= 1
        dice.animate_roll()

        while dice.rolls_left > 0:

            # Display current status
            text = f"{name}'s turn. {dice.rolls_left} roll"
            text += f"{'' if dice.rolls_left == 1 else 's'} left"
            player_name = FONT.render(text, True, WHITE)
            text_rect = player_name.get_rect(topleft=(50, 50))
            # Add some width to the rect, as '1 roll left'
            # does not cover same area as '2 rolls left'
            text_rect[2] += 20
            pygame.draw.rect(SCREEN, POOL_TABLE_GREEN, text_rect)
            SCREEN.blit(player_name, (50, 50))
            pygame.display.flip()

            # Let the AI decide which dice to hold.
            # Simple strategy: hold dice with the most common value.
            counts: dict[int, int] = {}
            for die in dice.rolled:
                counts[die] = counts.get(die, 0) + 1

            common_value, _ = max(counts.items(), key=lambda x: x[1])
            for i, _ in enumerate(dice.rolled):
                key = i + 1  # dice.slots keys are 1-indexed
                if dice.rolled[i] == common_value:
                    dice.slots[key][1] = True
                else:
                    dice.slots[key][1] = False

            # Redraw dice with held selections
            dice.draw()
            for key, (rect, selected) in dice.slots.items():
                if selected:
                    pygame.draw.rect(SCREEN, RED, rect, 5)
            pygame.display.flip()
            # wait 2 seconds so the human player can see the held dice
            pause(AI_TURN_DELAY)

            # Roll dice if rolls are still available
            if dice.rolls_left > 0:
                dice.roll_dice()
                dice.rolls_left -= 1

                # Update display after rolling
                dice.animate_roll()
                for key, (rect, selected, _) in dice.slots.items():
                    if selected:
                        pygame.draw.rect(SCREEN, RED, rect, 5)
                pygame.display.flip()
                # pause for 2s
                pause(AI_TURN_DELAY)

        # After rolling, choose the best scoring category.
        # Here, we iterate over the available (None) categories and pick the one
        # that would give the highest score for the current dice.
        best_category: str = ""
        best_score = -1
        for category in scorecard.scores:
            if scorecard.scores[category] is None:
                score = scorecard.calculate_score(dice.rolled, category)
                if score > best_score:
                    best_score = score
                    best_category = category

        # Display chosen category for a moment.
        text = f"Yahtzee Bot selects {best_category} for {best_score} points."
        surface = FONT.render(text, True, WHITE)
        text_rect = surface.get_rect(topleft=(50, 50))
        pygame.draw.rect(SCREEN, POOL_TABLE_GREEN, text_rect)
        SCREEN.blit(surface, (50, 50))
        pygame.display.flip()
        # Pause for 2s
        pause(AI_TURN_DELAY)
        # Update the scorecard with the chosen category.
        scorecard.update_score(dice.rolled, best_category)


class MainLoop(PlayerTurn):
    """
    The app mainloop.

    Should probably part out the high-score functionality at some point.
    """

    def __init__(self):
        self.new_players = False
        self.high_scores = []
        self.__read_high_scores()
        self.pl1_name, self.pl2_name = self.__get_players()
        self.__init_new_game()

    def __init_new_game(self) -> None:
        """
        Initializes new players and scorecards, and runs the game.
        """
        if self.new_players:
            self.pl1_name, self.pl2_name = self.__get_players()
        self.new_players = False
        self.clock = pygame.time.Clock()
        self.pl1_scorecard = Scorecard(50, 300, self.pl1_name)
        self.pl2_scorecard = Scorecard(775, 300, self.pl2_name)
        self.round = 0
        self.run()

    def __write_high_scores(self) -> None:
        """
        Writes the top-10 high scores to a file.
        """
        shs = sorted(self.high_scores, reverse=True)
        try:
            with open(HS_FILE, 'w', encoding='utf-8') as f:
                for score in shs[:10]:
                    line = f"{score[0]},{score[1]},{score[2]}\n"
                    f.write(line)
        except IOError as e:
            print(f"Could not write to high score file: {e}")

    def __read_high_scores(self) -> None:
        """
        Reads high scores from a file.
        """
        try:
            with open(HS_FILE, 'r', encoding='utf-8') as f:
                lines = f.readlines()
            for line in lines:
                items = line.strip().split(",")
                self.high_scores.append((int(items[0]), items[1], items[2]))
        except IOError as e:
            print(f"Could not read from high score file: {e}")

    def __view_high_scores(self) -> None:
        """
        Displays a screen and prints the high scores.
        """
        SCREEN.fill(POOL_TABLE_GREEN)
        big_font = pygame.font.SysFont("Arial", 54)
        text = big_font.render("High Scores", True, BLACK)
        SCREEN.blit(text, (500, 80))

        # Draw horizontal lines
        pygame.draw.line(SCREEN, BLACK, (0, 225), (WIDTH, 225), 10)
        pygame.draw.line(SCREEN, BLACK, (0, 775), (WIDTH, 775), 5)

        shs = sorted(self.high_scores, reverse=True)
        x = 500
        y = 350
        for i, score in enumerate(shs[:10]):
            scr, name, opp = score
            # Name
            t = f"{i + 1}. {name}"
            text = FONT.render(t, True, WHITE)
            SCREEN.blit(text, (x, y + (i * 30)))
            # Opponent
            t = f"vs. {opp}"
            text = FONT.render(t, True, WHITE)
            SCREEN.blit(text, (x + 300, y + (i * 30)))
            # Score
            t = f"{scr}"
            text = FONT.render(t, True, WHITE)
            SCREEN.blit(text, (x + 600, y + (i * 30)))
        pygame.display.flip()

        # Instantiate buttons
        ng_button = Button((370, 800), (BUTTON_WIDTH, BUTTON_HEIGHT), "(P)lay again")
        np_button = Button((540, 800), (BUTTON_WIDTH + 20, BUTTON_HEIGHT), "(N)ew Players")
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
                        self.__init_new_game()
                    elif event.key == pygame.K_n:
                        self.new_players = True
                        self.__init_new_game()
                    elif event.key == pygame.K_v:
                        self.__view_high_scores()
                if ng_button.handle_event(event, pos):
                    self.__init_new_game()
                if np_button.handle_event(event, pos):
                    self.new_players = True
                    self.__init_new_game()
                if q_button.handle_event(event, pos):
                    sys.exit()

            ng_button.draw(pos)
            np_button.draw(pos)
            q_button.draw(pos)
            pygame.display.flip()

    def __get_players(self) -> tuple[str, str]:
        """
        Prompts whether player 2 is human or AI.
        """
        pl2_type = None
        hs_button = Button((700, 800), (BUTTON_WIDTH + 60, BUTTON_HEIGHT), "(V)iew High Scores")
        while pl2_type is None:
            pos = pygame.mouse.get_pos()
            SCREEN.fill((255, 248, 220))
            question = "Is player two (h)uman or (b)ot?"
            question_surface = FONT.render(question, True, BLACK)
            SCREEN.blit(question_surface, (50, 50))

            hum_rect = SCREEN.blit(HUMAN_IMAGE, (200, 300))
            bot_rect = SCREEN.blit(BOT_IMAGE, (700, 300))
            hs_button.draw(pos)
            pygame.display.flip()

            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit()
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_h:
                        pl2_type = "human"
                    elif event.key == pygame.K_b:
                        pl2_type = ""  # Value doesn't matter

                if event.type == pygame.MOUSEBUTTONDOWN:
                    pos = pygame.mouse.get_pos()
                    if hum_rect.collidepoint(pos):
                        pl2_type = "human"
                    elif bot_rect.collidepoint(pos):
                        pl2_type = ""  # Value doesn't matter
                if hs_button.handle_event(event, pos):
                    self.__view_high_scores()

        pl1_name = self.__get_text_input("Enter Player One's Name:")
        if pl2_type == "human":
            pl2_name = self.__get_text_input("Enter Player Two's Name:")
        else:
            pl2_name = "Yahtzee Bot"
        return pl1_name, pl2_name

    @staticmethod
    def __get_text_input(prompt: str) -> str:
        """
        Get user-entered text for player names.
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

    def __draw_screen(self) -> None:
        """
        Draws the green background and scorecards.
        """
        SCREEN.fill(POOL_TABLE_GREEN)
        self.pl1_scorecard.draw()
        self.pl2_scorecard.draw()
        pygame.display.flip()

    def __pl2_turn(self, scorecard: Scorecard) -> None:
        """
        Dispatch player 2 whether AI or human.
        """
        if self.pl2_name == "Yahtzee Bot":
            self.ai_turn(scorecard)
        else:
            self.human_turn(scorecard)

    def __game_over(self) -> None:
        """
        A game-over screen which displays navigation options.
        """
        pl1_score = self.pl1_scorecard.final_tally()
        pl2_score = self.pl2_scorecard.final_tally()
        if pl1_score > pl2_score:
            winner = self.pl1_name
        else:
            winner = self.pl2_name

        # Add score to high score array
        self.high_scores.append((pl1_score, self.pl1_name, self.pl2_name))
        self.high_scores.append((pl2_score, self.pl2_name, self.pl1_name))
        # And write them to the file
        self.__write_high_scores()

        self.__draw_screen()
        winner_font = pygame.font.SysFont("Arial", 56)
        text = winner_font.render(f"{winner} WINS!!!!", True, BLACK)
        SCREEN.blit(text, (50, 50))
        pygame.display.flip()

        # Instantiate buttons
        ng_button = Button((670, 50), (BUTTON_WIDTH, BUTTON_HEIGHT), "(P)lay again")
        np_button = Button((840, 50), (BUTTON_WIDTH + 20, BUTTON_HEIGHT), "(N)ew Players")
        hs_button = Button((1030, 50), (BUTTON_WIDTH + 60, BUTTON_HEIGHT), "(V)iew High Scores")
        q_button = Button((1260, 50), (BUTTON_WIDTH, BUTTON_HEIGHT), "(Q)uit")

        while True:
            pos = pygame.mouse.get_pos()

            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    sys.exit()
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_q:
                        sys.exit()
                    elif event.key == pygame.K_p:
                        self.__init_new_game()
                    elif event.key == pygame.K_n:
                        self.new_players = True
                        self.__init_new_game()
                    elif event.key == pygame.K_v:
                        self.__view_high_scores()
                if ng_button.handle_event(event, pos):
                    self.__init_new_game()
                if np_button.handle_event(event, pos):
                    self.new_players = True
                    self.__init_new_game()
                if hs_button.handle_event(event, pos):
                    self.__view_high_scores()
                if q_button.handle_event(event, pos):
                    sys.exit()

            ng_button.draw(pos)
            np_button.draw(pos)
            hs_button.draw(pos)
            q_button.draw(pos)
            pygame.display.flip()

    def run(self) -> None:
        """
        Cycles through pl1 and pl2 turns until 13 rounds are complete.
        """
        while True:
            if self.round == MAX_ROUNDS:
                self.__game_over()
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    sys.exit()

            self.__draw_screen()
            self.human_turn(self.pl1_scorecard)
            self.__draw_screen()
            pause(1500)
            self.__pl2_turn(self.pl2_scorecard)
            self.__draw_screen()
            self.round += 1
            self.clock.tick(60)


if __name__ == "__main__":
    MainLoop()
