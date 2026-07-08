import pygame
import sys

# Initialize Pygame
pygame.init()

# Game Setup
SCREEN_WIDTH = 800
SCREEN_HEIGHT = 600
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption("Shadow Ninja: The Ascent")
clock = pygame.time.Clock()

# Colors (RGB)
BG_COLOR = (20, 24, 33)       # Dark midnight blue
NINJA_COLOR = (40, 40, 40)     # Dark gray outfit
HEADBAND_COLOR = (220, 20, 60) # Crimson red
PLATFORM_COLOR = (70, 80, 95)  # Slate gray
GOAL_COLOR = (255, 215, 0)     # Gold

# Player (Ninja) Properties
player_rect = pygame.Rect(50, 500, 30, 45) # X, Y, Width, Height
player_velocity_y = 0
player_speed = 6
is_grounded = False

# Platforms Layout [X, Y, Width, Height]
platforms = [
    pygame.Rect(0, 560, 800, 40),     # Main floor
    pygame.Rect(200, 450, 150, 20),   # First ledge
    pygame.Rect(450, 360, 180, 20),   # Second ledge
    pygame.Rect(250, 250, 150, 20),   # Third ledge
    pygame.Rect(550, 160, 150, 20),   # Final ledge
]

# Win Condition Goal
goal_rect = pygame.Rect(600, 110, 30, 30)

# Main Game Loop
running = True
while running:
    # 1. Handle Input Events
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
            
    keys = pygame.key.get_pressed()
    
    # Left/Right movement
    if keys[pygame.K_LEFT]:
        player_rect.x -= player_speed
    if keys[pygame.K_RIGHT]:
        player_rect.x += player_speed
        
    # Ninja Jump (Only if standing on a platform)
    if keys[pygame.K_SPACE] and is_grounded:
        player_velocity_y = -15
        is_grounded = False

    # 2. Physics & Gravity
    player_velocity_y += 0.8 # Gravity strength
    player_rect.y += player_velocity_y

    # 3. Collision Detection
    is_grounded = False
    for platform in platforms:
        if player_rect.colliderect(platform):
            # Check if ninja is falling down onto the top of a platform
            if player_velocity_y > 0 and player_rect.bottom <= platform.top + 15:
                player_rect.bottom = platform.top
                player_velocity_y = 0
                is_grounded = True

    # Screen Boundary Check
    if player_rect.left < 0: player_rect.left = 0
    if player_rect.right > SCREEN_WIDTH: player_rect.right = SCREEN_WIDTH

    # Win Condition Check
    if player_rect.colliderect(goal_rect):
        print("🏆 Victory! The Ninja recovered the ancient scroll!")
        running = False

    # 4. Drawing Everything
    screen.fill(BG_COLOR)
    
    # Draw platforms
    for platform in platforms:
        pygame.draw.rect(screen, PLATFORM_COLOR, platform)
        
    # Draw Golden Scroll Goal
    pygame.draw.rect(screen, GOAL_COLOR, goal_rect)
    
    # Draw Ninja (Body + Headband trail)
    pygame.draw.rect(screen, NINJA_COLOR, player_rect)
    headband_rect = pygame.Rect(player_rect.x - 5, player_rect.y + 8, 15, 6)
    pygame.draw.rect(screen, HEADBAND_COLOR, headband_rect)

    # Refresh Screen
    pygame.display.flip()
    clock.tick(60) # 60 Frames per second

pygame.quit()
sys.exit()
