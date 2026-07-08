import pygame, random, sys
pygame.init()

# --- Engine Configuration & Setup ---
W, H = 800, 600
screen = pygame.display.set_mode((W, H))
pygame.display.set_caption("Galactic Defender: Celeron Edition")
clock = pygame.time.Clock()
font = pygame.font.SysFont("Arial", 20, bold=True)

# --- Optimized Game Object States (Simple Lists for CPU efficiency) ---
px, py, pw, ph = 375, 540, 50, 40   # Player transform data
p_health, score, tier = 100, 0, 1
fire_cooldown, shield_timer, rapid_timer = 0, 0, 0

# Entity tracking databases
p_bullets = []  # Elements format: [x, y]
b_bullets = []  # Elements format: [x, y, dx]
enemies = [[random.randint(0, 760), random.randint(-200, -50), random.uniform(2, 4), 0.0] for _ in range(5)]
powerups = []   # Elements format: [x, y, type]
particles = []  # Elements format: [x, y, dx, dy, alpha]
boss = None     # Structure format: [x, y, dir, health, max_health, attack_tick]

# --- Main Performance Loop ---
while True:
    for e in pygame.event.get():
        if e.type == pygame.QUIT: pygame.quit(); sys.exit()
        if e.type == pygame.KEYDOWN and p_health <= 0:  # Soft memory wipe engine reset
            px, py, p_health, score, tier, boss = 375, 540, 100, 0, 1, None
            p_bullets, b_bullets, powerups, particles = [], [], [], []
            enemies = [[random.randint(0, 760), random.randint(-200, -50), random.uniform(2, 4), 0.0] for _ in range(5)]

    if p_health > 0:
        # Timers state tickdowns
        if fire_cooldown > 0: fire_cooldown -= 1
        if shield_timer > 0:  shield_timer -= 1
        if rapid_timer > 0:   rapid_timer -= 1

        # Celeron-friendly optimized keyboard polling logic
        keys = pygame.key.get_pressed()
        if keys[pygame.K_LEFT] or keys[pygame.K_a]:  px = max(0, px - 7)
        if keys[pygame.K_RIGHT] or keys[pygame.K_d]: px = min(W - pw, px + 7)
        if keys[pygame.K_SPACE] and fire_cooldown == 0:
            fire_cooldown = 5 if rapid_timer > 0 else 15
            p_bullets.extend([[px + 5, py], [px + pw - 10, py]])

        # 1. Update Player Projectiles Physics
        for b in p_bullets[:]:
            b -= 12
            if b < 0: p_bullets.remove(b)

        # 2. Update Standard Enemy Arrays & Collisions (ONLY running when boss is absent)
        if boss is None:
            for en in enemies:
                en += en                       # Vertical gravity drop speed
                en += 0.05                        # Low overhead wobble calculation
                en += int(1.5 * (1 if en % 2 > 1 else -1)) # Integer step variation instead of sin()
                if en > H: en, en = random.randint(0, 760), random.randint(-150, -40)

                # Hitbox resolution checks against player lasers
                ebx = pygame.Rect(en, en, 32, 32)
                for pb in p_bullets[:]:
                    if ebx.collidepoint(pb, pb):
                        if pb in p_bullets: p_bullets.remove(pb)
                        score += 50
                        particles.extend([[en+16, en+16, random.randint(-3, 3), random.randint(-3, 3), 255] for _ in range(6)])
                        if random.random() < 0.2: powerups.append([en, en, "SHIELD" if random.random() < 0.5 else "RAPID"])
                        en, en = random.randint(0, 760), random.randint(-150, -40)

                # Enemy hull contact checking
                if shield_timer <= 0 and ebx.colliderect(pygame.Rect(px, py, pw, ph)):
                    p_health -= 20
                    en, en = random.randint(0, 760), random.randint(-150, -40)

        # 3. Micro Boss AI Processing Structure
        if boss is None and score >= tier * 1000 and tier <= 5:
            boss = [350, 60, 2 + tier * 0.5, 200 * tier, 200 * tier, 0] # x, y, speed, hp, max_hp, tick
        
        if boss:
            boss += boss
            if boss <= 0 or boss >= W - (100 + tier * 15): boss *= -1 # Reverse direction on boundaries
            boss += 1

            # Flat conditional firing table cuts down looping calls
            if boss % (45 - tier * 4) == 0:
                if tier == 1: b_bullets.extend([[boss+50, boss+40, dx] for dx in [-2, 0, 2]])
                elif tier == 2: b_bullets.extend([[boss+20, boss+40, 0], [boss+70, boss+40, 0]])
                elif tier >= 3: b_bullets.extend([[boss+50, boss+40, dx] for dx in [-4, -2, 0, 2, 4]])

            # Checking player laser payloads hitting the boss core
            bw = 100 + tier * 15
            brx = pygame.Rect(boss, boss, bw, 50)
            for pb in p_bullets[:]:
                if brx.collidepoint(pb, pb):
                    if pb in p_bullets: p_bullets.remove(pb)
                    boss -= 10
                    if boss <= 0:
                        score += 500; tier += 1; boss = None; break

        # 4. Global Hostile Fire Mechanics
        for bb in b_bullets[:]:
            bb += 6; bb += bb
            if bb > H or bb < 0 or bb > W or bb < 0: b_bullets.remove(bb); continue
            
            # Hitbox check adjusted slightly to account for the shape of the lines
            if shield_timer <= 0 and pygame.Rect(px, py, pw, ph).collidepoint(bb, bb + 20):
                p_health -= 15; b_bullets.remove(bb)

        # 5. Drop Loot Updates
        for po in powerups[:]:
            po += 3
            if po > H: powerups.remove(po); continue
            if pygame.Rect(px, py, pw, ph).colliderect(pygame.Rect(po, po, 20, 20)):
                if po == "SHIELD": shield_timer = 300
                else: rapid_timer = 300
                powerups.remove(po)

        # 6. Light Particles Physics Updates
        for pt in particles[:]:
            pt += pt; pt += pt; pt -= 8
            if pt <= 0: particles.remove(pt)

    # --- Screen Draw Pipeline ---
    screen.fill((10, 8, 22))

    # Drawing light primitives saves CPU draw overhead over heavy images
    for pt in particles: pygame.draw.circle(screen, (255, 100, 100), (pt, pt), 2)
    for pb in p_bullets: pygame.draw.rect(screen, (0, 255, 255), (pb, pb, 4, 12))
    
    # Render Boss Bullets as cool laser lines instead of squares
    for bb in b_bullets: 
        # Draws a line from the laser's position down 20 pixels with a thickness of 3
        pygame.draw.line(screen, (255, 50, 50), (bb, bb), (bb + bb, bb + 20), 3)
        
    for po in powerups: pygame.draw.circle(screen, (255, 255, 0) if po == "RAPID" else (0, 190, 255), (po+10, po+10), 8)
    
    # Red normal enemies are ONLY drawn when no boss is present
    if boss is None:
        for en in enemies: pygame.draw.polygon(screen, (255, 60, 60), [(en+16, en), (en+32, en+24), (en, en+24)])

    if boss:
        bw = 100 + tier * 15
        pygame.draw.rect(screen, (200, 30, 100), (boss, boss, bw, 30), border_radius=5)
        pygame.draw.rect(screen, (80, 0, 0), (boss, boss - 12, bw, 6))
        pygame.draw.rect(screen, (255, 0, 0), (boss, boss - 12, int(bw * (boss / boss)), 6))

    if p_health > 0:
        pygame.draw.polygon(screen, (0, 190, 255) if shield_timer > 0 else (0, 255, 150), [(px+25, py), (px, py+ph), (px+pw, py+ph)])
        if shield_timer > 0: pygame.draw.circle(screen, (0, 190, 255), (px+25, py+20), 30, 1)
    else:
        t_txt = font.render("GAME OVER - Press Any Key to Restart", True, (255, 60, 60))
        screen.blit(t_txt, (W//2 - t_txt.get_width()//2, H//2))

    # Core Diagnostic Display metrics
    screen.blit(font.render(f"SCORE: {score}  |  TIER: {tier if tier <= 5 else 'MAX'}", True, (240, 240, 255)), (15, 15))
    
    # Expanded health bar system for player ship
    health_text = font.render(f"HP: {max(0, p_health)}/100", True, (0, 255, 150))
    screen.blit(health_text, (15, 42))
    pygame.draw.rect(screen, (40, 40, 50), (130, 48, 150, 14), border_radius=3)
    if p_health > 0:
        pygame.draw.rect(screen, (0, 255, 150), (130, 48, int(150 * (p_health / 100)), 14), border_radius=3)

    pygame.display.flip()
    clock.tick(60)
