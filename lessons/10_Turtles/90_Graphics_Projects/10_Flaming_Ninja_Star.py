import pygame
import random
import sys

# --- Engine Configuration & Setup ---
pygame.init()
W, H = 800, 600
screen = pygame.display.set_mode((W, H))
pygame.display.set_caption("Galactic Defender: Unbreakable Master Edition")
clock = pygame.time.Clock()

font_ui = pygame.font.SysFont("Courier", 18, bold=True)
font_big = pygame.font.SysFont("Courier", 32, bold=True)

# --- Vector Theme Palette ---
COLOR_SPACE   = (6, 5, 14)       
COLOR_GRID    = (16, 15, 35)     
COLOR_CYAN    = (0, 255, 240)    
COLOR_MINT    = (0, 255, 140)    
COLOR_ORANGE  = (255, 110, 0)    
COLOR_CRIMSON = (255, 40, 80)     
COLOR_SHIELD  = (0, 160, 255)    

def reset_game():
    global px, py, pw, ph, p_health, score, tier, fire_cooldown, shield_timer
    global p_bullets_x, p_bullets_y, b_bullets_x, b_bullets_y, b_bullets_dx
    global powerups_x, powerups_y, powerups_type, game_won, fire_rate_modifier
    global enemies_x, enemies_y, enemies_speed, enemies_wobble
    global boss_x, boss_y, boss_dir, boss_health, boss_max_health, boss_active
    global particles_x, particles_y, particles_dx, particles_dy, particles_color
    
    px, py, pw, ph = 375, 540, 50, 40
    p_health, score, tier = 100, 0, 1
    fire_cooldown, shield_timer = 0, 0
    fire_rate_modifier = 0  
    
    # Completely flat individual lists to prevent any indexing bugs
    p_bullets_x, p_bullets_y = [], []
    b_bullets_x, b_bullets_y, b_bullets_dx = [], [], []
    powerups_x, powerups_y, powerups_type = [], [], []
    particles_x, particles_y, particles_dx, particles_dy, particles_color = [], [], [], [], []
    
    # Flat parallel lists for enemy tracks
    enemies_x = [random.randint(0, 760) for _ in range(5)]
    enemies_y = [random.randint(-200, -50) for _ in range(5)]
    enemies_speed = [random.uniform(2.5, 4.5) for _ in range(5)]
    enemies_wobble = [0.0 for _ in range(5)]
    
    # Boss tracked variables completely flat
    boss_active = False
    boss_x, boss_y, boss_dir, boss_health, boss_max_health = 350, 70, 1, 200, 200
    game_won = False

reset_game()

# --- Main Engine Processing Core ---
while True:
    for e in pygame.event.get():
        if e.type == pygame.QUIT: 
            pygame.quit()
            sys.exit()
        if e.type == pygame.KEYDOWN and (p_health <= 0 or game_won):
            reset_game()

    if p_health > 0 and not game_won:
        if fire_cooldown > 0: fire_cooldown -= 1
        if shield_timer > 0:  shield_timer -= 1

        keys = pygame.key.get_pressed()
        if keys[pygame.K_LEFT] or keys[pygame.K_a]:  px = max(0, px - 7)
        if keys[pygame.K_RIGHT] or keys[pygame.K_d]: px = min(W - pw, px + 7)
        
        # Stacking speed formula calculations
        if keys[pygame.K_SPACE] and fire_cooldown == 0:
            base_cooldown = 16 - (fire_rate_modifier * 3)
            fire_cooldown = max(1, base_cooldown)
            
            # Append separate primitive tracks
            p_bullets_x.append(px + 8)
            p_bullets_y.append(py + 10)
            p_bullets_x.append(px + pw - 12)
            p_bullets_y.append(py + 10)
            
            # Spawning muzzle sparks
            for target_x in [px + 8, px + pw - 12]:
                particles_x.append(target_x)
                particles_y.append(py + 5)
                particles_dx.append(random.uniform(-1.5, 1.5))
                particles_dy.append(random.uniform(-2, -4))
                particles_color.append(1)

        if random.random() < 0.4:
            particles_x.append(px + pw // 2)
            particles_y.append(py + ph)
            particles_dx.append(random.uniform(-0.8, 0.8))
            particles_dy.append(random.uniform(2, 4))
            particles_color.append(2)

        # 1. Update Player Projectiles Positions 
        next_px, next_py = [], []
        for i in range(len(p_bullets_y)):
            new_y = p_bullets_y[i] - 14
            if new_y >= 0:
                next_px.append(p_bullets_x[i])
                next_py.append(new_y)
        p_bullets_x, p_bullets_y = next_px, next_py

        # 2. Update Standard Enemies (Only active if boss is not present)
        if not boss_active:
            for i in range(len(enemies_x)):
                enemies_y[i] += enemies_speed[i]       
                enemies_wobble[i] += 0.08        
                enemies_x[i] += int(2.5 * (1 if enemies_wobble[i] % 2 > 1 else -1)) 
                
                if enemies_y[i] > H:
                    enemies_x[i] = random.randint(0, 760)
                    enemies_y[i] = random.randint(-150, -40)

                ebx = pygame.Rect(enemies_x[i], enemies_y[i], 32, 32)
                
                # Bullet collision verification loop
                hit_by_bullet = False
                for b_idx in range(len(p_bullets_x)):
                    if ebx.collidepoint(p_bullets_x[b_idx], p_bullets_y[b_idx]):
                        p_bullets_x.pop(b_idx)
                        p_bullets_y.pop(b_idx)
                        hit_by_bullet = True
                        break
                        
                if hit_by_bullet:
                    score += 50
                    for _ in range(4):
                        particles_x.append(enemies_x[i] + 16)
                        particles_y.append(enemies_y[i] + 16)
                        particles_dx.append(random.uniform(-4, 4))
                        particles_dy.append(random.uniform(-4, 4))
                        particles_color.append(3)
                    
                    # 65% Drop Rate setup
                    if random.random() < 0.65:
                        powerups_x.append(enemies_x[i] + 6)
                        powerups_y.append(enemies_y[i] + 6)
                        powerups_type.append("SHIELD" if random.random() < 0.15 else "RAPID")
                    
                    enemies_x[i] = random.randint(0, 760)
                    enemies_y[i] = random.randint(-150, -40)
                    continue

                if shield_timer <= 0 and ebx.colliderect(pygame.Rect(px, py, pw, ph)):
                    p_health -= 20
                    for _ in range(8):
                        particles_x.append(px + 25)
                        particles_y.append(py + 20)
                        particles_dx.append(random.uniform(-4, 4))
                        particles_dy.append(random.uniform(-4, 4))
                        particles_color.append(4)
                    enemies_x[i] = random.randint(0, 760)
                    enemies_y[i] = random.randint(-150, -40)

        # 3. Capital Class Boss Mechanics
        if not boss_active and score >= tier * 1000:
            if tier > 5: 
                game_won = True
            else: 
                boss_active = True
                boss_x, boss_y, boss_dir = 350, 70, 1
                boss_max_health = 200 * tier
                boss_health = boss_max_health
        
        if boss_active:
            bw = 110 + tier * 12
            boss_x += (2.2 + tier * 0.4) * boss_dir
            
            if boss_x <= 10 or boss_x >= W - bw - 10: 
                boss_dir *= -1 

            if random.randint(1, 100) <= (4 + tier):
                mid_x = boss_x + bw // 2
                if tier == 1:
                    for dx in [-2, 0, 2]:
                        b_bullets_x.append(mid_x); b_bullets_y.append(boss_y + 35); b_bullets_dx.append(dx)
                elif tier == 2:
                    b_bullets_x.append(boss_x + 20); b_bullets_y.append(boss_y + 35); b_bullets_dx.append(-1)
                    b_bullets_x.append(boss_x + bw - 20); b_bullets_y.append(boss_y + 35); b_bullets_dx.append(1)
                elif tier >= 3:
                    for dx in [-4, -2, 0, 2, 4]:
                        b_bullets_x.append(mid_x); b_bullets_y.append(boss_y + 35); b_bullets_dx.append(dx)

            brx = pygame.Rect(boss_x, boss_y, bw, 45)
            hit_boss = False
            for b_idx in range(len(p_bullets_x)):
                if brx.collidepoint(p_bullets_x[b_idx], p_bullets_y[b_idx]):
                    p_bullets_x.pop(b_idx)
                    p_bullets_y.pop(b_idx)
                    boss_health -= 10 
                    particles_x.append(boss_x + bw // 2)
                    particles_y.append(boss_y + 40)
                    particles_dx.append(random.uniform(-2, 2))
                    particles_dy.append(random.uniform(1, 4))
                    particles_color.append(1)
                    if boss_health <= 0:
                        hit_boss = True
                    break
                    
            if hit_boss:
                score += 500
                tier += 1
                for _ in range(20):
                    particles_x.append(boss_x + bw // 2)
                    particles_y.append(boss_y + 20)
                    particles_dx.append(random.uniform(-5, 5))
                    particles_dy.append(random.uniform(-5, 5))
                    particles_color.append(3)
                boss_active = False
                if tier > 5: 
                    game_won = True

        # 4. Hostile Line-Laser Fire updates
        nbx, nby, nbdx = [], [], []
        player_rect = pygame.Rect(px, py, pw, ph)
        for i in range(len(b_bullets_y)):
            new_y = b_bullets_y[i] + 6.5
            new_x = b_bullets_x[i] + b_bullets_dx[i]
            
            if 0 <= new_y <= H and 0 <= new_x <= W:
                if shield_timer <= 0 and player_rect.collidepoint(int(new_x), int(new_y + 15)):
                    p_health -= 15
                    for _ in range(5):
                        particles_x.append(new_x); particles_y.append(new_y)
                        particles_dx.append(random.uniform(-3, 3)); particles_dy.append(random.uniform(-3, 3))
                        particles_color.append(4)
                else:
                    nbx.append(new_x); nby.append(new_y); nbdx.append(b_bullets_dx[i])
