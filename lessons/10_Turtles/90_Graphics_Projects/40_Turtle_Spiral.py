import pygame
import random
import os

# Initialize Engine Core
pygame.init()
WIDTH, HEIGHT = 1000, 600
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Space Shooter: Infinite Campaign")
clock = pygame.time.Clock()

# Color Systems
BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
RED = (255, 50, 50)
GREEN = (50, 255, 50)
YELLOW = (255, 255, 0)
ORANGE = (255, 128, 0)
DARK_GREEN = (30, 150, 30)
GRAY = (50, 50, 50)
PURPLE = (150, 50, 255)
CYAN = (0, 255, 255)
BLUE = (50, 100, 255)
GOLD = (218, 165, 32)
MAGENTA = (255, 0, 255)

# Global Font Engines
font = pygame.font.SysFont("Arial", 30)
button_font = pygame.font.SysFont("Arial", 24)

# Persistent High Score Tracker
HS_FILE = "highscore.txt"

def load_high_score():
    if os.path.exists(HS_FILE):
        try:
            with open(HS_FILE, "r") as f:
                return int(f.read().strip())
        except:
            return 0
    return 0

def save_high_score(new_high):
    with open(HS_FILE, "w") as f:
        f.write(str(new_high))

high_score = load_high_score()

# Game Classes: Projectiles and Hazards
class Laser:
    def __init__(self, x, y, is_boss=False, dx=0, speed_mult=1.0):
        self.width = 4
        self.height = 15
        self.x = x - self.width // 2
        self.y = y
        self.is_boss = is_boss
        # Boss projectile speeds escalate with new game loops
        self.speed_y = -int(6 * speed_mult) if is_boss else 3
        self.speed_x = dx

    def move(self):
        self.y -= self.speed_y
        self.x += self.speed_x

    def draw(self):
        color = ORANGE if self.is_boss else YELLOW
        pygame.draw.rect(screen, color, (self.x, self.y, self.width, self.height))

class Enemy:
    def __init__(self, speed_multiplier):
        self.size = random.randint(30, 50)
        self.x = random.randint(0, WIDTH - self.size)
        self.y = random.randint(-100, -40)
        self.speed = random.randint(3, 6) + int(speed_multiplier)

    def move(self):
        self.y += self.speed

    def draw(self):
        pygame.draw.ellipse(screen, RED, (self.x, self.y, self.size, self.size))

class PowerUp:
    def __init__(self, type_str):
        self.type = type_str
        self.size = 20
        self.x = random.randint(0, WIDTH - self.size)
        self.y = -50
        self.speed = 3

    def move(self):
        self.y += self.speed

    def draw(self):
        if self.type == "shield":
            pygame.draw.circle(screen, BLUE, (self.x + self.size // 2, self.y + self.size // 2), self.size // 2)
            pygame.draw.circle(screen, CYAN, (self.x + self.size // 2, self.y + self.size // 2), self.size // 2 - 3, 2)
        elif self.type == "firerate":
            points = [(self.x + self.size // 2, self.y), 
                      (self.x, self.y + self.size), 
                      (self.x + self.size, self.y + self.size)]
            pygame.draw.polygon(screen, YELLOW, points)
        elif self.type =="Heal":
            pygame.draw.square(screen, RED)
class Player:
    def __init__(self):
        self.width = 36
        self.height = 30
        self.x = WIDTH // 2 - self.width // 2
        self.y = HEIGHT - 50
        self.speed = 7
        self.max_health = 200
        self.health = 200
        self.shield_active = False
        self.shoot_cooldown = 0
        self.fire_rate_timer = 0

    def move(self, keys):
        if (keys[pygame.K_LEFT] or keys[pygame.K_a]) and self.x > 0:
            self.x -= self.speed
        if (keys[pygame.K_RIGHT] or keys[pygame.K_d]) and self.x < WIDTH - self.width:
            self.x += self.speed

    def shoot(self, player_lasers, keys):
        if self.shoot_cooldown > 0:
            self.shoot_cooldown -= 1
        if self.fire_rate_timer > 0:
            self.fire_rate_timer -= 1
            
        current_delay = 6 if self.fire_rate_timer > 0 else 10
        
        if keys[pygame.K_SPACE] and self.shoot_cooldown == 0:
            player_lasers.append(Laser(self.x + self.width // 2, self.y))
            self.shoot_cooldown = current_delay

    def draw(self):
        points = [(self.x + self.width // 2, self.y), 
                  (self.x, self.y + self.height), 
                  (self.x + self.width, self.y + self.height)]
        pygame.draw.polygon(screen, GREEN, points)
        if self.shield_active:
            pygame.draw.circle(screen, CYAN, (self.x + self.width // 2, self.y + self.height // 2), 26, 3)

class Boss:
    def __init__(self, relative_stage, loop_number):
        self.stage = relative_stage  # Always 1 through 5
        self.loop = loop_number      # Endless loop scaling index
        self.shoot_cooldown = 0
        self.phase = 1
        
        # Calculate dynamic global difficulty multipliers based on active loop layer
        self.loop_mult = 1.0 + (self.loop - 1) * 0.25

        if self.stage == 1:
            self.width, self.height = 160, 60
            self.max_health = int(100 * self.loop_mult)
            self.base_speed = 3 * self.loop_mult
            self.primary_color = PURPLE
        elif self.stage == 2:
            self.width, self.height = 140, 70
            self.max_health = int(150 * self.loop_mult)
            self.base_speed = 4.5 * self.loop_mult
            self.primary_color = CYAN
        elif self.stage == 3:
            self.width, self.height = 200, 80
            self.max_health = int(250 * self.loop_mult)
            self.base_speed = 2.5 * self.loop_mult
            self.primary_color = GOLD
        elif self.stage == 4:
            self.width, self.height = 170, 75
            self.max_health = int(320 * self.loop_mult)
            self.base_speed = 3.5 * self.loop_mult
            self.primary_color = ORANGE
        else: # Stage 5 - Final tier boss inside loop
            self.width, self.height = 220, 90
            self.max_health = int(450 * self.loop_mult)
            self.base_speed = 2.0 * self.loop_mult
            self.primary_color = MAGENTA

        self.health = self.max_health
        self.speed = self.base_speed
        self.x = WIDTH // 2 - self.width // 2
        self.y = 50

    def move(self):
        if self.health <= (self.max_health / 2) and self.phase == 1:
            self.phase = 2
            self.speed = self.base_speed * 1.8

        self.x += self.speed
        if self.x <= 0 or self.x >= WIDTH - self.width:
            self.speed *= -1

    def shoot(self, boss_lasers):
        if self.shoot_cooldown <= 0:
            # Scale firing pacing up slightly as loop limits elevate
            rate_mod = max(0.5, 2.0 - self.loop_mult)

            if self.stage == 1:
                if self.phase == 1:
                    boss_lasers.append(Laser(self.x + 20, self.y + self.height, True, 0, self.loop_mult))
                    boss_lasers.append(Laser(self.x + self.width - 20, self.y + self.height, True, 0, self.loop_mult))
                    self.shoot_cooldown = int(45 * rate_mod)
                else:
                    boss_lasers.append(Laser(self.x + self.width // 2, self.y + self.height, True, 0, self.loop_mult))
                    boss_lasers.append(Laser(self.x + 20, self.y + self.height, True, -2, self.loop_mult))
                    boss_lasers.append(Laser(self.x + self.width - 20, self.y + self.height, True, 2, self.loop_mult))
                    self.shoot_cooldown = int(35 * rate_mod)

            elif self.stage == 2:
                if self.phase == 1:
                    fire_x = self.x + 20 if pygame.time.get_ticks() % 400 < 200 else self.x + self.width - 20
                    boss_lasers.append(Laser(fire_x, self.y + self.height, True, 0, self.loop_mult))
                    self.shoot_cooldown = int(15 * rate_mod)
                else:
                    boss_lasers.append(Laser(self.x + self.width // 2, self.y + self.height, True, -1, self.loop_mult))
                    boss_lasers.append(Laser(self.x + self.width // 2, self.y + self.height, True, 1, self.loop_mult))
                    self.shoot_cooldown = int(12 * rate_mod)

            elif self.stage == 3:
                if self.phase == 1:
                    for offset in [20, 60, self.width - 60, self.width - 20]:
                        boss_lasers.append(Laser(self.x + offset, self.y + self.height, True, 0, self.loop_mult))
                    self.shoot_cooldown = int(50 * rate_mod)
                else:
                    for angle_dx in [-3, -1.5, 0, 1.5, 3]:
                        boss_lasers.append(Laser(self.x + self.width // 2, self.y + self.height, True, angle_dx, self.loop_mult))
                    self.shoot_cooldown = int(40 * rate_mod)

            elif self.stage == 4:
                # Stage 4: Moving sweeping perimeter columns
                if self.phase == 1:
                    boss_lasers.append(Laser(self.x + 10, self.y + self.height, True, -0.5, self.loop_mult))
                    boss_lasers.append(Laser(self.x + self.width - 10, self.y + self.height, True, 0.5, self.loop_mult))
                    self.shoot_cooldown = int(25 * rate_mod)
                else:
                    for offset in [10, self.width // 2, self.width - 10]:
                        boss_lasers.append(Laser(self.x + offset, self.y + self.height, True, -1.5, self.loop_mult))
                        boss_lasers.append(Laser(self.x + offset, self.y + self.height, True, 1.5, self.loop_mult))
                    self.shoot_cooldown = int(35 * rate_mod)

            else: # Stage 5 Vanguard Patterns
                if self.phase == 1:
                    for idx, offset in enumerate([30, 80, self.width - 80, self.width - 30]):
                        dx_val = -1 if idx < 2 else 1
                        boss_lasers.append(Laser(self.x + offset, self.y + self.height, True, dx_val, self.loop_mult))
                    self.shoot_cooldown = int(30 * rate_mod)
                else:
                    # Matrix geometric wall burst
                    for dx_val in [-4, -2.5, -1, 0, 1, 2.5, 4]:
                        boss_lasers.append(Laser(self.x + self.width // 2, self.y + self.height, True, dx_val, self.loop_mult))
                    self.shoot_cooldown = int(45 * rate_mod)
        else:
            self.shoot_cooldown -= 1

    def draw(self):
        color = self.primary_color if (self.phase == 1 or pygame.time.get_ticks() % 200 < 100) else RED
        points = [(self.x, self.y), 
                  (self.x + self.width, self.y), 
                  (self.x + self.width - 30, self.y + self.height), 
                  (self.x + 30, self.y + self.height)]
        pygame.draw.polygon(screen, color, points)
def draw_health_bar(screen, x, y, health, max_health, width=200, height=20, bar_color=None):
    fill_width = int((health / max_health) * width)
    if fill_width < 0: fill_width = 0
    if bar_color is None:
        if health > (max_health * 0.5): bar_color = GREEN
        elif health > (max_health * 0.2): bar_color = YELLOW
        else: bar_color = RED
    pygame.draw.rect(screen, GRAY, (x, y, width, height))
    pygame.draw.rect(screen, bar_color, (x, y, fill_width, height))
    pygame.draw.rect(screen, WHITE, (x, y, width, height), 2)

def reset_game():
    global player, lasers, enemies, powerups, boss, boss_active, score, game_over, current_stage, current_loop, stage_clear_timer
    player = Player()
    lasers = []
    enemies = []
    powerups = []
    boss = None
    boss_active = False
    score = 0
    current_stage = 1
    current_loop = 1
    stage_clear_timer = 0
    game_over = False
    
    # Spawn initial wave of enemies
    for _ in range(6):
        enemies.append(Enemy(speed_multiplier=1))
    pygame.mouse.set_visible(False)

def advance_stage():
    global current_stage, current_loop, boss, boss_active, lasers, enemies, powerups, stage_clear_timer
    
    # Clear out leftover entities from the boss fight
    lasers.clear()
    powerups.clear()
    enemies.clear()
    boss = None
    boss_active = False
    stage_clear_timer = 0
    
    # Progress stage index across infinite boundaries
    if current_stage < 5:
        current_stage += 1
    else:
        current_stage = 1
        current_loop += 1
        
    # Calculate compound difficulty modifier based on total stages depth
    total_stages_cleared = ((current_loop - 1) * 5) + current_stage
    
    # CRITICAL FIX: Explicitly generate a brand new active wave of falling red balls
    for _ in range(6):
        enemies.append(Enemy(speed_multiplier=total_stages_cleared))

button_width, button_height = 180, 50
restart_button_rect = pygame.Rect(WIDTH // 2 - button_width // 2, HEIGHT // 2 + 50, button_width, button_height)

# Launch Initial System State
reset_game()

running = True
while running:
    clock.tick(60)

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

        if event.type == pygame.MOUSEBUTTONDOWN and game_over:
            if event.button == 1 and restart_button_rect.collidepoint(event.pos):
                reset_game()

    if not game_over:
        if stage_clear_timer > 0:
            stage_clear_timer -= 1
            if stage_clear_timer == 0:
                advance_stage()
        else:
            keys = pygame.key.get_pressed()
            player.move(keys)
            player.shoot(lasers, keys)

            # Boss score thresholds scale linearly by 100 per stage deep
            total_stages_cleared = ((current_loop - 1) * 5) + current_stage
            target_score = total_stages_cleared * 100
            
            if score >= target_score and not boss_active:
                boss_active = True
                boss = Boss(current_stage, current_loop)
                enemies.clear()

            # Random item drop rates
            if random.randint(1, 450) == 1:
                item_type = "shield" if random.randint(1, 2) == 1 else "firerate"
                powerups.append(PowerUp(item_type))

            if boss_active and boss:
                boss.move()
                boss.shoot(lasers)

            for laser in lasers[:]:
                laser.move()
                if laser.y < 0 or laser.y > HEIGHT or laser.x < 0 or laser.x > WIDTH:
                    lasers.remove(laser)

            for pu in powerups[:]:
                pu.move()
                if pu.y > HEIGHT: powerups.remove(pu)

            # Only move and check collision for red balls if a boss is NOT currently active
            if not boss_active:
                # Fallback safeguard: if enemies list somehow goes empty outside a boss fight, refill it
                if len(enemies) == 0:
                    for _ in range(6):
                        enemies.append(Enemy(speed_multiplier=total_stages_cleared))

                for enemy in enemies[:]:
                    enemy.move()
                    if enemy.y > HEIGHT:
                        enemies.remove(enemy)
                        enemies.append(Enemy(speed_multiplier=total_stages_cleared))

                    player_rect = pygame.Rect(player.x, player.y, player.width, player.height)
                    enemy_rect = pygame.Rect(enemy.x, enemy.y, enemy.size, enemy.size)
                    
                    if player_rect.colliderect(enemy_rect):
                        enemies.remove(enemy)
                        enemies.append(Enemy(speed_multiplier=total_stages_cleared))
                        if player.shield_active: player.shield_active = False
                        else: player.health -= 20
                        if player.health <= 0:
                            game_over = True
                            pygame.mouse.set_visible(True)

            player_rect = pygame.Rect(player.x, player.y, player.width, player.height)
            for pu in powerups[:]:
                if player_rect.colliderect(pygame.Rect(pu.x, pu.y, pu.size, pu.size)):
                    if pu.type == "shield":
                        player.shield_active = True
                    elif pu.type == "firerate":
                        player.fire_rate_timer = 420
                    powerups.remove(pu)

            for laser in lasers[:]:
                laser_rect = pygame.Rect(laser.x, laser.y, laser.width, laser.height)
                if laser.is_boss:
                    if laser_rect.colliderect(player_rect):
                        if laser in lasers: lasers.remove(laser)
                        if player.shield_active: player.shield_active = False
                        else: player.health -= 15
                        if player.health <= 0:
                            game_over = True
                            pygame.mouse.set_visible(True)
                else:
                    if boss_active and boss:
                        if laser_rect.colliderect(pygame.Rect(boss.x, boss.y, boss.width, boss.height)):
                            boss.health -= 5
                            if laser in lasers: lasers.remove(laser)
                            if boss.health <= 0:
                                score += 150
                                stage_clear_timer = 120 # Freeze frame to show stage completion message
                    else:
                        for enemy in enemies[:]:
                            if laser_rect.colliderect(pygame.Rect(enemy.x, enemy.y, enemy.size, enemy.size)):
                                if laser in lasers: lasers.remove(laser)
                                enemies.remove(enemy)
                                score += 10
                                enemies.append(Enemy(speed_multiplier=total_stages_cleared))

            if score > high_score:
                high_score = score
                save_high_score(high_score)

    # Frame Buffer Draw Processing Engine
    screen.fill(BLACK)
    player.draw()
    for laser in lasers: laser.draw()
    for enemy in enemies: enemy.draw()
    for pu in powerups: pu.draw()
    if boss_active and boss: boss.draw()

    # Draw Text UI Overlays
    screen.blit(font.render(f"Score: {score}", True, WHITE), (10, 10))
    screen.blit(font.render(f"HI-Score: {high_score}", True, WHITE), (10, 45))
    screen.blit(font.render(f"Stage: {current_stage}", True, WHITE), (10, 80))
    if current_loop > 1:
        screen.blit(font.render(f"Loop: {current_loop}", True, GOLD), (10, 115))
        
    draw_health_bar(screen, WIDTH - 220, 15, player.health, player.max_health)
    
    if player.fire_rate_timer > 0:
        bar_y_offset = 150 if current_loop > 1 else 115
        draw_health_bar(screen, 10, bar_y_offset, player.fire_rate_timer, 420, width=120, height=8, bar_color=YELLOW)
        screen.blit(pygame.font.SysFont("Arial", 14).render("RAPID FIRE", True, YELLOW), (138, bar_y_offset - 4))
    
    if boss_active and boss:
        b_label = font.render(f"BOSS STAGE {boss.stage} (PHASE {boss.phase})", True, RED if boss.phase == 2 else boss.primary_color)
        screen.blit(b_label, (WIDTH // 2 - b_label.get_width() // 2, 10))
        draw_health_bar(screen, WIDTH // 2 - 150, 45, boss.health, boss.max_health, width=300, height=15, bar_color=boss.primary_color)

    if stage_clear_timer > 0:
        msg = f"STAGE {current_stage} CLEAR! WARPING..." if current_stage < 5 else f"LOOP {current_loop} COMPLETE! ENTERING NEW GALAXY LAYER..."
        clear_color = CYAN if current_stage < 5 else GOLD
        clear_banner = font.render(msg, True, clear_color)
        screen.blit(clear_banner, clear_banner.get_rect(center=(WIDTH // 2, HEIGHT // 2)))

    if game_over:
        display_text = font.render("GAME OVER", True, WHITE)
        screen.blit(display_text, display_text.get_rect(center=(WIDTH // 2, HEIGHT // 2 - 20)))
        
        btn_color = GREEN if restart_button_rect.collidepoint(pygame.mouse.get_pos()) else DARK_GREEN
        txt_color = BLACK if btn_color == GREEN else WHITE

        pygame.draw.rect(screen, btn_color, restart_button_rect, border_radius=5)
        btn_txt = button_font.render("Play Again", True, txt_color)
        screen.blit(btn_txt, btn_txt.get_rect(center=restart_button_rect.center))

    pygame.display.flip()

pygame.quit()