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

        # Jump Engine (Ensures double jumps aren't accidentally triggered at once)
        jump_key = keys[pygame.K_UP] or keys[pygame.K_w] or keys[pygame.K_SPACE]
        if jump_key:
            if not self.jump_key_pressed:
                self.jump_key_pressed = True
                
                # Case 1: Grounded Jump
                if self.is_grounded:
                    self.vy = JUMP_FORCE
                    self.is_grounded = False
                    self.jumps_remaining -= 1
                # Case 2: Wall Kick
                elif self.on_wall != 0:  
                    self.vy = JUMP_FORCE
                    self.vx = -self.on_wall * (MAX_SPEED * 1.2)  
                    self.on_wall = 0
                    self.jumps_remaining = self.max_jumps - 1 
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
            self.jumps_remaining = self.max_jumps 

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
                        self.jumps_remaining = self.max_jumps 
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


# --- FIXED MID-EASY HANDCRAFTED LAYOUTS (LEVELS 1 - 10) ---
HANDCRAFTED_LEVELS = {
    1: {"platforms": [(20, 500, 250, 100), (320, 420, 200, 30), (570, 320, 190, 30)], "goal": (640, 260)},
    2: {"platforms": [(20, 500, 200, 100), (280, 430, 180, 30), (520, 340, 220, 30)], "goal": (600, 280)},
    3: {"platforms": [(20, 500, 150, 100), (240, 420, 140, 30), (450, 330, 140, 30), (640, 240, 120, 30)], "goal": (680, 180)},
    4: {"platforms": [(20, 500, 180, 100), (260, 400, 160, 30), (480, 420, 120, 30), (640, 300, 120, 30)], "goal": (680, 240)},
    5: {"platforms": [(20, 500, 150, 100), (220, 410, 130, 30), (420, 320, 130, 30), (220, 230, 150, 30)], "goal": (260, 170)},
    6: {"platforms": [(20, 500, 160, 100), (240, 430, 150, 30), (450, 430, 150, 30), (650, 340, 110, 30)], "goal": (680, 280)},
    7: {"platforms": [(20, 500, 140, 100), (220, 420, 160, 30), (430, 330, 160, 30), (220, 240, 160, 30)], "goal": (260, 180)},
    8: {"platforms": [(20, 500, 160, 100), (240, 400, 140, 30), (440, 300, 140, 30), (640, 200, 120, 30)], "goal": (680, 140)},
    9: {"platforms": [(20, 500, 180, 100), (260, 440, 120, 30), (440, 360, 120, 30), (620, 280, 140, 30)], "goal": (670, 220)},
    10: {"platforms": [(20, 500, 200, 100), (300, 410, 180, 30), (540, 320, 200, 30)], "goal": (620, 260)},
}


# --- THE 50-LEVEL ENGINE CONTROLLER ---
def generate_game_level(level_num):
    """ Loads handmade assets if level <= 10, otherwise executes clean generation """
    level_data = {"platforms": [], "goal": (0, 0)}
    
    # Boundary Screen Enclosures
    level_data["platforms"].append((0, 0, 20, 600))
    level_data["platforms"].append((780, 0, 20, 600))
    
    # --- PULL HANDMADE MID-EASY LEVELS ---
    if level_num in HANDCRAFTED_LEVELS:
        level_data["platforms"].extend(HANDCRAFTED_LEVELS[level_num]["platforms"])
        level_data["goal"] = HANDCRAFTED_LEVELS[level_num]["goal"]
        return level_data

    # --- DOUBLE JUMP CALCULATED PROCEDURAL MAPS (LEVELS 11 - 50) ---
    random.seed(level_num + 777)
    
    # Starting Floor platform
    level_data["platforms"].append((20, 500, 160, 100))
    
    # Scale up platform difficulty as the index moves up towards 50
    progression = min((level_num - 11) / 39.0, 1.0)
    
    min_width = int(110 - (progression * 30))  # Shrinks down to 80px wide
    max_width = int(160 - (progression * 30))  
    
    current_x = 150
    current_y = 440
    
    while current_y > 150:
        p_width = random.randint(min_width, max_width)
        p_height = 20
        
        # Inject Wall-Jump vertical pillars
        if random.random() < 0.20 * progression:
            level_data["platforms"].append((current_x + 20, current_y - 80, 40, 90))
            current_y -= 110
        else:
            level_data["platforms"].append((current_x, current_y, p_width, p_height))
            
            # Double Jump distance tracking scaling bounds
            gap_x = random.randint(110, int(150 + (progression * 60)))  # Extended gaps to reward double jumps
            gap_y = random.randint(65, 95)
            
            if current_x + p_width + gap_x > 740:
                current_x = random.randint(40, 160)
            else:
                current_x += p_width + gap_x
                
            current_y -= gap_y

    # Cap stage with target pad destination
    goal_platform_x = random.randint(120, 500)
    level_data["platforms"].append((goal_platform_x, 140, 140, 20))
    level_data["goal"] = (goal_platform_x + 50, 80)
    
    return level_data


# --- MAIN LOOP ---
def main():
    pygame.init()
    screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
    pygame.display.set_caption("Scratch Ninja - 50 Level Edition")
    clock = pygame.time.Clock()
    font = pygame.font.SysFont("Arial", 24)

    all_sprites = pygame.sprite.Group()
    platforms = pygame.sprite.Group()
    stars = pygame.sprite.Group()
    goals = pygame.sprite.Group()

    player = Player(60, 440)
    all_sprites.add(player)

    current_idx = 1  
    MAX_LEVELS = 50

