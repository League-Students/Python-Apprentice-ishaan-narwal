import math
import random
import sys
import pygame

# --- Constants ---
WIDTH, HEIGHT = 800, 600
FPS = 60
PLAYER_SPEED = 5
BULLET_SPEED = 7

# Colors
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
RED = (255, 0, 0)
GREEN = (0, 255, 0)
BLUE = (0, 0, 255)
YELLOW = (255, 255, 0)

# Initialize
pygame.init()
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("2D Boss Rush Shooter")
clock = pygame.time.Clock()


# --- Classes ---
class Player(pygame.sprite.Sprite):

    def __init__(self):
        super().__init__()
        self.image = pygame.Surface((30, 30))
        self.image.fill(GREEN)
        self.rect = self.image.get_rect()
        self.rect.centerx = WIDTH // 2
        self.rect.bottom = HEIGHT - 20

    def update(self):
        keys = pygame.key.get_pressed()
        self.rect.x += (
            keys[pygame.K_d] - keys[pygame.K_a]
        ) * PLAYER_SPEED  # Only A and D are evaluated
        self.rect.clamp_ip(screen.get_rect())

    def shoot(self):
        return Bullet(self.rect.centerx, self.rect.top)


class Bullet(pygame.sprite.Sprite):

    def __init__(self, x, y):
        super().__init__()
        self.image = pygame.Surface((5, 15))
        self.image.fill(WHITE)
        self.rect = self.image.get_rect()
        self.rect.centerx = x
        self.rect.bottom = y

    def update(self):
        self.rect.y -= BULLET_SPEED
        if self.rect.bottom < 0:
            self.kill()


class Boss(pygame.sprite.Sprite):

    def __init__(self, tier):
        super().__init__()
        self.tier = tier
        size = 50 + (tier * 10)
        self.image = pygame.Surface((size, size))
        self.image.fill(RED)
        self.rect = self.image.get_rect()
        self.rect.x = random.randint(0, WIDTH - size)
        self.rect.y = 50

        # Boss attributes
        self.health = tier * 3
        self.max_health = self.health
        self.direction = 1
        self.speed = 2 + tier
        self.shoot_timer = 0
        self.shoot_interval = 60 - (tier * 8)

    def update(self):
        # Boss Movement
        self.rect.x += self.speed * self.direction
        if self.rect.right >= WIDTH or self.rect.left <= 0:
            self.direction *= -1

        # Boss Shooting
        self.shoot_timer += 1
        if self.shoot_timer >= self.shoot_interval:
            self.shoot_timer = 0
            return BossBullet(self.rect.centerx, self.rect.bottom, self.tier)
        return None

    def draw_health(self, surface):
        ratio = self.health / self.max_health
        pygame.draw.rect(
            surface, RED, (self.rect.x, self.rect.y - 15, self.rect.width, 10)
        )
        pygame.draw.rect(
            surface,
            GREEN,
            (
                self.rect.x,
                self.rect.y - 15,
                int(self.rect.width * ratio),
                10,
            ),
        )


class BossBullet(pygame.sprite.Sprite):

    def __init__(self, x, y, tier):
        super().__init__()
        self.image = pygame.Surface((10, 10))
        self.image.fill(YELLOW)
        self.rect = self.image.get_rect()
        self.rect.centerx = x
        self.rect.centery = y
        self.tier = tier

        # Trajectory towards player (simplified downward or tracking)
        self.dx = 0
        self.dy = 3 + tier

    def update(self):
        self.rect.x += self.dx
        self.rect.y += self.dy
        if self.rect.top > HEIGHT:
            self.kill()


# --- Game State ---
def draw_text(text, size, color, x, y):
    font = pygame.font.SysFont(None, size)
    img = font.render(text, True, color)
    screen.blit(img, (x, y))


def main():
    player = Player()
    all_sprites = pygame.sprite.Group()
    all_sprites.add(player)

    bullets = pygame.sprite.Group()
    enemy_bullets = pygame.sprite.Group()

    boss_tier = 1
    boss = Boss(boss_tier)
    all_sprites.add(boss)

    score = 0
    font = pygame.font.SysFont(None, 36)

    # Game Loop
    while True:
        clock.tick(FPS)
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_SPACE:
                    bullet = player.shoot()
                    all_sprites.add(bullet)
                    bullets.add(bullet)

        # Update
        all_sprites.update()

        # Boss Bullet Spawn
        result = boss.update()
        if isinstance(result, BossBullet):
            all_sprites.add(result)
            enemy_bullets.add(result)

        # Bullet -> Boss Collision
        hits = pygame.sprite.spritecollide(boss, bullets, True)
        for hit in hits:
            boss.health -= 1
            score += 10
            if boss.health <= 0:
                boss.kill()
                boss_tier += 1
                if boss_tier > 5:
                    # Victory State
                    screen.fill(BLACK)
                    draw_text("VICTORY! YOU DEFEATED ALL 5 BOSSES!", 48, GREEN, 80, 250)
                    pygame.display.flip()
                    pygame.time.wait(3000)
                    pygame.quit()
                    sys.exit()
                else:
                    boss = Boss(boss_tier)
                    all_sprites.add(boss)

        # Player -> Enemy Bullet Collision
        if pygame.sprite.spritecollideany(player, enemy_bullets):
            # Game Over State
            screen.fill(BLACK)
            draw_text("GAME OVER", 64, RED, 280, 250)
            pygame.display.flip()
            pygame.time.wait(3000)
            pygame.quit()
            sys.exit()

        # Draw
        screen.fill(BLACK)
        all_sprites.draw(screen)
        boss.draw_health(screen)

        # UI Drawing
        draw_text(f"Score: {score}", 24, WHITE, 10, 10)
        draw_text(f"Boss Tier: {boss_tier}/5", 24, WHITE, WIDTH - 150, 10)

        pygame.display.flip()


if __name__ == "__main__":
    main()
