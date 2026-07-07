import pygame
import sys
import math

# --- CONSTANTS & CONFIGURATION ---
SCREEN_WIDTH = 800
SCREEN_HEIGHT = 600
FPS = 60

# Colors (Scratch Aesthetic)
COLOR_BG = (15, 20, 30)         # Dark night sky
COLOR_PLAYER = (231, 76, 60)     # Ninja Red
COLOR_PLATFORM = (44, 62, 80)    # Dark slate bricks
COLOR_TEXT = (255, 255, 255)
COLOR_STAR = (241, 196, 15)     # Glowing Kunai/Star gold

# Physics Settings (Tweaked for crisp Scratch-like responses)
GRAVITY = 0.6
FRICTION = 0.85
RUN_SPEED = 0.9
MAX_SPEED = 7
JUMP_FORCE = -13
WALL_SLIDE_SPEED = 2

# --- CLASSES ---

class NinjaStar(pygame.sprite.Sprite):
    """ A basic throwing projectile reminiscent of Scratch clone weapons """
    def __init__(self, x, y, direction):
        super().__init__()
        self.image = pygame.Surface((12, 12), pygame.SRCALPHA)
        # Draw a little star/diamond diamond shape
        pygame.draw.polygon(self.image, COLOR_STAR, [(6,0), (12,6), (6,12), (0,6)])
        self.rect = self.image.get_rect(center=(x, y))
        self.speed = 12 * direction
        self.life = 40  # Disappears after traveling a certain distance

    def update(self, platforms):
        self.rect.x += self.speed
        self.life -= 1
        # Destroy star if it hits a wall or runs out of lifetime
        if pygame.sprite.spritecollideany(self, platforms) or self.life <= 0:
            self.kill()


class Player(pygame.sprite.Sprite):
    def __init__(self, x, y):
        super().__init__()
        self.image = pygame.Surface((32, 44))
        self.image.fill(COLOR_PLAYER)
        # Headband tail detail for visual flair
        pygame.draw.rect(self.image, (255, 255, 255), (0, 8, 12, 6)) 
        
        self.rect = self.image.get_rect()
        self.rect.topleft = (x, y)

        # Movement properties
        self.vx = 0
        self.vy = 0
        self.is_grounded = False
        self.facing_direction = 1  # 1 = Right, -1 = Left
        self.on_wall = 0          # -1 = Wall on left, 1 = Wall on right, 0 = No wall
        self.shoot_cooldown = 0

    def handle_input(self, all_sprites, stars):
        keys = pygame.key.get_pressed()
        
        # Horizontal acceleration (Scratch-like smooth inertia)
        if keys[pygame.K_LEFT] or keys[pygame.K_a]:
            self.vx -= RUN_SPEED
            self.facing_direction = -1
        elif keys[pygame.K_RIGHT] or keys[pygame.K_d]:
            self.vx += RUN_SPEED
            self.facing_direction = 1

        # Jump & Wall Jump
        if keys[pygame.K_UP] or keys[pygame.K_w] or keys[pygame.K_SPACE]:
            if self.is_grounded:
                self.vy = JUMP_FORCE
                self.is_grounded = False
            elif self.on_wall != 0:  # Wall jump mechanic!
                self.vy = JUMP_FORCE
                self.vx = -self.on_wall * (MAX_SPEED * 1.2)  # Kick away from wall
                self.on_wall = 0

        # Throw Ninja Star (F or Return key)
        if (keys[pygame.K_f] or keys[pygame.K_RETURN]) and self.shoot_cooldown == 0:
            star = NinjaStar(self.rect.centerx, self.rect.centery, self.facing_direction)
            all_sprites.add(star)
            stars.add(star)
            self.shoot_cooldown = 15  # Frame cooldown limit

        if self.shoot_cooldown > 0:
            self.shoot_cooldown -= 1

    def update(self, platforms):
        # Apply physics formulas
        self.vx *= FRICTION
        self.vy += GRAVITY

        # Cap terminal velocities
        if abs(self.vx) > MAX_SPEED:
            self.vx = math.copysign(MAX_SPEED, self.vx)
        
        # Wall slide restriction
        if self.on_wall != 0 and self.vy > WALL_SLIDE_SPEED:
            self.vy = WALL_SLIDE_SPEED

        # X Movement & Intercepts
        self.rect.x += int(self.vx)
        self.on_wall = 0
        self.collide_with_platforms(platforms, "horizontal")

        # Y Movement & Intercepts
        self.rect.y += int(self.vy)
        self.is_grounded = False
        self.collide_with_platforms(platforms, "vertical")

    def collide_with_platforms(self, platforms, direction):
        # Tiny expanding check box to capture wall touch parameters
        check_rect = self.rect.inflate(2, 0) if direction == "horizontal" else self.rect

        for platform in platforms:
            if check_rect.colliderect(platform.rect):
                if direction == "horizontal":
                    if self.vx > 0:
                        self.rect.right = platform.rect.left
                        if not self.is_grounded:
                            self.on_wall = 1
                        self.vx = 0
                    elif self.vx < 0:
                        self.rect.left = platform.rect.right
                        if not self.is_grounded:
                            self.on_wall = -1
                        self.vx = 0
                elif direction == "vertical":
                    if self.vy > 0:
                        self.rect.bottom = platform.rect.top
                        self.vy = 0
                        self.is_grounded = True
                    elif self.vy < 0:
                        self.rect.top = platform.rect.bottom
                        self.vy = 0


class Platform(pygame.sprite.Sprite):
    def __init__(self, x, y, width, height):
        super().__init__()
        self.image = pygame.Surface((width, height))
        self.image.fill(COLOR_PLATFORM)
        # Rim outline accent
        pygame.draw.rect(self.image, (52, 73, 94), (0, 0, width, height), 2)
        self.rect = self.image.get_rect(topleft=(x, y))


class Goal(pygame.sprite.Sprite):
    """ The portal or gate to progress levels """
    def __init__(self, x, y):
        super().__init__()
        self.image = pygame.Surface((40, 60))
        self.image.fill((155, 89, 182)) # Purple Portal
        pygame.draw.rect(self.image, (255, 255, 255), (5, 5, 30, 50), 2)
        self.rect = self.image.get_rect(topleft=(x, y))


# --- MAIN LOOP ---
def main():
    pygame.init()
    screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
    pygame.display.set_caption("Scratch Ninja Platformer Engine")
    clock = pygame.time.Clock()
    font = pygame.font.SysFont("Arial", 24)

    all_sprites = pygame.sprite.Group()
    platforms = pygame.sprite.Group()
    stars = pygame.sprite.Group()
    goals = pygame.sprite.Group()

    player = Player(80, 450)
    all_sprites.add(player)

    # Scratch Level Array Layout Maps
    levels = [
        # Level 1 Layout Map
        {
            "platforms": [
                (0, 550, 800, 50),     # Floor
                (0, 0, 20, 600),       # Left Bound Wall
                (780, 0, 20, 600),     # Right Bound Wall
                (250, 420, 160, 20),   # Jump step 1
                (480, 310, 160, 20),   # Jump step 2
                (200, 200, 200, 20),   # Goal platform
            ],
            "goal": (220, 140)
        },
        # Level 2 Layout Map (Emphasizing Wall Jumps)
        {
            "platforms": [
                (0, 550, 800, 50),
                (0, 0, 20, 600),
                (780, 0, 20, 600),
                (380, 280, 40, 270),   # Central pillar tower to scale
                (180, 420, 100, 20),
                (520, 420, 100, 20),
                (180, 220, 120, 20),
                (500, 140, 150, 20),
            ],
            "goal": (550, 80)
        }
    ]

    current_idx = 0

    def load_level(idx):
        # Wipe old assets clean
        for sprite in platforms: sprite.kill()
        for sprite in goals: sprite.kill()
        for sprite in stars: sprite.kill()

        # Build environments
        for p in levels[idx]["platforms"]:
            plat = Platform(*p)
            platforms.add(plat)
            all_sprites.add(plat)
        
        gx, gy = levels[idx]["goal"]
        goal = Goal(gx, gy)
        goals.add(goal)
        all_sprites.add(goal)

        # Reposition ninja to base
        player.rect.topleft = (80, 450)
        player.vx, player.vy = 0, 0

    load_level(current_idx)
    running = True
    win_state = False

    while running:
        # 1. Event Checks
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

        if not win_state:
            # 2. Update Actions & Variables
            player.handle_input(all_sprites, stars)
            player.update(platforms)
            stars.update(platforms)

            # Hit the purple portal trigger
            if pygame.sprite.spritecollideany(player, goals):
                current_idx += 1
                if current_idx < len(levels):
                    load_level(current_idx)
                else:
                    win_state = True

            # Drop off-screen reset loop
            if player.rect.top > SCREEN_HEIGHT:
                player.rect.topleft = (80, 450)
                player.vx, player.vy = 0, 0

        # 3. Graphics Rendering
        screen.fill(COLOR_BG)
        all_sprites.draw(screen)

        # UI & HUD Displays
        if win_state:
            txt = font.render("MISSION ACCOMPLISHED, SHINOBI!", True, COLOR_STAR)
            screen.blit(txt, (SCREEN_WIDTH // 2 - 180, SCREEN_HEIGHT // 2))
        else:
            hud = font.render(f"Level: {current_idx + 1}  | Controls: WASD/Arrows to Move/Wall Jump | F to Shoot", True, COLOR_TEXT)
            screen.blit(hud, (20, 20))

        pygame.display.flip()
        clock.tick(FPS)

    pygame.quit()
    sys.exit()

if __name__ == "__main__":
    main()
