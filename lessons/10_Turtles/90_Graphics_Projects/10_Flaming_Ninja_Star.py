import pygame
import sys
import random

# Initialize Pygame
pygame.init()

# Game Display Options
SCREEN_WIDTH = 900
SCREEN_HEIGHT = 500
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption("Geometry Dash: POLTERGEIST (Wave Mode)")
clock = pygame.time.Clock()

# Nine Circles Color Palette
BLACK = (10, 10, 10)
WHITE = (255, 255, 255)
WAVE_COLOR = (0, 255, 255)     # Cyan wave icon

# Define the tight, chaotic Poltergeist map structure
# Formatting: (X_position, Top_Wall_Height, Bottom_Wall_Y_Position)
# Gives that iconic "extremely narrow tunnel" experience
level_obstacles = [
    (200, 150, 350), (300, 180, 330), (400, 120, 360),
    (500, 200, 310), (600, 140, 340), (700, 220, 300),
    (800, 160, 350), (900, 110, 370), (1000, 190, 320),
    (1100, 230, 290), (1200, 130, 360), (1300, 170, 340),
    (1400, 210, 310), (1500, 150, 350), (1600, 100, 390)
]

# Game Variables
camera_x = 0
game_speed = 5

# Wave Player Setup (X starts fixed, Y controls physics)
player_x = 100
player_y = 250
wave_speed_y = 5
trail_points = []

# Main Game Loop
running = True
flash_counter = 0

while running:
    # 1. Handle Closing Window
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

    # 2. Controls: Hold SPACE to fly up, Release to dive down
    keys = pygame.key.get_pressed()
    if keys[pygame.K_SPACE]:
        player_y -= wave_speed_y  # Move diagonally up
    else:
        player_y += wave_speed_y  # Move diagonally down

    # Camera moves horizontally through the map automatically
    camera_x += game_speed
    current_player_global_x = player_x + camera_x

    # Keep track of the wave's path to draw the iconic neon trail
    trail_points.append((player_x, player_y))
    if len(trail_points) > 40:
        trail_points.pop(0)

    # 3. Handle the Flashing Nine Circles Background Effect
    flash_counter += 1
    if flash_counter % 6 < 3:
        # Alternates dark red styles rapidly to look like the real game
        bg_color = (60, 0, 0) if (flash_counter // 6) % 2 == 0 else (20, 0, 0)
        obstacle_color = (255, 40, 40)
    else:
        bg_color = BLACK
        obstacle_color = (150, 0, 0)

    # Draw Background
    screen.fill(bg_color)

    # 4. Render Obstacles and Test for Collisions
    player_rect = pygame.Rect(player_x, player_y, 16, 16)
    
    # Floor and Ceiling boundaries
    if player_y < 0 or player_y > SCREEN_HEIGHT - 16:
        print("💥 CRASHED! Poltergeist demands perfect precision!")
        running = False

    for obs_x, top_height, bot_y in level_obstacles:
        # Map global level positions to matching screen positions
        screen_x = obs_x - camera_x

        # Only process objects currently visible on screen
        if -100 < screen_x < SCREEN_WIDTH + 100:
            top_block = pygame.Rect(screen_x, 0, 60, top_height)
            bot_block = pygame.Rect(screen_x, bot_y, 60, SCREEN_HEIGHT - bot_y)

            # Draw the glowing grid hazards
            pygame.draw.rect(screen, obstacle_color, top_block)
            pygame.draw.rect(screen, obstacle_color, bot_block)
            pygame.draw.rect(screen, WHITE, top_block, 1) # White outline grid
            pygame.draw.rect(screen, WHITE, bot_block, 1)

            # Accurate hitbox verification
            if player_rect.colliderect(top_block) or player_rect.colliderect(bot_block):
                print("💥 Exploded into icons! Try again to master the spacing!")
                running = False

    # 5. Draw the Wave Trail and Player Icon
    if len(trail_points) > 1:
        pygame.draw.lines(screen, WAVE_COLOR, False, trail_points, 3)
    
    # Draw the main triangle wave projectile
    pygame.draw.polygon(screen, WHITE, [
        (player_x + 16, player_y + 8), 
        (player_x, player_y), 
        (player_x, player_y + 16)
    ])

    # End Level Win Trigger
    if camera_x > 1650:
        print("🎉 VICTORY! You survived Poltergeist!")
        running = False

    # Display loop adjustments
    pygame.display.flip()
    clock.tick(60) # Smooth 60hz simulation framerate

pygame.quit()
sys.exit()
