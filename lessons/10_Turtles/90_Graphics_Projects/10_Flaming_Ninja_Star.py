import pygame
import sys

# Initialize Pygame
pygame.init()

# Game Settings
SCREEN_WIDTH = 900
SCREEN_HEIGHT = 500
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption("Geometry Dash: POLARGEIST")
clock = pygame.time.Clock()

# Colors (Polargeist's classic purple/blue vibes)
BG_COLOR = (40, 15, 70)       # Dark purple atmosphere
GROUND_COLOR = (20, 5, 40)    # Deep dark ground block
CUBE_COLOR = (0, 255, 180)    # Cyan/mint player cube
SPIKE_COLOR = (200, 20, 100)  # Bright magenta spikes
ORB_COLOR = (255, 200, 0)     # Golden jump rings

# Physics Config
GRAVITY = 0.9
JUMP_FORCE = -14
game_speed = 6
camera_x = 0

# Player Definition
player_rect = pygame.Rect(150, 350, 40, 40)
player_vel_y = 0
is_grounded = False

# LEVEL DESIGN (Polargeist Intro Layout)
# Format: X coordinate position
spikes = [350, 550, 750, 1100, 1140, 1500] 

# Yellow Jump Rings (Orbs) Format: (X, Y)
# These allow mid-air jumps if you click right as you pass through them!
orbs = [(650, 280), (1300, 260)]

# Main Game Loop
running = True
while running:
    # 1. Input Processing
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
            
    keys = pygame.key.get_pressed()
    jump_intent = keys[pygame.K_SPACE] or keys[pygame.K_UP]

    # 2. Physics & Gravity Handling
    player_vel_y += GRAVITY
    player_rect.y += player_vel_y

    # Ground Level Stop (Standard GD Floor line)
    if player_rect.bottom >= 400:
        player_rect.bottom = 400
        player_vel_y = 0
        is_grounded = True

    # Regular Ground Jump
    if jump_intent and is_grounded:
        player_vel_y = JUMP_FORCE
        is_grounded = False

    # Move the level forward horizontally automatically
    camera_x += game_speed

    # 3. Game Element Rendering & Collisions
    screen.fill(BG_COLOR)
    
    # Draw the main landscape floor line
    pygame.draw.rect(screen, GROUND_COLOR, (0, 400, SCREEN_WIDTH, 100))

    # Handle Jump Orbs
    for orb_x, orb_y in orbs:
        screen_orb_x = orb_x - camera_x
        # Only render if visible on the player's view
        if -50 < screen_orb_x < SCREEN_WIDTH + 50:
            orb_rect = pygame.Rect(screen_orb_x, orb_y, 30, 30)
            pygame.draw.circle(screen, ORB_COLOR, (screen_orb_x + 15, orb_y + 15), 15)
            
            # Interactive Ring mechanic: Touch orb + Press spacebar = Mid-air boost!
            if player_rect.colliderect(orb_rect) and jump_intent:
                player_vel_y = JUMP_FORCE
                is_grounded = False

    # Handle Spikes
    for spike_x in spikes:
        screen_spike_x = spike_x - camera_x
        if -50 < screen_spike_x < SCREEN_WIDTH + 50:
            # Build the custom triangle path for precise spikes
            spike_points = [
                (screen_spike_x, 400),
                (screen_spike_x + 20, 350),
                (screen_spike_x + 40, 400)
            ]
            pygame.draw.polygon(screen, SPIKE_COLOR, spike_points)

            # Hitbox check: Crash and burn on impact
            spike_hitbox = pygame.Rect(screen_spike_x + 8, 360, 24, 40)
            if player_rect.colliderect(spike_hitbox):
                print("💥 Crash! Practice your timings to beat Polargeist!")
                running = False

    # Draw Player Avatar Square
    pygame.draw.rect(screen, CUBE_COLOR, player_rect)
    pygame.draw.rect(screen, (255, 255, 255), player_rect, 3) # Sleek border outline

    # Win Flag Trigger
    if camera_x > 1700:
        print("🎉 Level Complete! You mastered the rhythms of Polargeist!")
        running = False

    # Update Frame
    pygame.display.flip()
    clock.tick(60)

pygame.quit()
sys.exit()

