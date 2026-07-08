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
            b[1] -= 12
            if b[1] < 0: p_bullets.remove(b)

        # 2. Update Standard Enemy Arrays & Collisions
        for en in enemies:
            en[1] += en[2]                       # Vertical gravity drop speed
            en[3] += 0.05                        # Low overhead wobble calculation
            en[0] += int(1.5 * (1 if en[3] % 2 > 1 else -1)) # Integer step variation instead of sin()
            if en[1] > H: en[0], en[1] = random.randint(0, 760), random.randint(-150, -40)

            # Hitbox resolution checks against player lasers
            ebx = pygame.Rect(en[0], en[1], 32, 32)
            for pb in p_bullets[:]:
                if ebx.collidepoint(pb[0], pb[1]):
                    if pb in p_bullets: p_bullets.remove(pb)
                    score += 50
                    particles.extend([[en[0]+16, en[1]+16, random.randint(-3, 3), random.randint(-3, 3), 255] for _ in range(6)])
                    if random.random() < 0.2: powerups.append([en[0], en[1], "SHIELD" if random.random() < 0.5 else "RAPID"])
                    en[0], en[1] = random.randint(0, 760), random.randint(-150, -40)

            # Enemy hull contact checking
            if shield_timer <= 0 and ebx.colliderect(pygame.Rect(px, py, pw, ph)):
                p_health -= 20
                en[0], en[1] = random.randint(0, 760), random.randint(-150, -40)

        # 3. Micro Boss AI Processing Structure
        if boss is None and score >= tier * 1000 and tier <= 5:
            boss = [350, 60, 2 + tier * 0.5, 200 * tier, 200 * tier, 0] # x, y, speed, hp, max_hp, tick
        
        if boss:
            boss[0] += boss[2]
            if boss[0] <= 0 or boss[0] >= W - (100 + tier * 15): boss[2] *= -1 # Reverse direction on boundaries
            boss[5] += 1

            # Flat conditional firing table cuts down looping calls
            if boss[5] % (45 - tier * 4) == 0:
                if tier == 1: b_bullets.extend([[boss[0]+50, boss[1]+40, dx] for dx in [-2, 0, 2]])
                elif tier == 2: b_bullets.extend([[boss[0]+20, boss[1]+40, 0], [boss[0]+70, boss[1]+40, 0]])
                elif tier >= 3: b_bullets.extend([[boss[0]+50, boss[1]+40, dx] for dx in [-4, -2, 0, 2, 4]])

            # Checking player laser payloads hitting the boss core
            brx = pygame.Rect(boss[0], boss[1], 100 + tier * 15, 50)
            for pb in p_bullets[:]:
                if brx.collidepoint(pb[0], pb[1]):
                    if pb in p_bullets: p_bullets.remove(pb)
                    boss[3] -= 10
                    if boss[3] <= 0:
                        score += 500; tier += 1; boss = None; break

        # 4. Global Hostile Fire Mechanics
        for bb in b_bullets[:]:
            bb[1] += 6; bb[0] += bb[2]
            if bb[1] > H or bb[0] < 0 or bb[0] > W: b_bullets.remove(bb); continue
            if shield_timer <= 0 and pygame.Rect(px, py, pw, ph).collidepoint(bb[0], bb[1]):
                p_health -= 15; b_bullets.remove(bb)

        # 5. Drop Loot Updates
        for po in powerups[:]:
            po[1] += 3
            if po[1] > H: powerups.remove(po); continue
            if pygame.Rect(px, py, pw, ph).colliderect(pygame.Rect(po[0], po[1], 20, 20)):
                if po[2] == "SHIELD": shield_timer = 300
                else: rapid_timer = 300
                powerups.remove(po)

        # 6. Light Particles Physics Updates
        for pt in particles[:]:
            pt[0] += pt[2]; pt[1] += pt[3]; pt[4] -= 8
            if pt[4] <= 0: particles.remove(pt)

    # --- Screen Draw Pipeline ---
    screen.fill((10, 8, 22))

    # Drawing light primitives saves CPU draw overhead over heavy images
    for pt in particles: pygame.draw.circle(screen, (255, 100, 100), (pt[0], pt[1]), 2)
    for pb in p_bullets: pygame.draw.rect(screen, (0, 255, 255), (pb[0], pb[1], 4, 12))
    for bb in b_bullets: pygame.draw.rect(screen, (255, 130, 0), (bb[0], bb[1], 5, 12))
    for po in powerups: pygame.draw.circle(screen, (255, 255, 0) if po[2] == "RAPID" else (0, 190, 255), (po[0]+10, po[1]+10), 8)
    for en in enemies: pygame.draw.polygon(screen, (255, 60, 60), [(en[0]+16, en[1]), (en[0]+32, en[1]+24), (en[0], en[1]+24)])

    if boss:
        bw = 100 + tier * 15
        pygame.draw.rect(screen, (200, 30, 100), (boss[0], boss[1], bw, 30), border_radius=5)
        pygame.draw.rect(screen, (80, 0, 0), (boss[0], boss[1] - 12, bw, 6))
        pygame.draw.rect(screen, (255, 0, 0), (boss[0], boss[1] - 12, int(bw * (boss[3] / boss[4])), 6))

    if p_health > 0:
        pygame.draw.polygon(screen, (0, 190, 255) if shield_timer > 0 else (0, 255, 150), [(px+25, py), (px, py+ph), (px+pw, py+ph)])
        if shield_timer > 0: pygame.draw.circle(screen, (0, 190, 255), (px+25, py+20), 30, 1)
    else:
        t_txt = font.render("GAME OVER - Press Any Key to Restart", True, (255, 60, 60))
        screen.blit(t_txt, (W//2 - t_txt.get_width()//2, H//2))

    # Core Diagnostic Display metrics
    screen.blit(font.render(f"SCORE: {score}  |  TIER: {tier if tier <= 5 else 'MAX'}", True, (240, 240, 255)), (15, 15))
    pygame.draw.rect(screen, (40, 40, 50), (15, 45, 100, 10))
    pygame.draw.rect(screen, (0, 255, 150), (15, 45, max(0, p_health), 10))

    pygame.display.flip()
    clock.tick(60)
