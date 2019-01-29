import sys
import pygame
import json
import colors

# --------- Settings --------------
debug = True
filename = 'polygons.json'
width, height = 640, 480
#width, height = 1920, 1080
# ---------------------------------


print('To position the cursor: Click with the mouse or use arrow keys (shift+arrow keys for quick movement)')

x, y = 0, 0
polygons = []
current_polygon = []

def save_polygons():
    with open(filename, 'w+') as f:
        json.dump(polygons, f)

# Initialize pygame window.
pygame.init()
size = width, height = 640, 480
screen = pygame.display.set_mode(size, pygame.RESIZABLE)#, pygame.FULLSCREEN)

while 1:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            sys.exit()
        # Check key events.
        elif event.type == pygame.KEYDOWN:
            if event.key == pygame.K_ESCAPE:
                sys.exit()
            elif event.key == pygame.K_SPACE:  # add point
                current_polygon.append((x, y))
            elif event.key == pygame.K_RETURN:  # add polygon
                if len(current_polygon) > 2:
                    polygons.append(current_polygon)
                    save_polygons()
                    print('Added polygon with points:', current_polygon)
                    current_polygon = []
                else:
                    print('Need at least 3 points to create polygon')
            elif event.key == pygame.K_BACKSPACE:  # delete last point or polygon
                if current_polygon:
                    del current_polygon[-1]
                elif polygons:
                    print('Removed polygon with points:', polygons[-1])
                    del polygons[-1]
                    save_polygons()
        elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            #print(event.pos)
            #print('before', x, y)
            x, y = event.pos
            #print('after', x, y)

    # If arrow keys are pressed, move pointer.
    keys = pygame.key.get_pressed()
    offset = 7 if pygame.key.get_mods() & pygame.KMOD_SHIFT else 1
    if keys[pygame.K_LEFT] and x > 0:
        x -= offset
    if keys[pygame.K_RIGHT] and x < width:
        x += offset
    if keys[pygame.K_UP] and y > 0:
        y -= offset
    if keys[pygame.K_DOWN] and y < height:
        y += offset

    # Draw everything.
    screen.fill(colors.black)
    pygame.draw.rect(screen, colors.red, (x, y, 3, 3))
    pygame.draw.circle(screen, colors.red, (x, y), 50, 3)
    pygame.draw.circle(screen, colors.red, (x, y), 10, 2)
    for point in current_polygon:
        pygame.draw.circle(screen, colors.red, point, 3)
    for polygon in polygons:
        pygame.draw.polygon(screen, colors.red, polygon)

    pygame.display.flip()
