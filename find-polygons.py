import sys
import pygame
import json
import colors

# --------- Settings --------------
debug = False
filename = 'polygons.json'
#width, height = 640, 480
width, height = 1920, 1080
# ---------------------------------


print('To position the cursor: Click on the screen or use shift+arrow keys for quick movement, use arrow keys for fine adjustment')

x, y = 0, 0
polygons = []
current_polygon = []

def save_polygons():
    with open(filename, 'w+') as f:
        json.dump(polygons, f)

# Initialize pygame window.
pygame.init()
screen = pygame.display.set_mode((width, height), pygame.RESIZABLE)#, pygame.FULLSCREEN)

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
            # If arrow keys are pressed, move pointer slowly.
            elif event.key == pygame.K_LEFT and x > 0:
                x -= 1
            elif event.key == pygame.K_RIGHT  and x < width:
                x += 1
            elif event.key == pygame.K_UP and y > 0:
                y -= 1
            elif event.key == pygame.K_DOWN and y < height:
                y += 1
        elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            x, y = event.pos

    # If alt and arrow keys are pressed, move pointer quickly.
    keys = pygame.key.get_pressed()
    #offset = 7 if pygame.key.get_mods() & pygame.KMOD_SHIFT else 1
    offset = 7
    if pygame.key.get_mods() & pygame.KMOD_SHIFT:
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
    pygame.draw.circle(screen, colors.red, (x, y), 2)
    #pygame.draw.line(screen, colors.red, (x-50, y), (x+50, y))
    #pygame.draw.line(screen, colors.red, (x, y-50), (x, y+50))
    pygame.draw.circle(screen, colors.red, (x, y), 50, 3)
    pygame.draw.circle(screen, colors.red, (x, y), 10, 2)
    for point in current_polygon:
        pygame.draw.circle(screen, colors.red, point, 3)
    for polygon in polygons:
        pygame.draw.polygon(screen, colors.red, polygon)

    pygame.display.flip()
