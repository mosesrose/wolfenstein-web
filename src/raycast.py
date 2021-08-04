# packages
from math import sin, cos, pi
import pygame
import sys

# screen
WIDTH = 320
HEIGHT = 240
FOV = pi / 3

# init pygame
pygame.init()
pygame.mouse.set_visible(False)
window = pygame.display.set_mode((WIDTH, HEIGHT), pygame.FULLSCREEN)#, pygame.FULLSCREEN
clock = pygame.time.Clock()

# map
MAP_SCALE = 30
MAP_SPEED = (MAP_SCALE / 2) / 10
MAP_SIZE = 8

MAP = (
    '########'
    '#      #'
    '#  #   #'
    '#  #   #'
    '#  #   #'
    '#      #'
    '#      #'
    '########'
)

'''20
MAP = (
    '####################'
    '#                  #'
    '#                  #'
    '#                  #'
    '#                  #'
    '#                  #'
    '#                  #'
    '#                  #'
    '#    #   #    #    #'
    '#    #   #    #    #'
    '#    #   #    #    #'
    '#                  #'
    '#                  #'
    '#                  #'
    '#                  #'
    '#                  #'
    '#                  #'
    '#                  #'
    '#                  #'
    '####################'
)
'''


# player coordinates and view angle
player_x = MAP_SCALE + 1.0
player_y = MAP_SCALE + 1.0
player_angle = pi / 3

# game loop
while True:
    # get user input
    pygame.event.get()
    keys = pygame.key.get_pressed()
    
    # player move offset
    offset_x = sin(player_angle) * MAP_SPEED
    offset_y = cos(player_angle) * MAP_SPEED

    # handle user input
    if keys[pygame.K_ESCAPE]: pygame.quit(); sys.exit(0);
    if keys[pygame.K_LEFT]: player_angle += 0.06
    if keys[pygame.K_RIGHT]: player_angle -= 0.06
    if keys[pygame.K_UP]:
        target_x = int(player_y / MAP_SCALE) * MAP_SIZE + int((player_x + offset_x) / MAP_SCALE)
        target_y = int((player_y + offset_y) / MAP_SCALE) * MAP_SIZE + int(player_x / MAP_SCALE)
        if MAP[target_x] == ' ': player_x += offset_x
        if MAP[target_y] == ' ': player_y += offset_y
    if keys[pygame.K_DOWN]:
        target_x = int(player_y / MAP_SCALE) * MAP_SIZE + int((player_x - offset_x) / MAP_SCALE)
        target_y = int((player_y - offset_y) / MAP_SCALE) * MAP_SIZE + int(player_x / MAP_SCALE)
        if MAP[target_x] == ' ': player_x -= offset_x
        if MAP[target_y] == ' ': player_y -= offset_y
    
    # draw background
    window.fill((100, 100, 100))
    
    # draw map (debug)
    pygame.draw.rect(window, (0, 0, 0), (0, 0, MAP_SIZE * MAP_SCALE, MAP_SIZE * MAP_SCALE))
    for row in range(MAP_SIZE):
        for col in range(MAP_SIZE):
            pygame.draw.rect(window,
            (100, 100, 100) if MAP[row * MAP_SIZE + col] != ' ' else (200, 200, 200),
            (col * MAP_SCALE, row * MAP_SCALE, MAP_SCALE - 1, MAP_SCALE - 1))
    pygame.draw.circle(window, (255, 0, 0), (int(player_x), int(player_y)), 2)
    pygame.draw.line(window, (255, 0, 0), (player_x, player_y), 
                    (player_x + sin(player_angle) * 5, player_y + cos(player_angle) * 5), 1)

    
    # ray casting
    current_angle = player_angle - (FOV / 2)    
    start_x = int(player_x / MAP_SCALE) * MAP_SCALE
    start_y = int(player_y / MAP_SCALE) * MAP_SCALE
    for ray in range(WIDTH):    
        current_sin = sin(current_angle); current_sin = current_sin if current_sin else 0.000001
        current_cos = cos(current_angle); current_cos = current_cos if current_cos else 0.000001

        # vertical collision
        target_x, direction_x = (start_x + MAP_SCALE, 1) if current_sin >= 0 else (start_x, -1)
        for i in range(0, WIDTH, MAP_SCALE):
            vertical_depth = (target_x - player_x) / current_sin
            target_y = player_y + vertical_depth * current_cos
            map_x = int(target_x / MAP_SCALE)
            map_y = int(target_y / MAP_SCALE)
            if current_sin <= 0: map_x += direction_x
            target_square = map_y * MAP_SIZE + map_x
            if target_square not in range(len(MAP)) or MAP[target_square] == '#': break
            target_x += direction_x * MAP_SCALE

        vx = target_x
        vy = target_y
        vd = vertical_depth

        #pygame.draw.line(window, (255, 0, 0), (player_x, player_y), (target_x, target_y), 1)

        # horizontal collision
        target_y, direction_y = (start_y + MAP_SCALE, 1) if current_cos >= 0 else (start_y, -1)
        for i in range(0, WIDTH, MAP_SCALE):
            horizontal_depth = (target_y - player_y) / current_cos
            target_x = player_x + horizontal_depth * current_sin
            map_x = int(target_x / MAP_SCALE)
            map_y = int(target_y / MAP_SCALE)
            if current_cos <= 0: map_y += direction_y
            target_square = map_y * MAP_SIZE + map_x
            if target_square not in range(0, len(MAP)) or MAP[target_square] != ' ': break
            target_y += direction_y * MAP_SCALE
        
        hx = target_x
        hy = target_y
        hd = horizontal_depth        
        
        #pygame.draw.line(window, (0, 255, 0), (player_x, player_y), (target_x, target_y), 1)
        
        min_x = vx if vd < hd else hx
        min_y = vy if vd < hd else hy
        #pygame.draw.line(window, (255, 255, 0), (player_x, player_y), (min_x, min_y), 1)

        # projection

        depth = vertical_depth if vertical_depth < horizontal_depth else horizontal_depth
        color = 255 / (1 + depth * depth * 0.0001)
        depth *= cos(player_angle - current_angle)
        wall_height = MAP_SCALE * 350 / (depth + 0.0001)
        if wall_height > HEIGHT: wall_height = HEIGHT
        pygame.draw.rect(window, (color, color, color), (ray, (HEIGHT / 2) - wall_height / 2, 1, wall_height))

        current_angle += (FOV / WIDTH)

    # fps
    clock.tick(30)

    # print FPS to screen
    font = pygame.font.SysFont('Monospace Regular', 30)
    fps_surface = font.render(str(int(clock.get_fps())), False, (255, 0, 0))
    window.blit(fps_surface, (296, 0))

    # update display
    pygame.display.flip()
