import pygame
import random
import math

# --- Initialization ---
pygame.init()
WIDTH, HEIGHT = 800, 600
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Galactic Defender: Striker Edition")
clock = pygame.time.Clock()
FPS = 60

# --- Colors & Fonts ---
FONT_MAIN = pygame.font.SysFont("Arial", 22, bold=True)
FONT_TITLE = pygame.font.SysFont("Arial", 48, bold=True)

COLOR_BG = (10, 8, 22)
COLOR_PLAYER = (0, 255, 150)
COLOR_SHIELD = (0, 190, 255)
COLOR_ENEMY = (255, 60, 60)
COLOR_BULLET_P = (0, 255, 255)
COLOR_BULLET_B = (255, 130, 0)
COLOR_TEXT = (240, 240, 255)

# --- Particles ---
class Particle(pygame.sprite.Sprite):
    def __init__(self, x, y, color):
        super().__init__()
        self.image = pygame.Surface((4, 4), pygame.SRCALPHA)
        self.color = color
        self.rect = self.image.get_rect(center=(x, y))
        self.angle = random.uniform(0, math.pi * 2)
        self.speed = random.uniform(2, 6)
        self.alpha = 255
        self.decay = random.uniform(6, 12)

    def update(self):
        self.rect.x += math.cos(self.angle) * self.speed
        self.rect.y += math.sin(self.angle) * self.speed
        self.alpha -= self.decay
        if self.alpha <= 0:
            self.kill()
        else:
            self.image.fill((0, 0, 0, 0))
            pygame.draw.circle(self.image, (*self.color, int(self.alpha)), (2, 2), 2)

# --- Drops / Power-ups ---
class PowerUp(pygame.sprite.Sprite):
    def __init__(self, x, y, type):
        super().__init__()
        self.type = type # "SHIELD" or "RAPID"
        self.image = pygame.Surface((24, 24), pygame.SRCALPHA)
        self.rect = self.image.get_rect(center=(x, y))
        self.speed_y = 3
        
        if self.type == "SHIELD":
            pygame.draw.circle(self.image, COLOR_SHIELD, (12, 12), 10, 2)
            pygame.draw.circle(self.image, COLOR_SHIELD, (12, 12), 5)
        elif self.type == "RAPID":
            # Drawing a lightning bolt shape
            pygame.draw.polygon(self.image, (255, 255, 0), [(14, 2), (6, 12), (12, 12), (10, 22), (18, 12), (12, 12)])

    def update(self):
        self.rect.y += self.speed_y
        if self.rect.top > HEIGHT:
            self.kill()

# --- Player ---
class Player(pygame.sprite.Sprite):
    def __init__(self):
        super().__init__()
        self.image = pygame.Surface((50, 40), pygame.SRCALPHA)
        pygame.draw.polygon(self.image, COLOR_PLAYER, [(25, 0), (0, 40), (25, 30), (50, 40)])
        self.rect = self.image.get_rect(centerx=WIDTH // 2, bottom=HEIGHT - 30)
        self.speed = 7
        self.max_health = 100
        self.health = self.max_health
        self.fire_cooldown = 0
        
        # Power-up states
        self.shield_timer = 0
        self.rapid_timer = 0

    def update(self):
        # Timers
        if self.fire_cooldown > 0: self.fire_cooldown -= 1
        if self.shield_timer > 0:  self.shield_timer -= 1
        if self.rapid_timer > 0:   self.rapid_timer -= 1
            
        # Visual styling changes if shielded
        self.image.fill((0, 0, 0, 0))
        if self.shield_timer > 0:
            pygame.draw.polygon(self.image, COLOR_SHIELD, [(25, 0), (0, 40), (25, 30), (50, 40)])
            pygame.draw.circle(self.image, COLOR_SHIELD, (25, 22), 24, 2)
        else:
            pygame.draw.polygon(self.image, COLOR_PLAYER, [(25, 0), (0, 40), (25, 30), (50, 40)])

        # Left / Right Movement Only (Vertical logic completely removed)
        keys = pygame.key.get_pressed()
        if keys[pygame.K_LEFT] or keys[pygame.K_a]:
            self.rect.x -= self.speed
        if keys[pygame.K_RIGHT] or keys[pygame.K_d]:
            self.rect.x += self.speed
        
        self.rect.x = max(0, min(WIDTH - self.rect.width, self.rect.x))

        # Firing weapon mechanics
        if keys[pygame.K_SPACE] and self.fire_cooldown == 0:
            self.shoot()

    def shoot(self):
        # Cooldown is 4 frames if rapid fire is active, otherwise 14 frames
        self.fire_cooldown = 4 if self.rapid_timer > 0 else 14
        b1 = Bullet(self.rect.left + 5, self.rect.top + 10, -12, COLOR_BULLET_P)
        b2 = Bullet(self.rect.right - 5, self.rect.top + 10, -12, COLOR_BULLET_P)
        all_sprites.add(b1, b2)
        player_bullets.add(b1, b2)

# --- Normal Enemies ---
class Enemy(pygame.sprite.Sprite):
    def __init__(self):
        super().__init__()
        self.image = pygame.Surface((32, 32), pygame.SRCALPHA)
        pygame.draw.polygon(self.image, COLOR_ENEMY, [(16, 0), (32, 16), (16, 32), (0, 16)])
        self.rect = self.image.get_rect(x=random.randrange(WIDTH - 32), y=random.randrange(-150, -40))
        self.speed_y = random.uniform(2, 4)
        self.wobble = random.uniform(0, 100)

    def update(self):
        self.rect.y += self.speed_y
        self.wobble += 0.05
        self.rect.x += math.sin(self.wobble) * 2
        if self.rect.top > HEIGHT:
            self.reset_position()

    def reset_position(self):
        self.rect.x = random.randrange(WIDTH - self.rect.width)
        self.rect.y = random.randrange(-150, -40)
        self.speed_y = random.uniform(2, 4)

class Bullet(pygame.sprite.Sprite):
    def __init__(self, x, y, speed_y, color, speed_x=0):
        super().__init__()
        self.image = pygame.Surface((6, 16), pygame.SRCALPHA)
        pygame.draw.rect(self.image, color, (0, 0, 6, 16), border_radius=3)
        self.rect = self.image.get_rect(center=(x, y))
        self.speed_y = speed_y
        self.speed_x = speed_x

    def update(self):
        self.rect.y += self.speed_y
        self.rect.x += self.speed_x
        if self.rect.bottom < 0 or self.rect.top > HEIGHT or self.rect.right < 0 or self.rect.left > WIDTH:
            self.kill()

# --- Progressive 5-Tier Boss System ---
class Boss(pygame.sprite.Sprite):
    def __init__(self, tier):
        super().__init__()
        self.tier = tier
        
        # Scale sizes and health formulas dynamically based on Tier
        width = 100 + (tier * 20)
        height = 60 + (tier * 12)
        self.image = pygame.Surface((width, height), pygame.SRCALPHA)
        
        # Color spectrum shifting darker/more menacing per tier
        self.color = (min(50 * tier, 255), 255 - (45 * tier), 255 if tier == 1 else 30)
        pygame.draw.rect(self.image, self.color, (0, 0, width, height // 2), border_radius=10)
        pygame.draw.polygon(self.image, self.color, [(0, height // 2), (width, height // 2), (width // 2, height)])

        self.max_health = 200 * tier
        self.health = self.max_health
        self.speed = 2 + tier * 0.7
        self.rect = self.image.get_rect(centerx=WIDTH // 2, y=50)
        self.direction = 1
        self.attack_timer = 0

    def update(self):
        self.rect.x += self.speed * self.direction
        if self.rect.right >= WIDTH or self.rect.left <= 0:
            self.direction *= -1

        self.attack_timer += 1
        self.fire_patterns()

    def fire_patterns(self):
        # Boss 1: Slow Triple Stream
        if self.tier == 1 and self.attack_timer % 45 == 0:
            for dx in [-2, 0, 2]:
                all_sprites.add(Bullet(self.rect.centerx, self.rect.bottom, 5, COLOR_BULLET_B, dx))
                boss_bullets.add(Bullet(self.rect.centerx, self.rect.bottom, 5, COLOR_BULLET_B, dx))

        # Boss 2: Double Spread + Faster
        elif self.tier == 2 and self.attack_timer % 40 == 0:
            for offset in [-30, 30]:
                all_sprites.add(Bullet(self.rect.centerx + offset, self.rect.bottom, 6, COLOR_BULLET_B, 0))
                boss_bullets.add(Bullet(self.rect.centerx + offset, self.rect.bottom, 6, COLOR_BULLET_B, 0))

        # Boss 3: Radial 5-Shot Fan
        elif self.tier == 3 and self.attack_timer % 35 == 0:
            for dx in [-4, -2, 0, 2, 4]:
                all_sprites.add(Bullet(self.rect.centerx, self.rect.bottom, 6, COLOR_BULLET_B, dx))
                boss_bullets.add(Bullet(self.rect.centerx, self.rect.bottom, 6, COLOR_BULLET_B, dx))

        # Boss 4: Targeted Aiming Vectors
        elif self.tier == 4 and self.attack_timer % 30 == 0:
            tx = player.rect.centerx - self.rect.centerx
            ty = player.rect.centery - self.rect.bottom
            dist = math.hypot(tx, ty) or 1
            all_sprites.add(Bullet(self.rect.centerx, self.rect.bottom, (ty/dist)*7, (255, 0, 0), (tx/dist)*7))
            boss_bullets.add(Bullet(self.rect.centerx, self.rect.bottom, (ty/dist)*7, (255, 0, 0), (tx/dist)*7))

        # Boss 5 (FINAL): Rapid Rain Hellfire
        elif self.tier == 5 and self.attack_timer % 12 == 0:
            rx = random.uniform(-5, 5)
            all_sprites.add(Bullet(random.randint(self.rect.left, self.rect.right), self.rect.bottom, 8, (255, 255, 0), rx))
            boss_bullets.add(Bullet(random.randint(self.rect.left, self.rect.right), self.rect.bottom, 8, (255, 255, 0), rx))

# --- Spawning Helpers ---
def create_explosion(x, y, color=COLOR_ENEMY, count=12):
    for _ in range(count):
        all_sprites.add(Particle(x, y, color))

def spawn_enemies(count):
    for _ in range(count):
        e = Enemy()
        all_sprites.add(e)
        enemies.add(e)

# --- Setup Sprite Engine Containers ---
all_sprites = pygame.sprite.Group()
enemies = pygame.sprite.Group()
player_bullets = pygame.sprite.Group()
boss_bullets = pygame.sprite.Group()
bosses = pygame.sprite.Group()
powerups = pygame.sprite.Group()

player = Player()
all_sprites.add(player)
spawn_enemies(6)

# --- Mechanics System Trackers ---
score = 0
red_kills = 0
boss_tier = 0
active_boss = None
game_state = "PLAYING"

# --- Main Runtime Loop ---
running = True
while running:
    clock.tick(FPS)
    screen.fill(COLOR_BG)

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        elif event.type == pygame.KEYDOWN and game_state != "PLAYING":
            if event.key == pygame.K_r: # Full software state reconstruction
