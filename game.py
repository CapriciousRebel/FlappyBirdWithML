import pygame
import neat
import time
import random
import os


WINDOW_WIDTH = 600
WINDOW_HEIGHT = 800


BIRD_SPRITES = [pygame.transform.scale2x(pygame.image.load(os.path.join("imgs", "bird1.png"))),
                pygame.transform.scale2x(pygame.image.load(
                    os.path.join("imgs", "bird2.png"))),
                pygame.transform.scale2x(pygame.image.load(os.path.join("imgs", "bird3.png")))]

PIPE_SPRITE = pygame.transform.scale2x(
    pygame.image.load(os.path.join("imgs", "pipe.png")))

BACKGROUND_SPRITE = pygame.transform.scale2x(
    pygame.image.load(os.path.join("imgs", "bg.png")))

BASE_SPRITE = pygame.transform.scale2x(
    pygame.image.load(os.path.join("imgs", "base.png")))


