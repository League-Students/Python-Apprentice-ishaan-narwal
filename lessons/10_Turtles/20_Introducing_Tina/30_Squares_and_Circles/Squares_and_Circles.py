import pygame
import sys
import math
import random

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
    def __init__(self, x, y, direction):
        super().__init__()
        self.image = pygame.Surface((12, 12), pygame.SRCALPHA)
        pygame.draw.polygon(self.image, COLOR_STAR, [(6,0), (12,6), (6,12), (0,6)])
        self.rect = self.image.get_rect(center=(x, y))
        self.speed = 12 * direction
        self.life = 40  

    def update(self, platforms):
        self.rect.x += self.speed
        self.life -= 1
        if pygame.sprite.spritecollideany(self, platforms) or self.life <= 0:
            self.kill()


class Player(pygame.sprite.Sprite):
    def __init__(self, x, y):
        super().__init__()
        self.image = pygame.Surface((32, 44))
        self.image.fill(COLOR_PLAYER)
        pygame.draw.rect(self.image, (255, 255, 255), (0, 8, 12, 6)) 
        
        self.rect = self.image.get_rect()
        self.rect.topleft = (x, y)

        self.vx = 0
        self.vy = 0
        self.is_grounded = False
        self.facing_direction = 1  
        self.on_wall = 0          
        self.shoot_cooldown = 0
        
        # Double Jump properties
        self.max_jumps = 2
        self.jumps_remaining = 2
        self.jump_key_pressed = False

    def handle_input(self, all_sprites, stars):
        keys = pygame.key.get_pressed()
        
        if keys[pygame.K_LEFT] or keys[pygame.K_a]:
            self.vx -= RUN_SPEED
            self.facing_direction = -1
        elif keys[pygame.K_RIGHT] or keys[pygame.K_d]:
            self.vx += RUN_SPEED
            self.facing_direction = 1

        # Jump Input with single-press validation (prevents instantly consuming both jumps)
        jump_key = keys[pygame.K_UP] or keys[pygame.K_w] or keys[pygame.K_SPACE]
        if jump_key:
            if not self.jump_key_pressed:
                self.jump_key_pressed = True
                
                # Case 1: Ground Jump
                if self.is_grounded:
                    self.vy = JUMP_FORCE
                    self.is_grounded = False
                    self.jumps_remaining -= 1
                # Case 2: Wall Jump (Takes precedence over double jump while on a wall)
                elif self.on_wall != 0:  
                    self.vy = JUMP_FORCE
                    self.vx = -self.on_wall * (MAX_SPEED * 1.2)  
                    self.on_wall = 0
                    self.jumps_remaining = self.max_jumps - 1 # Grant a double jump fresh off a wall kick
                # Case 3: Mid-air Double Jump
                elif self.jumps_remaining > 0:
                    self.vy = JUMP_FORCE
                    self.jumps_remaining -= 1
        else:
            self.jump_key_pressed = False

        if (keys[pygame.K_f] or keys[pygame.K_RETURN]) and self.shoot_cooldown == 0:
            star = NinjaStar(self.rect.centerx, self.rect.centery, self.facing_direction)
            all_sprites.add(star)
            stars.add(star)
            self.shoot_cooldown = 15  

        if self.shoot_cooldown > 0:
            self.shoot_cooldown -= 1

    def update(self, platforms):
        self.vx *= FRICTION
        self.vy += GRAVITY

        if abs(self.vx) > MAX_SPEED:
            self.vx = math.copysign(MAX_SPEED, self.vx)
        
        if self.on_wall != 0 and self.vy > WALL_SLIDE_SPEED:
            self.vy = WALL_SLIDE_SPEED
            self.jumps_remaining = self.max_jumps # Reset jumps while sliding down walls

        self.rect.x += int(self.vx)
        self.on_wall = 0
        self.collide_with_platforms(platforms, "horizontal")

        self.rect.y += int(self.vy)
        self.is_grounded = False
        self.collide_with_platforms(platforms, "vertical")

    def collide_with_platforms(self, platforms, direction):
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
                        self.jumps_remaining = self.max_jumps # Reset jumps when touching the floor
                    elif self.vy < 0:
                        self.rect.top = platform.rect.bottom
                        self.vy = 0


class Platform(pygame.sprite.Sprite):
    def __init__(self, x, y, width, height):
        super().__init__()
        self.image = pygame.Surface((width, height))
        self.image.fill(COLOR_PLATFORM)
        pygame.draw.rect(self.image, (52, 73, 94), (0, 0, width, height), 2)
        self.rect = self.image.get_rect(topleft=(x, y))


class Goal(pygame.sprite.Sprite):
    def __init__(self, x, y):
        super().__init__()
        self.image = pygame.Surface((40, 60))
        self.image.fill((155, 89, 182)) 
        pygame.draw.rect(self.image, (255, 255, 255), (5, 5, 30, 50), 2)
        self.rect = self.image.get_rect(topleft=(x, y))


# --- PROCEDURAL GENERATOR ALGORITHM WITH TUTORIAL BYPASS ---
def generate_procedural_level(level_num):
    """ Builds a guaranteed easy Level 1, then procedural maps up to level 500 """
    level_data = {"platforms": [], "goal": (0, 0)}
    
    level_data["platforms"].append((0, 0, 20, 600))
    level_data["platforms"].append((780, 0, 20, 600))
    
    if level_num == 1:
        level_data["platforms"].extend([
            (0, 530, 300, 70),    
            (350, 440, 150, 20),   
            (550, 350, 180, 20),   
            (300, 250, 200, 20),   
            (80, 180, 160, 20)     
        ])
        level_data["goal"] = (140, 120)
        return level_data

    random.seed(level_num + 999)
    level_data["platforms"].append((0, 530, 200, 70)) 
    
    progression = min(level_num / 500.0, 1.0)
    min_width = int(120 - (progression * 50))  
    max_width = int(180 - (progression * 60))  
    
    current_x = 150
    current_y = 450
    
    while current_y > 150:
        p_width = random.randint(min_width, max_width)
        p_height = 20
        
        if random.random() < 0.25 * progression:
            level_data["platforms"].append((current_x + 30, current_y - 80, 40, 100))
            current_y -= 120
        else:
            level_data["platforms"].append((current_x, current_y, p_width, p_height))
            gap_x = random.randint(80, int(120 + (progression * 50))) 
            gap_y = random.randint(70, 95)
            
            if current_x + p_width + gap_x > 740:
                current_x = random.randint(40, 150)
            else:
                current_x += p_width + gap_x
                
            current_y -= gap_y

    goal_platform_x = random.randint(100, 500)
    level_data["platforms"].append((goal_platform_x, 130, 150, 20))
    level_data["goal"] = (goal_platform_x + 55, 70)
    
    return level_data


# --- MAIN LOOP ---
def main():
    pygame.init()
    screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
    pygame.display.set_caption("Scratch Ninja - 500 Level Edition")
    clock = pygame.time.Clock()
    font = pygame.font.SysFont("Arial", 24)

    all_sprites = pygame.sprite.Group()
    platforms = pygame.sprite.Group()
    stars = pygame.sprite.Group()
    goals = pygame.sprite.Group()

    player = Player(40, 450)
    all_sprites.add(player)

    current_idx = 1  
    MAX_LEVELS = 500

    def load_level(idx):
        for sprite in platforms: sprite.kill()
        for sprite in goals: sprite.kill()
        for sprite in stars: sprite.kill()

        generated_level = generate_procedural_level(idx)
        
        for p in generated_level["platforms"]:
            plat = Platform(*p)
            platforms.add(plat)
            all_sprites.add(plat)
        
        gx, gy = generated_level["goal"]
        goal = Goal(gx, gy)
        goals.add(goal)
        all_sprites.add(goal)

        player.rect.topleft = (40, 450)
        player.vx, player.vy = 0, 0

    load_level(current_idx)
    running = True
    win_state = False

    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

        if not win_state:
            player.handle_input(all_sprites, stars)
            player.update(platforms)
            stars.update(platforms)

            if pygame.sprite.spritecollideany(player, goals):
                current_idx += 1
                if current_idx <= MAX_LEVELS:
                    load_level(current_idx)
                else:
                    win_state = True

            if player.rect.top > SCREEN_HEIGHT:
                player.rect.topleft = (40, 450)
                player.vx, player.vy = 0, 0

        screen.fill(COLOR_BG)
        all_sprites.draw(screen)

        if win_state:
            txt = font.render("YOU CONQUERED ALL 500 LEVELS!", True, COLOR_STAR)
main()
