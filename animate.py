import colors
import sys
import json
import pygame
import pygame.gfxdraw
import numpy as np
import colorsys
import matplotlib as mpl
import matplotlib.path
import sounddevice as sd
import shapely.geometry

from animations import ChangingColorsAnimation, MovingBarAnimation, FadeAnimation, EdgeAnimation, ShootingBallsAnimation
import utils

# Load polygons.
if len(sys.argv) > 1:
    filename = sys.argv[1]
else:
    filename = 'polygons.json'
    print('No filename provided, reading polygons from polygons.json.')

with open(filename, 'r') as f:
    polygons = json.load(f)['polygons']

# Initialize pygame window.
pygame.init()
size = width, height = 640, 480
screen = pygame.display.set_mode(size, pygame.RESIZABLE)

# Initialize timer, see https://stackoverflow.com/questions/13591949/in-pygame-normalizing-game-speed-across-different-fps-values
clock = pygame.time.Clock()
elapsed_ms = 0.
ms_since_last_change = 0.
animation_index = 0

def random_animation():
    global current_animations, animation_index
    animation_index = np.ranomd.randint(5)
    next_animation()

def next_animation():
    global current_animations, animation_index
    if animation_index == 0:
        current_animations = [FadeAnimation(polygon) for polygon in polygons]
    elif animation_index == 1:
        current_animations = [ChangingColorsAnimation(polygon, flash_with_volume=True, change_size_with_volume=False) for i, polygon in enumerate(polygons)]
    elif animation_index == 2:
        current_animations = [MovingBarAnimation(polygon, fill_below=True) for i, polygon in enumerate(polygons)]
    elif animation_index == 3:
        current_animations = [EdgeAnimation(polygon, velocity=10, reverse=np.random.choice([True, False])) for polygon in polygons]
    elif animation_index == 4:
        current_animations = [ShootingBallsAnimation(polygon, which_volume='all') for i, polygon in enumerate(polygons)]
    animation_index += 1
    if animation_index > 4:
        animation_index = 0

next_animation()

# Game loop.
with utils.Audio() as audio:
    while 1:

        # Housekeeping.
        elapsed_ms = clock.tick(60)  # limit fps to 60
        ms_since_last_change += elapsed_ms
        for event in pygame.event.get():
            if event.type == pygame.QUIT or (event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE):
                sys.exit()

        # Get input volume.
        volume, volume_low, volume_high = audio.volume(normalize_to='average', print_=True)

        # Update internal state of all polygons.
        for animation in current_animations:
            animation.update(elapsed_ms, {'all': volume, 'low': volume_low, 'high': volume_high})

        # Draw everything.
        screen.fill(colors.black)
        for animation in current_animations:
            animation.draw(screen)
        pygame.display.flip()

        # Change to next animation periodically.
        if ms_since_last_change > 10000:
            ms_since_last_change = 0
            next_animation()
