import pygame
import sys

# --- CONSTANTS & CONFIGURATION ---
SCREEN_WIDTH = 800
SCREEN_HEIGHT = 600
FPS = 60

# Colors (R, G, B)
COLOR_BG = (30, 30, 40)
COLOR_PLAYER = (50, 150, 255)
COLOR_PLATFORM = (46, 204, 113)
COLOR_TEXT = (255, 255, 255)

# Physics Settings
GRAVITY = 0.8
PLAYER_SPEED = 6
PLAYER_JUMP = -16

# --- CLASSES ---
class Player(pygame.sprite.Sprite):
    def __init__(self, x, y):
        super().__init__()
        self.image = pygame.Surface((40, 40))
        self.image.fill(COLOR_PLAYER)
        self.rect = self.image.get_rect()
        self.rect.topleft = (x, y)
        
        # Movement properties
        self.velocity_x = 0
        self.velocity_y = 0
        self.is_grounded = False

    def handle_input(self):
        keys = pygame.key.get_pressed()
        self.velocity_x = 0
        
        if keys[pygame.K_LEFT]:
            self.velocity_x = -PLAYER_SPEED
        if keys[pygame.K_RIGHT]:
            self.velocity_x = PLAYER_SPEED
        if keys[pygame.K_UP] or keys[pygame.K_SPACE]:
            if self.is_grounded:
                self.velocity_y = PLAYER_JUMP
                self.is_grounded = False

    def update(self, platforms):
        # Apply Gravity
        self.velocity_y += GRAVITY
        
        # Horizontal Movement and Collision
        self.rect.x += self.velocity_x
        self.collide_with_platforms(platforms, "horizontal")
        
        # Vertical Movement and Collision
        self.rect.y += self.velocity_y
        self.is_grounded = False  # Reset before checking collisions
        self.collide_with_platforms(platforms, "vertical")

    def collide_with_platforms(self, platforms, direction):
        for platform in platforms:
            if self.rect.colliderect(platform.rect):
                if direction == "horizontal":
                    if self.velocity_x > 0:  # Moving right
                        self.rect.right = platform.rect.left
                    elif self.velocity_x < 0:  # Moving left
                        self.rect.left = platform.rect.right
                
                elif direction == "vertical":
                    if self.velocity_y > 0:  # Falling down
                        self.rect.bottom = platform.rect.top
                        self.velocity_y = 0
                        self.is_grounded = True
                    elif self.velocity_y < 0:  # Jumping up
                        self.rect.top = platform.rect.bottom
                        self.velocity_y = 0


class Platform(pygame.sprite.Sprite):
    def __init__(self, x, y, width, height):
        super().__init__()
        self.image = pygame.Surface((width, height))
        self.image.fill(COLOR_PLATFORM)
        self.rect = self.image.get_rect()
        self.rect.topleft = (x, y)


# --- MAIN GAME LOOP ---
def main():
    pygame.init()
    screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
    pygame.display.set_caption("Python 2D Platformer")
    clock = pygame.time.Clock()
    font = pygame.font.SysFont(None, 36)

    # Sprite Groups
    all_sprites = pygame.sprite.Group()
    platforms = pygame.sprite.Group()

    # Create Player
    player = Player(100, 400)
    all_sprites.add(player)

    # Design Levels (x, y, width, height)
    level_layout = [
        (0, 560, 800, 40),      # Floor
        (300, 450, 200, 20),    # Middle platform
        (100, 340, 150, 20),    # Left platform
        (550, 300, 180, 20),    # Right platform
        (350, 180, 120, 20)     # Top platform
    ]

    for p in level_layout:
        plat = Platform(p[0], p[1], p[2], p[3])
        all_sprites.add(plat)
        platforms.add(plat)

    # Game Run Flag
    running = True

    while running:
        # 1. Event Handling
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_r:  # Reset Player
                    player.rect.topleft = (100, 400)
                    player.velocity_y = 0

        # 2. Physics & Logic Updates
        player.handle_input()
        player.update(platforms)

        # 3. Drawing / Rendering
        screen.fill(COLOR_BG)
        all_sprites.draw(screen)

        # UI Text Instructions
        instructions = font.render("Arrows / Space to Move | R to Reset", True, COLOR_TEXT)
        screen.blit(instructions, (20, 20))

        # Check if out of bounds (Fell down)
        if player.rect.top > SCREEN_HEIGHT:
            game_over_text = font.render("YOU FELL! Press R to Restart", True, (255, 87, 34))
            screen.blit(game_over_text, (SCREEN_WIDTH // 2 - 150, SCREEN_HEIGHT // 2))

        pygame.display.flip()
        clock.tick(FPS)

    pygame.quit()
    sys.exit()

if __name__ == "__main__":
    main()
