import pygame
import random
import math

# Initialize Pygame
pygame.init()

# Screen Dimensions
WIDTH = 800
HEIGHT = 600
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Galactic Defender")

# Frame Rate
clock = pygame.time.Clock()
FPS = 60

# Colors
WHITE = (255, 255, 255)
RED = (255, 0, 0)
GREEN = (0, 255, 0)
BLUE = (0, 0, 255)
YELLOW = (255, 255, 0)
BLACK = (0, 0, 0)

# Fonts
font = pygame.font.SysFont(None, 36)
game_over_font = pygame.font.SysFont(None, 74)

# Score
score = 0

# --- Player Class ---
class Player(pygame.sprite.Sprite):
    def __init__(self):
        super().__init__()
        self.image = pygame.Surface((50, 40))
        self.image.fill(GREEN)
        self.rect = self.image.get_rect()
        self.rect.centerx = WIDTH // 2
        self.rect.bottom = HEIGHT - 10
        self.speed = 5
        self.health = 100

    def update(self):
        keys = pygame.key.get_pressed()
        if keys[pygame.K_LEFT] or keys[pygame.K_a]:
            self.rect.x -= self.speed
        if keys[pygame.K_RIGHT] or keys[pygame.K_d]:
            self.rect.x += self.speed
        if keys[pygame.K_UP] or keys[pygame.K_w]:
            self.rect.y -= self.speed
        if keys[pygame.K_DOWN] or keys[pygame.K_s]:
            self.rect.y += self.speed

        # Boundary checks
        if self.rect.left < 0: self.rect.left = 0
        if self.rect.right > WIDTH: self.rect.right = WIDTH
        if self.rect.top < 0: self.rect.top = 0
        if self.rect.bottom > HEIGHT: self.rect.bottom = HEIGHT

    def shoot(self):
        bullet = Bullet(self.rect.centerx, self.rect.top)
        all_sprites.add(bullet)
        bullets.add(bullet)

# --- Bullet Class ---
class Bullet(pygame.sprite.Sprite):
    def __init__(self, x, y):
        super().__init__()
        self.image = pygame.Surface((10, 20))
        self.image.fill(WHITE)
        self.rect = self.image.get_rect()
        self.rect.bottom = y
        self.rect.centerx = x
        self.speed = -10

    def update(self):
        self.rect.y += self.speed
        # Kill if it moves off-screen
        if self.rect.bottom < 0:
            self.kill()

# --- Enemy Class ---
class Enemy(pygame.sprite.Sprite):
    def __init__(self):
        super().__init__()
        self.image = pygame.Surface((30, 30))
        self.image.fill(RED)
        self.rect = self.image.get_rect()
        self.rect.x = random.randrange(WIDTH - self.rect.width)
        self.rect.y = random.randrange(-100, -40)
        self.speedy = random.randrange(1, 4)
        self.speedx = random.randrange(-2, 2)

    def update(self):
        self.rect.y += self.speedy
        self.rect.x += self.speedx
        
        # Boundary bounce
        if self.rect.right > WIDTH or self.rect.left < 0:
            self.speedx = -self.speedx

        if self.rect.top > HEIGHT:
            self.rect.x = random.randrange(WIDTH - self.rect.width)
            self.rect.y = random.randrange(-100, -40)
            self.speedy = random.randrange(1, 4)

# --- Boss Class ---
class Boss(pygame.sprite.Sprite):
    def __init__(self, level):
        super().__init__()
        self.level = level
        # Boss sizing and color based on level
        if level == 1:
            self.image = pygame.Surface((100, 80))
            self.image.fill(BLUE)
            self.health = 200
            self.max_health = 200
            self.speed = 2
        elif level == 2:
            self.image = pygame.Surface((120, 100))
            self.image.fill(YELLOW)
            self.health = 400
            self.max_health = 400
            self.speed = 3
        elif level == 3:
            self.image = pygame.Surface((160, 120))
            self.image.fill((255, 0, 255)) # Purple
            self.health = 600
            self.max_health = 600
            self.speed = 4

        self.rect = self.image.get_rect()
        self.rect.centerx = WIDTH // 2
        self.rect.y = 50
        self.direction = 1 # 1 for right, -1 for left

    def update(self):
        # Move side to side
        self.rect.x += self.speed * self.direction
        if self.rect.right > WIDTH:
            self.direction = -1
        elif self.rect.left < 0:
            self.direction = 1

    def take_damage(self, amount):
        self.health -= amount
        return self.health <= 0

# --- Helper Functions ---
def draw_text(surface, text, font, color, x, y):
    text_surface = font.render(text, True, color)
    text_rect = text_surface.get_rect()
    text_rect.midtop = (x, y)
    surface.blit(text_surface, text_rect)

def draw_health_bar(surface, x, y, current, maximum, color):
    if current < 0: current = 0
    bar_length = 200
    bar_height = 20
    fill = (current / maximum) * bar_length
    outline_rect = pygame.Rect(x, y, bar_length, bar_height)
    fill_rect = pygame.Rect(x, y, fill, bar_height)
    pygame.draw.rect(surface, color, fill_rect)
    pygame.draw.rect(surface, WHITE, outline_rect, 2)

# --- Sprite Groups ---
all_sprites = pygame.sprite.Group()
enemies = pygame.sprite.Group()
bullets = pygame.sprite.Group()
bosses = pygame.sprite.Group()

player = Player()
all_sprites.add(player)

# Spawn initial enemies
for i in range(8):
    enemy = Enemy()
    all_sprites.add(enemy)
    enemies.add(enemy)

# Game Loop Variables
game_over = False
victory = False
boss_fight = False
current_boss_level = 0
score_to_boss = 300 # Score needed to trigger boss 

# --- Game Loop ---
running = True
while running:
    # Keep loop running at the right speed
    clock.tick(FPS)

    # Process Input (Events)
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        elif event.type == pygame.KEYDOWN:
            if event.key == pygame.K_SPACE:
                if not game_over:
                    player.shoot()
            if event.key == pygame.K_r and game_over:
                # Reset game
                score = 0
                player.health = 100
                game_over = False
                victory = False
                boss_fight = False
                current_boss_level = 0
                
                # Clear all sprites
                for sprite in all_sprites:
                    sprite.kill()
                
                all_sprites.add(player)
                for i in range(8):
                    enemy = Enemy()
                    all_sprites.add(enemy)
                    enemies.add(enemy)

    if not game_over:
        # Check if it's time for a boss
        if score >= score_to_boss and not boss_fight and current_boss_level < 3:
            # Clear normal enemies for boss fight
            for enemy in enemies:
                enemy.kill()
            current_boss_level += 1
            boss = Boss(current_boss_level)
            all_sprites.add(boss)
            bosses.add(boss)
            boss_fight = True

        # Update
        all_sprites.update()

        # Check for bullet hitting an enemy
        hits = pygame.sprite.groupcollide(enemies, bullets, True, True)
        for hit in hits:
            score += 10
            # Spawn a new enemy to replace the dead one
            m = Enemy()
            all_sprites.add(m)
            enemies.add(m)

        # Check for bullet hitting the boss
        if boss_fight:
            boss_hits = pygame.sprite.groupcollide(bosses, bullets, False, True)
            for b in boss_hits:
                defeated = b.take_damage(10)
                if defeated:
                    b.kill()
                    boss_fight = False
                    score += 500 # Big boss bonus
                    
                    if current_boss_level >= 3:
                        victory = True
                        game_over = True
                    else:
                        # Resume normal enemies
                        for i in range(8):
                            enemy = Enemy()
                            all_sprites.add(enemy)
                            enemies.add(enemy)

        # Check for enemy hitting player
        hits = pygame.sprite.spritecollide(player, enemies, True)
        for hit in hits:
            player.health -= 20
            # Spawn new enemy
            m = Enemy()
            all_sprites.add(m)
            enemies.add(m)

        # Check if player died
        if player.health <= 0:
            game_over = True

    # Draw / Render
    screen.fill(BLACK)
    all_sprites.draw(screen)

    # Draw HUD
    draw_text(screen, f"Score: {score}", font, WHITE, WIDTH // 2, 10)
    draw_health_bar(screen, 10, 10, player.health, 100, GREEN)

    if boss_fight:
        # Assuming there is only one boss at a time in this group
        for b in bosses:
            draw_text(screen, f"BOSS Level {current_boss_level}", font, RED, WIDTH // 2, 40)
            draw_health_bar(screen, WIDTH // 2 - 100, 70, b.health, b.max_health, RED)

    if game_over:
        if victory:
            draw_text(screen, "VICTORY!", game_over_font, GREEN, WIDTH // 2, HEIGHT // 2 - 50)
            draw_text(screen, "Press 'R' to restart", font, WHITE, WIDTH // 2, HEIGHT // 2 + 20)
        else:
            draw_text(screen, "GAME OVER", game_over_font, RED, WIDTH // 2, HEIGHT // 2 - 50)
            draw_text(screen, "Press 'R' to restart", font, WHITE, WIDTH // 2, HEIGHT // 2 + 20)

    # Flip the display
    pygame.display.flip()

pygame.quit()
