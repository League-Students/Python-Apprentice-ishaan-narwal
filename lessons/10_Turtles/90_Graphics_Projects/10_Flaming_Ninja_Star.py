import pygame
import random
import sys

# --- Engine Configuration & Setup ---
pygame.init()
W, H = 800, 600
screen = pygame.display.set_mode((W, H))
pygame.display.set_caption("Galactic Defender: Final Overdrive Edition")
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
    global p_bullets, b_bullets, powerups, particles, game_won, fire_rate_modifier
    global enemies_x, enemies_y, enemies_speed, enemies_wobble
    global boss_x, boss_y, boss_dir, boss_health, boss_max_health, boss_active
    
    px, py, pw, ph = 375, 540, 50, 40
    p_health, score, tier = 100, 0, 1
    fire_cooldown, shield_timer = 0, 0
    fire_rate_modifier = 0  
    
    # Clean, separate list tracks to completely avoid list index crashes
    p_bullets = []   # Format: [x, y]
    b_bullets = []   # Format: [x, y, dx]
    powerups = []    # Format: [x, y, type]
    particles = []   # Format: [x, y, dx, dy, color_id]
    
    # Flat, parallel lists for enemy management
    enemies_x = [random.randint(0, 760) for _ in range(5)]
    enemies_y = [random.randint(-200, -50) for _ in range(5)]
    enemies_speed = [random.uniform(2.5, 4.5) for _ in range(5)]
    enemies_wobble = [0.0 for _ in range(5)]
    
    # Boss states completely isolated out of mixed lists
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
        
        # Continuous weapon stream tracking stacking modifications
        if keys[pygame.K_SPACE] and fire_cooldown == 0:
            base_cooldown = 16 - (fire_rate_modifier * 3)
            fire_cooldown = max(1, base_cooldown)
            
            p_bullets.append([px + 8, py + 10])
            p_bullets.append([px + pw - 12, py + 10])
            particles.append([px + 8, py + 5, random.uniform(-1.5, 1.5), random.uniform(-2, -4), 1])
            particles.append([px + pw - 12, py + 5, random.uniform(-1.5, 1.5), random.uniform(-2, -4), 1])

        if random.random() < 0.5:
            particles.append([px + pw // 2, py + ph, random.uniform(-0.8, 0.8), random.uniform(2, 4), 2])

        # 1. Update Player Projectiles Positions
        next_p_bullets = []
        for pb in p_bullets:
            pb[1] -= 14  # Move upward along Y axis
            if pb[1] >= 0: 
                next_p_bullets.append(pb)
        p_bullets = next_p_bullets

        # 2. Update Standard Enemies (Only active if boss is not present)
        if not boss_active:
            for i in range(len(enemies_x)):
                enemies_y[i] += enemies_speed[i]       
                enemies_wobble[i] += 0.08        
                enemies_x[i] += int(2.5 * (1 if enemies_wobble[i] % 2 > 1 else -1)) 
                
                # Recycle off-screen enemies back to ceiling
                if enemies_y[i] > H:
                    enemies_x[i] = random.randint(0, 760)
                    enemies_y[i] = random.randint(-150, -40)

                ebx = pygame.Rect(enemies_x[i], enemies_y[i], 32, 32)
                
                # Hitbox verification against player weapon payloads
                hit_by_bullet = False
                for pb in p_bullets[:]:
                    if ebx.collidepoint(pb[0], pb[1]):
                        if pb in p_bullets: 
                            p_bullets.remove(pb)
                        hit_by_bullet = True
                        break
                        
                if hit_by_bullet:
                    score += 50
                    for _ in range(4):
                        particles.append([enemies_x[i] + 16, enemies_y[i] + 16, random.uniform(-4, 4), random.uniform(-4, 4), 3])
                    
                    # 65% Drop rate heavily favoring permanent RAPID speedups
                    if random.random() < 0.65:
                        powerups.append([enemies_x[i] + 6, enemies_y[i] + 6, "SHIELD" if random.random() < 0.15 else "RAPID"])
                    
                    enemies_x[i] = random.randint(0, 760)
                    enemies_y[i] = random.randint(-150, -40)
                    continue

                # Player contact damage resolution
                if shield_timer <= 0 and ebx.colliderect(pygame.Rect(px, py, pw, ph)):
                    p_health -= 20
                    for _ in range(8):
                        particles.append([px + 25, py + 20, random.uniform(-4, 4), random.uniform(-4, 4), 4])
                    enemies_x[i] = random.randint(0, 760)
                    enemies_y[i] = random.randint(-150, -40)

        # 3. Capital Class Boss Generation Mechanics
        if not boss_active and score >= tier * 1000:
            if tier > 5: 
                game_won = True
            else: 
                boss_active = True
                boss_x = 350
                boss_y = 70
                boss_dir = 1
                boss_max_health = 200 * tier
                boss_health = boss_max_health
        
        if boss_active:
            bw = 110 + tier * 12
            boss_x += (2.2 + tier * 0.4) * boss_dir
            
            if boss_x <= 10 or boss_x >= W - bw - 10: 
                boss_dir *= -1 

            # Automated boss firing rates
            if random.randint(1, 100) <= (4 + tier):
                mid_x = boss_x + bw // 2
                if tier == 1: 
                    b_bullets.extend([[mid_x, boss_y + 35, dx] for dx in [-2, 0, 2]])
                elif tier == 2: 
                    b_bullets.extend([[boss_x + 20, boss_y + 35, -1], [boss_x + bw - 20, boss_y + 35, 1]])
                elif tier >= 3: 
                    b_bullets.extend([[mid_x, boss_y + 35, dx] for dx in [-4, -2, 0, 2, 4]])

            # Check weapon damage payloads hitting the boss core
            brx = pygame.Rect(boss_x, boss_y, bw, 45)
            for pb in p_bullets[:]:
                if brx.collidepoint(pb[0], pb[1]):
                    if pb in p_bullets: 
                        p_bullets.remove(pb)
                    boss_health -= 10 
                    particles.append([pb[0], boss_y + 40, random.uniform(-2, 2), random.uniform(1, 4), 1])
                    
                    if boss_health <= 0:
                        score += 500
                        tier += 1
                        for _ in range(20):
                            particles.append([boss_x + bw // 2, boss_y + 20, random.uniform(-5, 5), random.uniform(-5, 5), 3])
                        boss_active = False
                        if tier > 5: 
                            game_won = True
                        break

        # 4. Global Hostile Line-Laser Fire
        next_b_bullets = []
        player_rect = pygame.Rect(px, py, pw, ph)
        for bb in b_bullets:
            bb[1] += 6.5       # Move Y down
            bb[0] += bb[2]     # Move X by its dx variable velocity smoothly
            
            if 0 <= bb[1] <= H and 0 <= bb[0] <= W:
                if shield_timer <= 0 and player_rect.collidepoint(int(bb[0]), int(bb[1] + 15)):
                    p_health -= 15
                    for _ in range(5):
                        particles.append([bb[0], bb[1], random.uniform(-3, 3), random.uniform(-3, 3), 4])
                else:
                    next_b_bullets.append(bb)
        b_bullets = next_b_bullets

        # 5. Drop Upgrade Loot Updates
        next_powerups = []
        for po in powerups:
            po[1] += 2.5 
            if po[1] <= H:
                if pygame.Rect(po[0] - 10, po[1] - 10, 20, 20).colliderect(player_rect):
                    if po[2] == "SHIELD": 
                        shield_timer = 360
                    elif po[2] == "RAPID": 
                        fire_rate_modifier += 1 
                else:
                    next_powerups.append(po)
        powerups = next_powerups

        # 6. Global Particles Array Processing
        next_particles = []
        for pt in particles:
            pt[0] += pt[2] # Translate X via dx
            pt[1] += pt[3] # Translate Y via dy
            if 0 <= pt[0] <= W and 0 <= pt[1] <= H:
                next_particles.append(pt)
        particles = next_particles[:50] 

    # --- Canvas Screen Draw Pipeline ---
    screen.fill(COLOR_SPACE)

    # Render vector map background grid lines
    for x in range(0, W, 80): pygame.draw.line(screen, COLOR_GRID, (x, 0), (x, H), 1)
    for y in range(0, H, 60): pygame.draw.line(screen, COLOR_GRID, (0, y), (W, y), 1)

    # Render active vector explosion shards safely
    for pt in particles:
        p_hue = COLOR_CYAN if pt[4] == 1 else (COLOR_ORANGE if pt[4] == 2 else (COLOR_CRIMSON if pt[4] == 3 else COLOR_MINT))
        pygame.draw.circle(screen, p_hue, (int(pt[0]), int(pt[1])), 2 if pt[4] == 2 else 3)

    # Render player blasters
    for pb in p_bullets: 
        pygame.draw.rect(screen, COLOR_CYAN, (pb[0], pb[1], 3, 16))

    # Render glowing Enemy / Boss line weapons
    for bb in b_bullets: 
