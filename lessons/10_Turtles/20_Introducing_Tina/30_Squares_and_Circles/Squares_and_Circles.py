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
    pygame.display.set_caption("Python 2D Platformer - Multi-Level")
    clock = pygame.time.Clock()
    font = pygame.font.SysFont(None, 36)

    # Sprite Groups
    all_sprites = pygame.sprite.Group()
    platforms = pygame.sprite.Group()

    # Create Player
    player = Player(100, 400)
    all_sprites.add(player)

    # Design Multiple Levels (x, y, width, height)
    levels = {
        1: [
            (0, 560, 800, 40),  # Floor
            (300, 450, 200, 20),
            (100, 340, 150, 20),
            (550, 300, 180, 20),
            (350, 180, 120, 20)
        ],
        2: [
            (0, 560, 800, 40),  # Floor
            (100, 450, 120, 20),
            (300, 380, 120, 20),
            (500, 300, 120, 20),
            (300, 200, 120, 20)
        ],
        3: [
            (0, 560, 400, 40),  # Partial Floor
            (450, 560, 350, 40), # Separate Floor
            (150, 450, 100, 20),
            (300, 350, 100, 20),
            (450, 250, 100, 20),
            (600, 150, 100, 20)
        ]
    }
    
    current_level = 1
    max_level = len(levels)

    def load_level(level_num):
        # Clear previous platforms
        platforms.empty()
        
        # Remove only platforms from all_sprites (keep player)
        for sprite in all_sprites:
            if isinstance(sprite, Platform):
                sprite.kill()

        # Add new platforms
        for p in levels[level_num]:
            plat = Platform(p[0], p[1], p[2], p[3])
            all_sprites.add(plat)
            platforms.add(plat)

    # Load initial level
    load_level(current_level)

    # Game Run Flag
    running = True
    game_complete = False

    while running:
        # 1. Event Handling
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_r:  # Reset Player
                    player.rect.topleft = (100, 400)
                    player.velocity_x = 0
                    player.velocity_y = 0
                if event.key == pygame.K_SPACE and game_complete: # Restart Game
                    current_level = 1
                    game_complete = False
                    player.rect.topleft = (100, 400)
                    load_level(current_level)

        # Only process physics/input if the game isn't finished
        if not game_complete:
            # 2. Physics & Logic Updates
            player.handle_input()
            player.update(platforms)

            # Check Level Completion (Reach the right edge of the screen)
            if player.rect.left >= SCREEN_WIDTH:
                current_level += 1
                if current_level > max_level:
                    game_complete = True
                else:
                    load_level(current_level)
                    # Respawn at the left side for the next level
                    player.rect.topleft = (50, 400)
                    player.velocity_x = 0
                    player.velocity_y = 0

        # 3. Drawing / Rendering
        screen.fill(COLOR_BG)
        all_sprites.draw(screen)

        # UI Text Instructions
        if game_complete:
            win_text1 = font.render("YOU BEAT ALL LEVELS!", True, COLOR_TEXT)
            win_text2 = font.render("Press SPACE to Restart", True, COLOR_PLATFORM)
            screen.blit(win_text1, (SCREEN_WIDTH // 2 - 140, SCREEN_HEIGHT // 2 - 30))
            screen.blit(win_text2, (SCREEN_WIDTH // 2 - 145, SCREEN_HEIGHT // 2 + 20))
        else:
            instructions = font.render("Arrows/Space to Move | R to Reset", True, COLOR_TEXT)
            screen.blit(instructions, (20, 20))
            
            # Level Display
            level_text = font.render(f"Level: {current_level}", True, COLOR_TEXT)
            screen.blit(level_text, (SCREEN_WIDTH - 120, 20))

        # Check if out of bounds (Fell down)
        if player.rect.top > SCREEN_HEIGHT and not game_complete:
            game_over_text = font.render("YOU FELL! Press R to Restart", True, (255, 87, 34))
            screen.blit(game_over_text, (SCREEN_WIDTH // 2 - 170, SCREEN_HEIGHT // 2))

        pygame.display.flip()
        clock.tick(FPS)

    pygame.quit()
    sys.exit()

if __name__ == "__main__":
    main()
