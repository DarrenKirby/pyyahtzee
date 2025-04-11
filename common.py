"""
Defines various constants which are used in the game,
as well as a simple pause function.
"""
import sys
import pygame

# pylint: disable=no-member
pygame.init()

# AI turn pause length in milliseconds
AI_TURN_DELAY = 2000

# For testing
MAX_ROUNDS = 13

# Set up the display
WIDTH, HEIGHT = 1440, 900
SCREEN = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Yahtzee")

# Colour constants
POOL_TABLE_GREEN = (10, 108, 3)
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
RED = (255, 0, 0)
DARK_GRAY = (50, 50, 50)
LIGHT_GRAY = (200, 200, 200)
BLUE = (0, 122, 204)
DARK_BLUE = (0, 102, 174)

# Font
FONT = pygame.font.SysFont("Arial", 24)

# High score file
HS_FILE = "high_score.txt"

# Human and bot images
hum = pygame.image.load("assets/human.png")
HUM = pygame.transform.scale(hum, (400, 400))

bot = pygame.image.load("assets/robot.png")
BOT = pygame.transform.scale(bot, (400, 400))

# Button
BUTTON_WIDTH, BUTTON_HEIGHT = 150, 60

# Dice images
DS = 60  # dice size (px)
d1 = pygame.image.load("assets/diceOne.png")
D1 = pygame.transform.scale(d1, (DS, DS))
d2 = pygame.image.load("assets/diceTwo.png")
D2 = pygame.transform.scale(d2, (DS, DS))
d3 = pygame.image.load("assets/diceThree.png")
D3 = pygame.transform.scale(d3, (DS, DS))
d4 = pygame.image.load("assets/diceFour.png")
D4 = pygame.transform.scale(d4, (DS, DS))
d5 = pygame.image.load("assets/diceFive.png")
D5 = pygame.transform.scale(d5, (DS, DS))
d6 = pygame.image.load("assets/diceSix.png")
D6 = pygame.transform.scale(d6, (DS, DS))

DS = 30  # dice size (px)
MD1 = pygame.transform.scale(d1, (DS, DS))
MD2 = pygame.transform.scale(d2, (DS, DS))
MD3 = pygame.transform.scale(d3, (DS, DS))
MD4 = pygame.transform.scale(d4, (DS, DS))
MD5 = pygame.transform.scale(d5, (DS, DS))
MD6 = pygame.transform.scale(d6, (DS, DS))

# Dice int to image mapping
i_to_d = {
    1: D1,
    2: D2,
    3: D3,
    4: D4,
    5: D5,
    6: D6
}

i_to_md = {
    1: MD1,
    2: MD2,
    3: MD3,
    4: MD4,
    5: MD5,
    6: MD6
}


def pause(delay: int) -> None:
    """
    Loops until <delay> milliseconds has passed.
    """
    begin_time = pygame.time.get_ticks()
    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                sys.exit()
        if pygame.time.get_ticks() - begin_time > delay:
            return
