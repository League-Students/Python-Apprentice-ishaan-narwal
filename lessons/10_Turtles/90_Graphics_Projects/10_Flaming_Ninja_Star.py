import sys
import random
import pygame

# --- Constants ---
WIDTH, HEIGHT = 800, 600
FPS = 60
SCREEN_RECT = pygame.Rect(0, 0, WIDTH, HEIGHT)  # FIXED: Global reference to prevent NameError crashing

# Colors
COLOR_BG = (10, 12, 24)       
COLOR_PLAYER = (0, 210, 255)   
COLOR_BULLET = (0, 255, 150)   
COLOR_RED_BALL = (255, 40, 80) 
COLOR_SHIELD = (0, 150, 255)   
COLOR_RAPID = (255, 180, 0)    
COLOR_BOSS = (230, 0, 100)     
WHITE = (255, 255, 255)

# Initialize Pygame & Screen Globally
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
        alpha = int((self.speed / 3.0) * 155) + 100
        color = (alpha, alpha, alpha)
        pygame.draw.circle(surface, color, (int(self.x), int(self.y)), self.size)


class Player(pygame.sprite.Sprite):
    def __init__(self):
        super().__init__()
        self.image = pygame.Surface((40, 40), pygame.SRCALPHA)
        pygame.draw.polygon(self.image, COLOR_PLAYER, [(20, 0), (0, 40), (40, 40)])
        pygame.draw.polygon(self.image, WHITE, [(20, 10), (10, 35), (30, 35)], 2)
        
        self.rect = self.image.get_rect()
        self.rect.centerx = WIDTH // 2
        self.rect.bottom = HEIGHT - 30
        
        # Stats
        self.health = 100
        self.max_health = 100
        self.base_cooldown = 20  
        self.shoot_cooldown_timer = 0
        self.speed = 6
        self.rapid_fire_stacks = 0

    def update(self):
        keys = pygame.key.get_pressed()
        self.rect.x += (keys[pygame.K_d] - keys[pygame.K_a]) * self.speed
        self.rect.clamp_ip(SCREEN_RECT)  # FIXED: Uses global SCREEN_RECT instead of local screen variable
        
        if self.shoot_cooldown_timer > 0:
            self.shoot_cooldown_timer -= 1

    def shoot(self):
        actual_cooldown = max(2, self.base_cooldown - (self.rapid_fire_stacks * 3))
        if self.shoot_cooldown_timer == 0:
            self.shoot_cooldown_timer = actual_cooldown
            return Bullet(self.rect.centerx, self.rect.top)
        return None

    def draw_health_bar(self, surface):
        bar_width = 200
        bar_height = 15
        x = 20
        y = HEIGHT - 35
        pygame.draw.rect(surface, (50, 50, 50), (x, y, bar_width, bar_height))
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
        pygame.draw.circle(self.image, (255, 100, 120), (12, 12), 12)
        pygame.draw.circle(self.image, COLOR_RED_BALL, (12, 12), 9)
        self.rect = self.image.get_rect()
        self.rect.x = random.randint(10, WIDTH - 30)
        self.rect.y = random.randint(-100, -30)
        self.speed = random.uniform(2, 4)

    def update(self):
        self.rect.y += self.speed
        if self.rect.top > HEIGHT:
            self.rect.x = random.randint(10, WIDTH - 30)
            self.rect.y = random.randint(-100, -30)


class Boss(pygame.sprite.Sprite):
    def __init__(self, tier):
        super().__init__()
        self.tier = tier
        self.size = 60 + (tier * 10)
        
        self.image = pygame.Surface((self.size, self.size), pygame.SRCALPHA)
        pygame.draw.rect(self.image, COLOR_BOSS, (0, 0, self.size, self.size), border_radius=10)
        pygame.draw.polygon(self.image, WHITE, [(self.size//2, 10), (10, self.size-10), (self.size-10, self.size-10)], 4)
        
        self.rect = self.image.get_rect()
        self.rect.centerx = WIDTH // 2
        self.rect.y = 60

        self.health = tier * 30  
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
        self.damage = 10 + (tier * 2)  
        
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
        self.type = drop_type  
        self.image = pygame.Surface((22, 22), pygame.SRCALPHA)
        
        if self.type == "SHIELD":
            pygame.draw.circle(self.image, COLOR_SHIELD, (11, 11), 11)
            pygame.draw.rect(self.image, WHITE, (7, 5, 8, 12)) 
        else:
            pygame.draw.polygon(self.image, COLOR_RAPID, [(11, 0), (22, 22), (0, 22)]) 
            
        self.rect = self.image.get_rect()
        self.rect.centerx = x
        self.rect.centery = y
        self.speed = 3

    def update(self):
        self.rect.y += self.speed
        if self.rect.top > HEIGHT:
            self.kill()


# --- UI Helper ---
def draw_ui_text(surface, text, size, color, x, y):
    font = pygame.font.SysFont("Impact", size)
    img = font.render(text, True, color)
    surface.blit(img, (x, y))

def main():
    player = Player()
    
    bullets = pygame.sprite.Group()
    red_balls = pygame.sprite.Group()
    boss_group = pygame.sprite.GroupSingle()
    enemy_bullets = pygame.sprite.Group()
    drops = pygame.sprite.Group()

    stars = [BackgroundStar() for _ in range(60)]

    game_state = "BALLS"  
    boss_tier = 1
    balls_destroyed_this_phase = 0
    balls_needed = 30
    score = 0

    for _ in range(8):
        rb = RedBall()
        red_balls.add(rb)

    while True:
        clock.tick(FPS)
        
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()

        keys = pygame.key.get_pressed()
        if keys[pygame.K_SPACE] or keys[pygame.K_j]:
            b = player.shoot()
            if b:
                bullets.add(b)

        for star in stars:
            star.update()

        player.update()
        bullets.update()
        drops.update()
        enemy_bullets.update()

        if game_state == "BALLS":
            red_balls.update()
            if len(red_balls) < 8:
                rb = RedBall()
                red_balls.add(rb)
                
            hits = pygame.sprite.groupcollide(red_balls, bullets, True, True)
            for hit in hits:
                balls_destroyed_this_phase += 1
                score += 5
                
                if random.random() < 0.40:
                    d_type = "RAPID" if random.random() < 0.70 else "SHIELD"
                    drop = Drop(hit.rect.centerx, hit.rect.centery, d_type)
                    drops.add(drop)

                if balls_destroyed_this_phase >= balls_needed:
                    red_balls.empty()
                    enemy_bullets.empty() 
                    game_state = "BOSS"
                    boss_group.add(Boss(boss_tier))
                    balls_destroyed_this_phase = 0

        elif game_state == "BOSS":
            current_boss = boss_group.sprite
            if current_boss:
                boss_action = current_boss.update()
                if isinstance(boss_action, BossBullet):
                    enemy_bullets.add(boss_action)

                boss_hits = pygame.sprite.spritecollide(current_boss, bullets, True)
                for _ in boss_hits:
                    current_boss.health -= 1
                    score += 15
                    if current_boss.health <= 0:
                        current_boss.kill()
                        
                        if boss_tier >= 5:
                            screen.fill(COLOR_BG)
                            draw_ui_text(screen, "UNIVERSAL VICTORY!", 54, COLOR_BULLET, WIDTH // 4, HEIGHT // 2 - 30)
