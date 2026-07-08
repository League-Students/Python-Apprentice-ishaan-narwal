import pygame, random, sys
pygame.init()

# --- Engine Configuration & Setup ---
W, H = 800, 600
screen = pygame.display.set_mode((W, H))
pygame.display.set_caption("Galactic Defender: Neon Vector Edition")
clock = pygame.time.Clock()

# Low-overhead clean system fonts
font_ui = pygame.font.SysFont("Consolas", 18, bold=True)
font_big = pygame.font.SysFont("Consolas", 32, bold=True)

# --- Enhanced Vector Color Palette ---
COLOR_SPACE   = (6, 5, 14)       # Deep space indigo
COLOR_GRID    = (16, 15, 35)     # Background vector grid lines
COLOR_CYAN    = (0, 255, 240)    # Player projectiles / tech neon
COLOR_MINT    = (0, 255, 140)    # Player hull neon
COLOR_ORANGE  = (255, 110, 0)    # Powerups / core energy
COLOR_CRIMSON = (255, 40, 80)     # Enemy core neon
COLOR_SHIELD  = (0, 160, 255)    # Energy matrix shield

def reset_game():
    global px, py, pw, ph, p_health, score, tier, boss, fire_cooldown, shield_timer, rapid_timer
    global p_bullets, b_bullets, enemies, powerups, particles, engine_particles, game_won
    px, py, pw, ph = 375, 540, 50, 40
    p_health, score, tier = 100, 0, 1
    fire_cooldown, shield_timer, rapid_timer = 0, 0, 0
    p_bullets = []        # format: [x, y]
    b_bullets = []        # format: [x, y, dx]
    powerups = []         # format: [x, y, type, rotation_angle]
    particles = []        # format: [x, y, dx, dy, alpha, color]
    engine_particles = [] # format: [x, y, radius, alpha]
    boss = None           # format: [x, y, dir, health, max_health, attack_tick]
    enemies = [[random.randint(0, 760), random.randint(-200, -50), random.uniform(2.5, 4.5), 0.0] for _ in range(5)]
    game_won = False

reset_game()

# --- Main Performance Loop ---
while True:
    for e in pygame.event.get():
        if e.type == pygame.QUIT: pygame.quit(); sys.exit()
        if e.type == pygame.KEYDOWN and (p_health <= 0 or game_won):
            reset_game()

    if p_health > 0 and not game_won:
        # Timers state tickdowns
        if fire_cooldown > 0: fire_cooldown -= 1
        if shield_timer > 0:  shield_timer -= 1
        if rapid_timer > 0:   rapid_timer -= 1

        # Celeron-friendly keyboard polling
        keys = pygame.key.get_pressed()
        if keys[pygame.K_LEFT] or keys[pygame.K_a]:  px = max(0, px - 7)
        if keys[pygame.K_RIGHT] or keys[pygame.K_d]: px = min(W - pw, px + 7)
        
        # Continuous weapon stream
        if keys[pygame.K_SPACE] and fire_cooldown == 0:
            fire_cooldown = 6 if rapid_timer > 0 else 16
            p_bullets.append([px + 8, py + 10])
            p_bullets.append([px + pw - 12, py + 10])
            # Fire sparks
            particles.append([px + 8, py, random.uniform(-1, 1), -3, 200, COLOR_CYAN])
            particles.append([px + pw - 12, py, random.uniform(-1, 1), -3, 200, COLOR_CYAN])

        # Procedural Rocket Exhaust Particle trail
        if random.random() < 0.6:
            engine_particles.append([px + pw // 2 + random.randint(-4, 4), py + ph, random.randint(3, 6), 255])

        # Update rocket trails
        next_eng = []
        for ep in engine_particles:
            ep[1] += 3  # move down
            ep[2] = max(1, ep[2] - 0.2)  # shrink size
            ep[3] -= 12 # fade alpha
            if ep[3] > 0 and ep[2] > 1:
                next_eng.append(ep)
        engine_particles = next_eng

        # 1. Update Player Projectiles Physics
        next_p_bullets = []
        for b in p_bullets:
            b[1] -= 14
            if b[1] >= 0:
                next_p_bullets.append(b)
        p_bullets = next_p_bullets

        # 2. Update Standard Enemy Arrays & Collisions (Only active if no boss exists)
        if boss is None:
            for en in enemies:
                en[1] += en[2] # Vertical movement
                en[3] += 0.07  # Speed phase clock for wobble
                en[0] += int(2 * (1 if en[3] % 2 > 1 else -1)) # Vector zig-zag logic
                
                if en[1] > H:
                    en[0], en[1] = random.randint(0, 760), random.randint(-150, -40)

                ebx = pygame.Rect(en[0], en[1], 32, 32)
                
                # Check collisions with player bullets
                hit_by_bullet = False
                for pb in p_bullets[:]:
                    if ebx.collidepoint(pb[0], pb[1]):
                        if pb in p_bullets: p_bullets.remove(pb)
                        hit_by_bullet = True
                        break
                        
                if hit_by_bullet:
                    score += 50
                    # Refined shattering explosion particles
                    for _ in range(8):
                        particles.append([en[0]+16, en[1]+16, random.uniform(-4, 4), random.uniform(-4, 4), 255, COLOR_CRIMSON])
                    if random.random() < 0.25:
                        powerups.append([en[0] + 6, en[1] + 6, "SHIELD" if random.random() < 0.5 else "RAPID", 0])
                    en[0], en[1] = random.randint(0, 760), random.randint(-150, -40)
                    continue

                # Enemy hull contact checking
                if shield_timer <= 0 and ebx.colliderect(pygame.Rect(px, py, pw, ph)):
                    p_health -= 20
                    for _ in range(10):
                        particles.append([px+25, py+20, random.uniform(-5, 5), random.uniform(-5, 5), 255, COLOR_MINT])
                    en[0], en[1] = random.randint(0, 760), random.randint(-150, -40)

        # 3. Micro Boss AI Processing Structure
        if boss is None and score >= tier * 1000:
            if tier > 5:
                game_won = True
            else:
                boss = [350, 70, 2.2 + tier * 0.4, 200 * tier, 200 * tier, 0] # x, y, speed, hp, max_hp, tick
        
        if boss:
            boss[0] += boss[2]
            bw = 110 + tier * 12
            if boss[0] <= 10 or boss[0] >= W - bw - 10:
                boss[2] *= -1 # Reverse direction on boundaries
            boss[5] += 1

            # Conditional refined firing patterns
            if boss[5] % (42 - tier * 4) == 0:
                mid_x = boss[0] + bw // 2
                if tier == 1: b_bullets.extend([[mid_x, boss[1]+40, dx] for dx in [-2.5, 0, 2.5]])
                elif tier == 2: b_bullets.extend([[boss[0]+20, boss[1]+45, -0.5], [boss[0]+bw-20, boss[1]+45, 0.5]])
                elif tier >= 3: b_bullets.extend([[mid_x, boss[1]+40, dx] for dx in [-4, -2, 0, 2, 4]])

            # Checking player bullets hitting boss core
            brx = pygame.Rect(boss[0], boss[1], bw, 45)
            for pb in p_bullets[:]:
                if brx.collidepoint(pb[0], pb[1]):
                    if pb in p_bullets: p_bullets.remove(pb)
                    boss[3] -= 10
                    # Hit sparks
                    particles.append([pb[0], boss[1]+40, random.uniform(-2, 2), random.uniform(1, 4), 200, COLOR_CYAN])
                    if boss[3] <= 0:
                        score += 500
                        tier += 1
                        for _ in range(25):
                            particles.append([boss[0]+bw//2, boss[1]+20, random.uniform(-6, 6), random.uniform(-6, 6), 255, COLOR_ORANGE])
                        boss = None
                        if tier > 5: game_won = True
                        break

        # 4. Global Hostile Fire Mechanics
        next_b_bullets = []
        player_rect = pygame.Rect(px, py, pw, ph)
        for bb in b_bullets:
            bb[1] += 6.5     # Move down
            bb[0] += bb[2]   # Move sideways based on dx vector speed
            
            if 0 <= bb[1] <= H and 0 <= bb[0] <= W:
                # Targeted accurate line-tip bounding box calculations
                if shield_timer <= 0 and player_rect.collidepoint(bb[0], bb[1] + 15):
                    p_health -= 15
                    for _ in range(6):
                        particles.append([bb[0], bb[1], random.uniform(-3, 3), random.uniform(-3, 3), 220, COLOR_MINT])
                else:
                    next_b_bullets.append(bb)
        b_bullets = next_b_bullets

        # 5. Drop Loot Updates
        next_powerups = []
        for po in powerups:
            po[1] += 2.5
            po[3] = (po[3] + 4) % 360  # Spin the vector shape frame
            if po[1] <= H:
                if pygame.Rect(px, py, pw, ph).colliderect(pygame.Rect(po[0]-10, po[1]-10, 20, 20)):
                    if po[2] == "SHIELD": shield_timer = 360
                    else: rapid_timer = 360
                    # Collection flash sparks
                    for _ in range(8):
                        particles.append([px+25, py+20, random.uniform(-4, 4), random.uniform(-4, 4), 255, COLOR_CYAN if po[2]=="RAPID" else COLOR_SHIELD])
                else:
                    next_powerups.append(po)
        powerups = next_powerups

        # 6. General Particle System Physics Updates
        next_particles = []
        for pt in particles:
            pt[0] += pt[2]
            pt[1] += pt[3]
            pt[4] -= 7  # Decay alpha rate
            if pt[4] > 0:
                next_particles.append(pt)
        particles = next_particles

    # --- Screen Draw Pipeline ---
    screen.fill(COLOR_SPACE)

    # Performance-friendly structural vector grid lines behind all items
    for x in range(0, W, 80): pygame.draw.line(screen, COLOR_GRID, (x, 0), (x, H), 1)
    for y in range(0, H, 60): pygame.draw.line(screen, COLOR_GRID, (0, y), (W, y), 1)

    # Draw Rocket Flame particles trail
    for ep in engine_particles:
        # Emulates high-end flame alpha blending on a Celeron using layered radii size draws
        pygame.draw.circle(screen, (255, int(ep[3]*0.6), 0), (ep[0], ep[1]), int(ep[2]))
        pygame.draw.circle(screen, (255, 255, 100), (ep[0], ep[1]), max(1, int(ep[2] * 0.5)))

    # Draw standard explosion shards
    for pt in particles:
        pygame.draw.circle(screen, pt[5], (int(pt[0]), int(pt[1])), max(1, int(pt[4] // 80 + 1)))

