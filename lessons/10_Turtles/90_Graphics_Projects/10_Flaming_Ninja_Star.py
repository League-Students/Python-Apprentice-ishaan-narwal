import pygame
import random
import sys

# --- Engine Configuration & Setup ---
pygame.init()
W, H = 800, 600
screen = pygame.display.set_mode((W, H))
pygame.display.set_caption("Galactic Defender: Master Overdrive Edition")
clock = pygame.time.Clock()

font_ui = pygame.font.SysFont("Courier", 18, bold=True)
font_big = pygame.font.SysFont("Courier", 32, bold=True)

# --- Rigid Vector Theme Palette ---
COLOR_SPACE   = (6, 5, 14)       
COLOR_GRID    = (16, 15, 35)     
COLOR_CYAN    = (0, 255, 240)    
COLOR_MINT    = (0, 255, 140)    
COLOR_ORANGE  = (255, 110, 0)    
COLOR_CRIMSON = (255, 40, 80)     
COLOR_SHIELD  = (0, 160, 255)    

def reset_game():
    global px, py, pw, ph, p_health, score, tier, boss, fire_cooldown, shield_timer
    global p_bullets, b_bullets, enemies, powerups, particles, game_won, fire_rate_modifier
    px, py, pw, ph = 375, 540, 50, 40
    p_health, score, tier = 100, 0, 1
    fire_cooldown, shield_timer = 0, 0
    fire_rate_modifier = 0  
    p_bullets = []   # Format: [x, y]
    b_bullets = []   # Format: [x, y, dx]
    powerups = []    # Format: [x, y, type]
    particles = []   # Format: [x, y, dx, dy, color_id]
    boss = None      # Format: [x, y, dir, health, max_health]
    # Enemies Format: [x, y, vertical_speed, wobble_tick]
    enemies = [[random.randint(0, 760), random.randint(-200, -50), random.uniform(2.5, 4.5), 0.0] for _ in range(5)]
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
        
        # Fire weapon continuous flow logic
        if keys[pygame.K_SPACE] and fire_cooldown == 0:
            base_cooldown = 16 - (fire_rate_modifier * 3)
            fire_cooldown = max(1, base_cooldown)
            
            p_bullets.append([px + 8, py + 10])
            p_bullets.append([px + pw - 12, py + 10])
            particles.append([px + 8, py + 5, random.uniform(-1.5, 1.5), random.uniform(-2, -4), 1])
            particles.append([px + pw - 12, py + 5, random.uniform(-1.5, 1.5), random.uniform(-2, -4), 1])

        if random.random() < 0.5:
            particles.append([px + pw // 2, py + ph, random.uniform(-0.8, 0.8), random.uniform(2, 4), 2])

        # 1. Update Player Projectiles Safely
        next_p_bullets = []
        for pb in p_bullets:
            pb[1] -= 14  # Move up along Y axis
            if pb[1] >= 0: 
                next_p_bullets.append(pb)
        p_bullets = next_p_bullets

        # 2. Update Standard Interceptor Enemies (Only when boss is absent)
        if boss is None:
            for en in enemies:
                en[1] += en[2]       # Update Y position by speed
                en[3] += 0.08        # Advance wobble tick
                en[0] += int(2.5 * (1 if en[3] % 2 > 1 else -1)) # Shift X sideways
                
                # Recycle offscreen enemies
                if en[1] > H:
                    en[0] = random.randint(0, 760)
                    en[1] = random.randint(-150, -40)

                ebx = pygame.Rect(en[0], en[1], 32, 32)
                
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
                        particles.append([en[0] + 16, en[1] + 16, random.uniform(-4, 4), random.uniform(-4, 4), 3])
                    
                    # 65% Drop rate heavily favoring RAPID fire upgrades
                    if random.random() < 0.65:
                        powerups.append([en[0] + 6, en[1] + 6, "SHIELD" if random.random() < 0.15 else "RAPID"])
                    
                    en[0] = random.randint(0, 760)
                    en[1] = random.randint(-150, -40)
                    continue

                if shield_timer <= 0 and ebx.colliderect(pygame.Rect(px, py, pw, ph)):
                    p_health -= 20
                    for _ in range(8):
                        particles.append([px + 25, py + 20, random.uniform(-4, 4), random.uniform(-4, 4), 4])
                    en[0] = random.randint(0, 760)
                    en[1] = random.randint(-150, -40)

        # 3. Capital Class Boss Mechanics
        if boss is None and score >= tier * 1000:
            if tier > 5: 
                game_won = True
            else: 
                # [X, Y, Velocity, Health, Max_Health]
                boss = [350, 70, 2.2 + tier * 0.4, 200 * tier, 200 * tier] 
        
        if boss:
            boss[0] += boss[2] # Move horizontally
            bw = 110 + tier * 12
            
            if boss[0] <= 10 or boss[0] >= W - bw - 10: 
                boss[2] *= -1 

            if random.randint(1, 100) <= (3 + tier):
                mid_x = boss[0] + bw // 2
                if tier == 1: 
                    b_bullets.extend([[mid_x, boss[1] + 35, dx] for dx in [-2, 0, 2]])
                elif tier == 2: 
                    b_bullets.extend([[boss[0] + 20, boss[1] + 35, -1], [boss[0] + bw - 20, boss[1] + 35, 1]])
                elif tier >= 3: 
                    b_bullets.extend([[mid_x, boss[1] + 35, dx] for dx in [-4, -2, 0, 2, 4]])

            brx = pygame.Rect(boss[0], boss[1], bw, 45)
            for pb in p_bullets[:]:
                if brx.collidepoint(pb[0], pb[1]):
                    if pb in p_bullets: 
                        p_bullets.remove(pb)
                    boss[3] -= 10 
                    particles.append([pb[0], boss[1] + 40, random.uniform(-2, 2), random.uniform(1, 4), 1])
                    
                    if boss[3] <= 0:
                        score += 500
                        tier += 1
                        for _ in range(20):
                            particles.append([boss[0] + bw // 2, boss[1] + 20, random.uniform(-5, 5), random.uniform(-5, 5), 3])
                        boss = None
                        if tier > 5: 
                            game_won = True
                        break

        # 4. Global Hostile Line-Laser Fire Updates
        next_b_bullets = []
        player_rect = pygame.Rect(px, py, pw, ph)
        for bb in b_bullets:
            bb[1] += 6.5   # Move Y down
            bb[0] += bb[2] # Move X by dx direction
            
            if 0 <= bb[1] <= H and 0 <= bb[0] <= W:
                if shield_timer <= 0 and player_rect.collidepoint(int(bb[0]), int(bb[1] + 15)):
                    p_health -= 15
                    for _ in range(5):
                        particles.append([bb[0], bb[1], random.uniform(-3, 3), random.uniform(-3, 3), 4])
                else:
                    next_b_bullets.append(bb)
        b_bullets = next_b_bullets

        # 5. Drop Loot Updates
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
            pt[0] += pt[2] # Move X
            pt[1] += pt[3] # Move Y
            if 0 <= pt[0] <= W and 0 <= pt[1] <= H:
                next_particles.append(pt)
        particles = next_particles[:50] 

    # --- Canvas Screen Draw Pipeline ---
    screen.fill(COLOR_SPACE)

    # Render vector background grid lines
    for x in range(0, W, 80): pygame.draw.line(screen, COLOR_GRID, (x, 0), (x, H), 1)
    for y in range(0, H, 60): pygame.draw.line(screen, COLOR_GRID, (0, y), (W, y), 1)

    for pt in particles:
        p_hue = COLOR_CYAN if pt[4] == 1 else (COLOR_ORANGE if pt[4] == 2 else (COLOR_CRIMSON if pt[4] == 3 else COLOR_MINT))
        pygame.draw.circle(screen, p_hue, (int(pt[0]), int(pt[1])), 2 if pt[4] == 2 else 3)

    for pb in p_bullets: 
        pygame.draw.rect(screen, COLOR_CYAN, (pb[0], pb[1], 3, 16))

    for bb in b_bullets: 
        pygame.draw.line(screen, COLOR_CRIMSON, (int(bb[0]), int(bb[1])), (int(bb[0] + bb[2] * 2), int(bb[1] + 16)), 3)

    for po in powerups:
        token_hue = COLOR_SHIELD if po[2] == "SHIELD" else COLOR_CYAN
        pygame.draw.rect(screen, token_hue, (po[0] - 8, po[1] - 8, 16, 16), 2)
    
    if boss is None and not game_won:
        for en in enemies: 
            pygame.draw.polygon(screen, COLOR_CRIMSON, [(en[0] + 16, en[1]), (en[0] + 32, en[1] + 26), (en[0] + 16, en[1] + 18), (en[0], en[1] + 26)])
            pygame.draw.polygon(screen, (255, 255, 255), [(en[0] + 16, en[1]), (en[0] + 32, en[1] + 26), (en[0] + 16, en[1] + 18), (en[0], en[1] + 26)], 1)

    if boss and not game_won:
        bw = 110 + tier * 12
        pygame.draw.polygon(screen, COLOR_ORANGE, [(boss[0], boss[1]), (boss[0] + bw, boss[1]), (boss[0] + bw - 20, boss[1] + 35), (boss[0] + 20, boss[1] + 35)])
        pygame.draw.polygon(screen, (255, 255, 255), [(boss[0], boss[1]), (boss[0] + bw, boss[1]), (boss[0] + bw - 20, boss[1] + 35), (boss[0] + 20, boss[1] + 35)], 2)
        
