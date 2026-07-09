import sys
import random
import pygame

# --- Constants ---
WIDTH, HEIGHT = 800, 600
FPS = 60

# Colors (Hex-inspired RGB equivalents for "Better Graphics" feel)
COLOR_BG = (10, 12, 24)       # Deep Space Blue/Black
COLOR_PLAYER = (0, 210, 255)   # Neon Cyan
COLOR_BULLET = (0, 255, 150)   # Plasma Green
COLOR_RED_BALL = (255, 40, 80) # Glowing Crimson
COLOR_SHIELD = (0, 150, 255)   # Shield Blue
COLOR_RAPID = (255, 180, 0)    # Energy Amber
COLOR_BOSS = (230, 0, 100)     # Magenta Red
WHITE = (255, 255, 255)

# Initialize
pygame.init()
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Ultimate Space Boss Rush")
clock = pygame.time.Clock()

# --- Classes ---
class BackgroundStar:
    def __init__(self):
        self.x = random.randint(0, WIDTH)
        self.y = random.randint(0, HEIGHT)
        self.speed = random.uniform(0.5, 3.0)
        self.size = random.randint(1, 3)

    def update(self):
        self.y += self.speed
        if self.y > HEIGHT:
            self.y = 0
            self.x = random.randint(0, WIDTH)

    def draw(self, surface):
        # Brighter stars move faster (parallax effect)
        alpha = int((self.speed / 3.0) * 155) + 100
        color = (alpha, alpha, alpha)
        pygame.draw.circle(surface, color, (int(self.x), int(self.y)), self.size)


class Player(pygame.sprite.Sprite):
    def __init__(self):
        super().__init__()
        # Better Graphic: Sleek spaceship triangle shape using vectors
        self.image = pygame.Surface((40, 40), pygame.SRCALPHA)
        pygame.draw.polygon(self.image, COLOR_PLAYER, [(20, 0), (0, 40), (40, 40)])
        pygame.draw.polygon(self.image, WHITE, [(20, 10), (10, 35), (30, 35)], 2) # Inner detail
        
        self.rect = self.image.get_rect()
        self.rect.centerx = WIDTH // 2
        self.rect.bottom = HEIGHT - 30
        
        # Stats
        self.health = 100
        self.max_health = 100
        self.base_cooldown = 20  # Frames between shots
        self.shoot_cooldown_timer = 0
        self.speed = 6
        
        # Upgrade stacks
        self.rapid_fire_stacks = 0

    def update(self):
        keys = pygame.key.get_pressed()
        # WASD layout but strictly stripping vertical mapping
        self.rect.x += (keys[pygame.K_d] - keys[pygame.K_a]) * self.speed
        self.rect.clamp_ip(screen.get_rect())
        
        if self.shoot_cooldown_timer > 0:
            self.shoot_cooldown_timer -= 1

    def shoot(self):
        # Stack formula: piling up cuts down the frame delay significantly
        # E.g., 0 stacks = 20 frames, 5 stacks = 5 frames, 10 stacks = 2 frames!
        actual_cooldown = max(2, self.base_cooldown - (self.rapid_fire_stacks * 3))
        
        if self.shoot_cooldown_timer == 0:
            self.shoot_cooldown_timer = actual_cooldown
            return Bullet(self.rect.centerx, self.rect.top)
        return None

    def draw_health_bar(self, surface):
        # Dynamic HUD Health Bar at bottom
        bar_width = 200
        bar_height = 15
        x = 20
        y = HEIGHT - 35
        
        # Border / BG
        pygame.draw.rect(surface, (50, 50, 50), (x, y, bar_width, bar_height))
        # Health Fill
        fill_width = int((self.health / self.max_health) * bar_width)
        if fill_width > 0:
            pygame.draw.rect(surface, COLOR_PLAYER, (x, y, fill_width, bar_height))
        pygame.draw.rect(surface, WHITE, (x, y, bar_width, bar_height), 2)


class Bullet(pygame.sprite.Sprite):
    def __init__(self, x, y):
        super().__init__()
        self.image = pygame.Surface((6, 16), pygame.SRCALPHA)
        pygame.draw.rect(self.image, COLOR_BULLET, (0, 0, 6, 16), border_radius=3)
        self.rect = self.image.get_rect()
        self.rect.centerx = x
        self.rect.bottom = y
        self.speed = 9

    def update(self):
        self.rect.y -= self.speed
        if self.rect.bottom < 0:
            self.kill()


class RedBall(pygame.sprite.Sprite):
    def __init__(self):
        super().__init__()
        self.image = pygame.Surface((24, 24), pygame.SRCALPHA)
        # Glow graphic effect
        pygame.draw.circle(self.image, (255, 100, 120), (12, 12), 12)
        pygame.draw.circle(self.image, COLOR_RED_BALL, (12, 12), 9)
        self.rect = self.image.get_rect()
        self.rect.x = random.randint(10, WIDTH - 30)
        self.rect.y = random.randint(-100, -30)
        self.speed = random.uniform(2, 4)

    def update(self):
        self.rect.y += self.speed
        if self.rect.top > HEIGHT:
            # Recycle to prevent running out of balls
            self.rect.x = random.randint(10, WIDTH - 30)
            self.rect.y = random.randint(-100, -30)


class Boss(pygame.sprite.Sprite):
    def __init__(self, tier):
        super().__init__()
        self.tier = tier
        self.size = 60 + (tier * 10)
        
        self.image = pygame.Surface((self.size, self.size), pygame.SRCALPHA)
        # Menacing geometric layout
        pygame.draw.rect(self.image, COLOR_BOSS, (0, 0, self.size, self.size), border_radius=10)
        pygame.draw.polygon(self.image, WHITE, [(self.size//2, 10), (10, self.size-10), (self.size-10, self.size-10)], 4)
        
        self.rect = self.image.get_rect()
        self.rect.centerx = WIDTH // 2
        self.rect.y = 60

        self.health = tier * 30  # Enhanced health pools for bars
        self.max_health = self.health
        self.direction = 1
        self.speed = 2 + (tier * 0.5)
        self.shoot_timer = 0
        self.shoot_interval = max(15, 50 - (tier * 6))

    def update(self):
        self.rect.x += self.speed * self.direction
        if self.rect.right >= WIDTH - 10 or self.rect.left <= 10:
            self.direction *= -1

        self.shoot_timer += 1
        if self.shoot_timer >= self.shoot_interval:
            self.shoot_timer = 0
            return BossBullet(self.rect.centerx, self.rect.bottom, self.tier)
        return None

    def draw_health_bar(self, surface):
        ratio = max(0.0, self.health / self.max_health)
        bar_w = 400
        bx = (WIDTH - bar_w) // 2
        by = 25
        pygame.draw.rect(surface, (60, 20, 30), (bx, by, bar_w, 12))
        pygame.draw.rect(surface, COLOR_BOSS, (bx, by, int(bar_w * ratio), 12))
        pygame.draw.rect(surface, WHITE, (bx, by, bar_w, 12), 2)


class BossBullet(pygame.sprite.Sprite):
    def __init__(self, x, y, tier):
        super().__init__()
        self.image = pygame.Surface((12, 12), pygame.SRCALPHA)
        pygame.draw.circle(self.image, (255, 255, 100), (6, 6), 6)
        self.rect = self.image.get_rect()
        self.rect.centerx = x
        self.rect.centery = y
        self.damage = 10 + (tier * 2)  # Survives multiple hits
        
        # Simple varied tracking angles based on Tier level
        self.dy = 4 + tier
        self.dx = random.choice([-1.5, 0, 1.5]) if tier >= 3 else 0

    def update(self):
        self.rect.x += self.dx
        self.rect.y += self.dy
        if self.rect.top > HEIGHT:
            self.kill()


class Drop(pygame.sprite.Sprite):
    def __init__(self, x, y, drop_type):
        super().__init__()
        self.type = drop_type  # "SHIELD" or "RAPID"
        self.image = pygame.Surface((22, 22), pygame.SRCALPHA)
        
        if self.type == "SHIELD":
            pygame.draw.circle(self.image, COLOR_SHIELD, (11, 11), 11)
            pygame.draw.rect(self.image, WHITE, (7, 5, 8, 12)) # 'S' Shape stand-in icon
        else:
            pygame.draw.polygon(self.image, COLOR_RAPID, [(11, 0), (22, 22), (0, 22)]) # Bolt icon
            
        self.rect = self.image.get_rect()
        self.rect.centerx = x
        self.rect.centery = y
        self.speed = 3

    def update(self):
        self.rect.y += self.speed
        if self.rect.top > HEIGHT:
            self.kill()


# --- Game Engine Loop ---
def draw_ui_text(text, size, color, x, y):
    font = pygame.font.SysFont("Impact", size)
    img = font.render(text, True, color)
    screen.blit(img, (x, y))

def main():
    player = Player()
    
    # Sprite Group Management
    all_sprites = pygame.sprite.Group()
    all_sprites.add(player)
    
    bullets = pygame.sprite.Group()
    red_balls = pygame.sprite.Group()
    boss_group = pygame.sprite.GroupSingle()
    enemy_bullets = pygame.sprite.Group()
    drops = pygame.sprite.Group()

    # Dynamic Starfield Setup
    stars = [BackgroundStar() for _ in range(60)]

    # State Variables
    game_state = "BALLS"  # Options: "BALLS" or "BOSS"
    boss_tier = 1
    balls_destroyed_this_phase = 0
    balls_needed = 30
    score = 0

    # Initial Red Balls Spawn Loop
    for _ in range(8):
        rb = RedBall()
        all_sprites.add(rb)
        red_balls.add(rb)

    while True:
        clock.tick(FPS)
        
        # Inputs & Events
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()

        # Continuous automatic/held shooting mechanism
        keys = pygame.key.get_pressed()
        if keys[pygame.K_SPACE] or keys[pygame.K_j]:
            b = player.shoot()
            if b:
                all_sprites.add(b)
                bullets.add(b)

        # Starfield Calculations First
        for star in stars:
            star.update()

        # Standard Sprite Processing Updates
        all_sprites.update()

        # Handle State Behaviors (Ball Clearing Mode vs Active Boss Fights)
        if game_state == "BALLS":
            # Keep keeping ball counts steady up to 8 max on-screen
            if len(red_balls) < 8:
                rb = RedBall()
                all_sprites.add(rb)
                red_balls.add(rb)
                
            # Collisions: Player Bullets hitting Red Balls
            hits = pygame.sprite.groupcollide(red_balls, bullets, True, True)
            for hit in hits:
                balls_destroyed_this_phase += 1
                score += 5
                
