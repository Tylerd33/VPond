# constants.py
import pygame

# Get the screen resolution
infoObject = pygame.display.Info()
SCREEN_WIDTH = infoObject.current_w
SCREEN_HEIGHT = infoObject.current_h

# Game Constants
CELL_SIZE = 20
CREATURE_SIZE_X = 18
CREATURE_SIZE_Y = 12
CREATURE_SPEED = 1
FPS = 60

# Boundary Constants
TOP_MARGIN = 50
SIDE_MARGIN = 50
BOTTOM_MARGIN = 50
SWIM_ZONE_TOP = TOP_MARGIN
SWIM_ZONE_BOTTOM = SCREEN_HEIGHT - BOTTOM_MARGIN
SWIM_ZONE_LEFT = SIDE_MARGIN
SWIM_ZONE_RIGHT = SCREEN_WIDTH - SIDE_MARGIN