import pygame
import random
import sys

# --- Engine Configuration & Setup ---
pygame.init()
W, H = 800, 600
screen = pygame.display.set_mode((W, H))
pygame.display.set_caption("Galactic Defender: Unbreakable Overdrive Edition")
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
    fire_rate_modifier = 0  # Tracking permanent stacked upgrades
    p_bullets = []   # Explicit layout: [x, y]
    b_bullets = []   # Explicit layout: [x, y, dx]
    powerups = []    # Explicit layout: [x, y, type]
    particles = []   # Explicit layout: [x, y, dx, dy, color_id]
    boss = None      # Explicit layout: [x, y, dir, health, max_health]
    # Enemies tracking layout: [x, y, speed, wobble_accumulator]
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
        
        # Fire weapon continuous flow logic tracking collected stack variations
        if keys[pygame.K_SPACE] and fire_cooldown == 0:
            # Dynamically reduce cooldown frames per collected upgrade level (Capped at maximum hardware speed of 1 frame)
            base_cooldown = 16 - (fire_rate_modifier * 3)
            fire_cooldown = max(1, base_cooldown)
            
            p_bullets.append([px + 8, py + 10])
            p_bullets.append([px + pw - 12, py + 10])
            particles.append([px + 8, py + 5, random.uniform(-1.5, 1.5), random.uniform(-2, -4), 1])
            particles.append([px + pw - 12, py + 5, random.uniform(-1.5, 1.5), random.uniform(-2, -4), 1])

        if random.random() < 0.5:
            particles.append([px + pw // 2, py + ph, random.uniform(-0.8, 0.8), random.uniform(2, 4), 2])

        # 1. Update Player Projectiles Safely via Temporary Allocation Filters
        next_p_bullets = []
        for pb in p_bullets:
            pb[1] -= 14  
            if pb[1] >= 0: 
                next_p_bullets.append(pb)
        p_bullets = next_p_bullets

        # 2. Update Standard Interceptor Enemies Safely
        if boss is None:
            for en in enemies:
                en[1] += en[2]       # Add speed to vertical Y coordinate
                en[3] += 0.08        # Advance horizontal wobble wave tick rate
                en[0] += int(2.5 * (1 if en[1] % 2 > 1 else -1)) # Perform side shift
                
                # Recycle offscreen enemies back to top ceiling bounds
                if en[1] > H:
                    en[0] = random.randint(0, 760)
                    en[1] = random.randint(-150, -40)

                ebx = pygame.Rect(en[0], en[1], 32, 32)
                
                # Check target collisions against player blasters safely
                hit_by_bullet = False
                for pb in p_bullets:
                    if ebx.collidepoint(pb[0], pb[1]):
                        p_bullets.remove(pb)
                        hit_by_bullet = True
                        break
                        
                if hit_by_bullet:
                    score += 50
                    for _ in range(6):
                        particles.append([en[0] + 16, en[1] + 16, random.uniform(-4, 4), random.uniform(-4, 4), 3])
                    
                    # MASSIVE DROP RATE: Raised to 65% total chance per destroy, heavily favoring RAPID fire
                    if random.random() < 0.65:
                        powerups.append([en[0] + 6, en[1] + 6, "SHIELD" if random.random() < 0.15 else "RAPID"])
                    
                    en[0] = random.randint(0, 760)
                    en[1] = random.randint(-150, -40)
                    continue

                # Hull impact damage resolution
                if shield_timer <= 0 and ebx.colliderect(pygame.Rect(px, py, pw, ph)):
                    p_health -= 20
                    for _ in range(8):
                        particles.append([px + 25, py + 20, random.uniform(-4, 4), random.uniform(-4, 4), 4])
                    en[0] = random.randint(0, 760)
                    en[1] = random.randint(-150, -40)

        # 3. Capital Class Boss Generation Mechanics
        if boss is None and score >= tier * 1000:
            if tier > 5: 
                game_won = True
            else: 
                # Spawn parameters layout: [X, Y, Velocity_Direction, Health, Max_Health]
                boss = [350, 70, 2.2 + tier * 0.4, 200 * tier, 200 * tier] 
        
        if boss:
            boss[0] += boss[2] # Add speed to horizontal X coordinate axis track
            bw = 110 + tier * 12
            
            if boss[0] <= 10 or boss[0] >= W - bw - 10: 
                boss[2] *= -1 

            # Automated tactical line laser spray tables
            if random.randint(1, 100) <= (3 + tier):
                mid_x = boss[0] + bw // 2
                if tier == 1: 
                    b_bullets.extend([[mid_x, boss[1] + 35, dx] for dx in [-2, 0, 2]])
                elif tier == 2: 
                    b_bullets.extend([[boss[0] + 20, boss[1] + 35, -1], [boss[0] + bw - 20, boss[1] + 35, 1]])
                elif tier >= 3: 
                    b_bullets.extend([[mid_x, boss[1] + 35, dx] for dx in [-4, -2, 0, 2, 4]])

            # Check player weapon impacts directly on boss core safely
            brx = pygame.Rect(boss[0], boss[1], bw, 45)
            for pb in p_bullets:
                if brx.collidepoint(pb[0], pb[1]):
                    p_bullets.remove(pb)
                    boss[3] -= 10 # Deduct armor health value points
                    particles.append([pb[0], boss[1] + 40, random.uniform(-2, 2), random.uniform(1, 4), 1])
                    
                    if boss[3] <= 0:
                        score += 500
                        tier += 1
                        for _ in range(20):
                            particles.append([boss[0] + bw // 2, boss[1] + 20, random.uniform(-5, 5), random.uniform(-5, 5), 4])
                        boss = None
                        if tier > 5: 
                            game_won = True
                        break

        # 4. Global Hostile Line-Laser Fire updates & Collisions Safely
        next_b_bullets = []
        player_rect = pygame.Rect(px, py, pw, ph)
        for bb in b_bullets:
            bb[1] += 6.5   # Move downward vertically
            bb[0] += bb[2] # Adjust sideways displacement vector via dx
            
            if 0 <= bb[1] <= H and 0 <= bb[0] <= W:
                # Intercept laser endpoint targeting bounds checking
                if shield_timer <= 0 and player_rect.collidepoint(int(bb[0]), int(bb[1] + 15)):
                    p_health -= 15
                    for _ in range(5):
                        particles.append([bb[0], bb[1], random.uniform(-3, 3), random.uniform(-3, 3), 4])
                else:
                    next_b_bullets.append(bb)
        b_bullets = next_b_bullets

        # 5. Drop Loot Updates & Active State Triggers Safely
        next_powerups = []
        for po in powerups:
            po[1] += 2.5 # Advance vertical drop
            if po[1] <= H:
                if pygame.Rect(po[0] - 10, po[1] - 10, 20, 20).colliderect(player_rect):
                    if po[2] == "SHIELD": 
                        shield_timer = 360
                    elif po[2] == "RAPID":
                        fire_rate_modifier += 1 # Increments firepower levels permanently 
                else:
                    next_powerups.append(po)
        powerups = next_powerups

        # 6. Global Particles Array Processing Safely
        next_particles = []
        for pt in particles:
            pt[0] += pt[2] # Translate along X track via dx
            pt[1] += pt[3] # Translate along Y track via dy
            # Instead of mutating the shared list, we store a separate custom alpha tracker or use standard screen limits
            if 0 <= pt[0] <= W and 0 <= pt[1] <= H:
                next_particles.append(pt)
        # Apply safety threshold clip cutoff value to protect Celeron from looping out
        particles = next_particles[:50] 

    # --- Canvas Screen Draw Pipeline ---
    screen.fill(COLOR_SPACE)

    # Render cyber retro vector space map grid background lines
    for x in range(0, W, 80): 
        pygame.draw.line(screen, COLOR_GRID, (x, 0), (x, H), 1)
    for y in range(0, H, 60): 
        pygame.draw.line(screen, COLOR_GRID, (0, y), (W, y), 1)

    # Render active vector debris sparks and flame exhausts loops safely
    for pt in particles:
        p_hue = COLOR_CYAN if pt[4] == 1 else (COLOR_ORANGE if pt[4] == 2 else (COLOR_CRIMSON if pt[4] == 3 else COLOR_MINT))
        pygame.draw.circle(screen, p_hue, (int(pt[0]), int(pt[1])), 2 if pt[4] == 2 else 3)

