import pygame
import random
import sys

# --- Engine Configuration & Setup ---
pygame.init()
W, H = 800, 600
screen = pygame.display.set_mode((W, H))
pygame.display.set_caption("Galactic Defender: Neon Vector Edition")
clock = pygame.time.Clock()

# Low-overhead safe fallback fonts
font_ui = pygame.font.SysFont("Courier", 18, bold=True)
font_big = pygame.font.SysFont("Courier", 32, bold=True)

# --- Rigid Vector Theme Palette ---
COLOR_SPACE   = (6, 5, 14)       # Deep Void 
COLOR_GRID    = (16, 15, 35)     # Background Matrix Lines
COLOR_CYAN    = (0, 255, 240)    # Player Weapons / Blast Glow
COLOR_MINT    = (0, 255, 140)    # Player Chassis Core
COLOR_ORANGE  = (255, 110, 0)    # Elite Class Armor Plate
COLOR_CRIMSON = (255, 40, 80)     # Enemy Vanguard Hulls
COLOR_SHIELD  = (0, 160, 255)    # Defensive Shield Matrix

def reset_game():
    global px, py, pw, ph, p_health, score, tier, boss, fire_cooldown, shield_timer, rapid_timer
    global p_bullets, b_bullets, enemies, powerups, particles, game_won
    px, py, pw, ph = 375, 540, 50, 40
    p_health, score, tier = 100, 0, 1
    fire_cooldown, shield_timer, rapid_timer = 0, 0, 0
    p_bullets = []   # Format: [x, y]
    b_bullets = []   # Format: [x, y, dx]
    powerups = []    # Format: [x, y, type]
    particles = []   # Format: [x, y, dx, dy, lifetime_alpha, color_id]
    boss = None      # Format: [x, y, dir, health, max_health]
    # Enemies Format: [x, y, vertical_speed, wobble_angle_accumulator]
    enemies = [[random.randint(0, 760), random.randint(-200, -50), random.uniform(2.5, 4.5), 0.0] for _ in range(5)]
    game_won = False

reset_game()

# --- Main Engine Processing Core ---
while True:
    # Handle Keyboard / Window Quit Triggers
    for e in pygame.event.get():
        if e.type == pygame.QUIT: 
            pygame.quit()
            sys.exit()
        if e.type == pygame.KEYDOWN and (p_health <= 0 or game_won):
            reset_game()

    if p_health > 0 and not game_won:
        # Tick down frame-rate timers
        if fire_cooldown > 0: fire_cooldown -= 1
        if shield_timer > 0:  shield_timer -= 1
        if rapid_timer > 0:   rapid_timer -= 1

        # Polish Hardware Inputs
        keys = pygame.key.get_pressed()
        if keys[pygame.K_LEFT] or keys[pygame.K_a]:  
            px = max(0, px - 7)
        if keys[pygame.K_RIGHT] or keys[pygame.K_d]: 
            px = min(W - pw, px + 7)
        
        # Fire Blasters Continuous Stream Check
        if keys[pygame.K_SPACE] and fire_cooldown == 0:
            fire_cooldown = 6 if rapid_timer > 0 else 16
            p_bullets.append([px + 8, py + 10])
            p_bullets.append([px + pw - 12, py + 10])
            
            # Left & Right Gun Barrel Muzzle Sparks
            particles.append([px + 8, py + 5, random.uniform(-1.5, 1.5), random.uniform(-2, -4), 255, 1])
            particles.append([px + pw - 12, py + 5, random.uniform(-1.5, 1.5), random.uniform(-2, -4), 255, 1])

        # Generate Procedural Engine Exhaust Trails
        if random.random() < 0.5:
            particles.append([px + pw // 2, py + ph, random.uniform(-0.8, 0.8), random.uniform(2, 4), 200, 2])

        # 1. Update Player Projectiles Positions Safely
        next_p_bullets = []
        for pb in p_bullets:
            pb[1] -= 14  # Move upward along Y axis
            if pb[1] >= 0: 
                next_p_bullets.append(pb)
        p_bullets = next_p_bullets

        # 2. Update Standard Interceptor Enemies (Only processed if boss is dead)
        if boss is None:
            for en in enemies:
                en[1] += en[2]       # Add speed to vertical Y coordinate
                en[3] += 0.08        # Advance horizontal wobble wave tick rate
                en[0] += int(2.5 * (1 if en[3] % 2 > 1 else -1)) # Perform low-overhead shift sideways
                
                # Recycle offscreen enemies back to top ceiling bounds
                if en[1] > H:
                    en[0] = random.randint(0, 760)
                    en[1] = random.randint(-150, -40)

                ebx = pygame.Rect(en[0], en[1], 32, 32)
                
                # Check target collisions against player blasters
                hit_by_bullet = False
                for pb in p_bullets[:]:
                    if ebx.collidepoint(pb[0], pb[1]):
                        if pb in p_bullets: 
                            p_bullets.remove(pb)
                        hit_by_bullet = True
                        break
                        
                if hit_by_bullet:
                    score += 50
                    # Shatter minion hull into explosion debris sparks
                    for _ in range(6):
                        particles.append([en[0] + 16, en[1] + 16, random.uniform(-4, 4), random.uniform(-4, 4), 255, 3])
                    # Dynamic tactical upgrade drops check
                    if random.random() < 0.22:
                        powerups.append([en[0] + 6, en[1] + 6, "SHIELD" if random.random() < 0.5 else "RAPID"])
                    
                    en[0] = random.randint(0, 760)
                    en[1] = random.randint(-150, -40)
                    continue

                # Hull impact damage resolution
                if shield_timer <= 0 and ebx.colliderect(pygame.Rect(px, py, pw, ph)):
                    p_health -= 20
                    for _ in range(8):
                        particles.append([px + 25, py + 20, random.uniform(-4, 4), random.uniform(-4, 4), 255, 4])
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
            
            # Reverse bounce direction whenever side walls are hit
            if boss[0] <= 10 or boss[0] >= W - bw - 10: 
                boss[2] *= -1 

            # Automated tactical line laser spray tables
            # Triggers every few frames based on current Tier level
            if random.randint(1, 100) <= (3 + tier):
                mid_x = boss[0] + bw // 2
                if tier == 1: 
                    b_bullets.extend([[mid_x, boss[1] + 35, dx] for dx in [-2, 0, 2]])
                elif tier == 2: 
                    b_bullets.extend([[boss[0] + 20, boss[1] + 35, -1], [boss[0] + bw - 20, boss[1] + 35, 1]])
                elif tier >= 3: 
                    b_bullets.extend([[mid_x, boss[1] + 35, dx] for dx in [-4, -2, 0, 2, 4]])

            # Check your player weapon impacts directly on boss core
            brx = pygame.Rect(boss[0], boss[1], bw, 45)
            for pb in p_bullets[:]:
                if brx.collidepoint(pb[0], pb[1]):
                    if pb in p_bullets: 
                        p_bullets.remove(pb)
                    boss[3] -= 10 # Deduct armor health value points
                    particles.append([pb[0], boss[1] + 40, random.uniform(-2, 2), random.uniform(1, 4), 200, 1])
                    
                    if boss[3] <= 0:
                        score += 500
                        tier += 1
                        # Generate heavy destruction vector shockwave ring sparks
                        for _ in range(20):
                            particles.append([boss[0] + bw // 2, boss[1] + 20, random.uniform(-5, 5), random.uniform(-5, 5), 255, 5])
                        boss = None
                        if tier > 5: 
                            game_won = True
                        break

        # 4. Hostile Line-Laser Fire updates & Collisions
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
                        particles.append([bb[0], bb[1], random.uniform(-3, 3), random.uniform(-3, 3), 200, 4])
                else:
                    next_b_bullets.append(bb)
        b_bullets = next_b_bullets

        # 5. Drop Loot Updates & Active State Triggers
        next_powerups = []
        for po in powerups:
            po[1] += 2.5 # Advance vertical drop
            if po[1] <= H:
                if pygame.Rect(px, py, pw, ph).colliderect(pygame.Rect(po[0] - 10, po[1] - 10, 20, 20)):
                    if po[2] == "SHIELD": 
                        shield_timer = 360
                    else: 
                        rapid_timer = 360
                else:
                    next_powerups.append(po)
        powerups = next_powerups

        # 6. Global Particles Array Processing (Hardware safe single-pass filtration filter)
        next_particles = []
        for pt in particles:
            pt[0] += pt[2] # Translate along X track via dx
            pt[1] += pt[3] # Translate along Y track via dy
            pt[4] -= 8     # Fade lifetime alpha metric values
            if pt[4] > 0 and 0 <= pt[0] <= W and 0 <= pt[1] <= H:
                next_particles.append(pt)
        # Apply safety threshold clip cutoff value to protect Celeron from looping out
        particles = next_particles[:50] 

    # --- Canvas Screen Draw Pipeline ---
    screen.fill(COLOR_SPACE)

    # Render cyber retro vector space map grid background lines
