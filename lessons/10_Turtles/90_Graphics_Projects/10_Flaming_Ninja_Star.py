import pygame, random, sys
pygame.init()

# --- Engine Configuration & Setup ---
W, H = 800, 600
screen = pygame.display.set_mode((W, H))
pygame.display.set_caption("Galactic Defender: Master Celeron Edition")
clock = pygame.time.Clock()
font = pygame.font.SysFont("Arial", 20, bold=True)

# --- Game States Reset Engine ---
def reset_game():
    global px, py, pw, ph, p_health, score, tier, boss, fire_cooldown, shield_timer, rapid_timer
    global p_bullets, b_bullets, enemies, powerups, particles, game_won
    px, py, pw, ph = 375, 540, 50, 40
    p_health, score, tier = 100, 0, 1
    fire_cooldown, shield_timer, rapid_timer = 0, 0, 0
    p_bullets = []  # format: [x, y]
    b_bullets = []  # format: [x, y, dx]
    powerups = []   # format: [x, y, type]
    particles = []  # format: [x, y, dx, dy, alpha]
    boss = None     # format: [x, y, dir, health, max_health, attack_tick]
    enemies = [[random.randint(0, 760), random.randint(-200, -50), random.uniform(2, 4), 0.0] for _ in range(5)]
    game_won = False

reset_game()

# --- Main Engine Loop ---
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
        if keys[pygame.K_SPACE] and fire_cooldown == 0:
            fire_cooldown = 5 if rapid_timer > 0 else 15
            p_bullets.append([px + 5, py])
            p_bullets.append([px + pw - 10, py])

        # 1. Update Player Projectiles Physics
        next_p_bullets = []
        for b in p_bullets:
            b[1] -= 12
            if b[1] >= 0:
                next_p_bullets.append(b)
        p_bullets = next_p_bullets

        # 2. Update Standard Enemy Arrays & Collisions (Only active if no boss exists)
        if boss is None:
            for en in enemies:
                en[1] += en[2] # Vertical movement
                en[3] += 0.05  # Horizontal wave adjustment variable
                en[0] += int(1.5 * (1 if en[3] % 2 > 1 else -1)) # Low overhead wobble step
                
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
                    for _ in range(4):
                        particles.append([en[0]+16, en[1]+16, random.randint(-3, 3), random.randint(-3, 3), 255])
                    if random.random() < 0.2:
                        powerups.append([en[0], en[1], "SHIELD" if random.random() < 0.5 else "RAPID"])
                    en[0], en[1] = random.randint(0, 760), random.randint(-150, -40)
                    continue

                # Enemy hull contact checking
                if shield_timer <= 0 and ebx.colliderect(pygame.Rect(px, py, pw, ph)):
                    p_health -= 20
                    en[0], en[1] = random.randint(0, 760), random.randint(-150, -40)

        # 3. Micro Boss AI Processing Structure
        if boss is None and score >= tier * 1000:
            if tier > 5:
                game_won = True
            else:
                boss = [350, 60, 2 + tier * 0.5, 200 * tier, 200 * tier, 0] # x, y, speed, hp, max_hp, tick
        
        if boss:
            boss[0] += boss[2]
            bw = 100 + tier * 15
            if boss[0] <= 0 or boss[0] >= W - bw:
                boss[2] *= -1 # Reverse direction on boundaries
            boss[5] += 1

            # Conditional firing processing table
            if boss[5] % (45 - tier * 4) == 0:
                mid_x = boss[0] + bw // 2
                if tier == 1: b_bullets.extend([[mid_x, boss[1]+40, dx] for dx in [-2, 0, 2]])
                elif tier == 2: b_bullets.extend([[boss[0]+20, boss[1]+40, 0], [boss[0]+bw-20, boss[1]+40, 0]])
                elif tier >= 3: b_bullets.extend([[mid_x, boss[1]+40, dx] for dx in [-4, -2, 0, 2, 4]])

            # Checking player bullets hitting boss core
            brx = pygame.Rect(boss[0], boss[1], bw, 50)
            for pb in p_bullets[:]:
                if brx.collidepoint(pb[0], pb[1]):
                    if pb in p_bullets: p_bullets.remove(pb)
                    boss[3] -= 10
                    if boss[3] <= 0:
                        score += 500
                        tier += 1
                        boss = None
                        if tier > 5: game_won = True
                        break

        # 4. Global Hostile Fire Mechanics (Clean single-pass allocation filter)
        next_b_bullets = []
        player_rect = pygame.Rect(px, py, pw, ph)
        for bb in b_bullets:
            bb[1] += 6     # Move down
            bb[0] += bb[2] # Move sideways based on angle speed vector
            
            if 0 <= bb[1] <= H and 0 <= bb[0] <= W:
                # Optimized line-tip hazard point intercept mapping
                if shield_timer <= 0 and player_rect.collidepoint(bb[0], bb[1] + 15):
                    p_health -= 15
                else:
                    next_b_bullets.append(bb)
        b_bullets = next_b_bullets

        # 5. Drop Loot Updates
        next_powerups = []
        for po in powerups:
            po[1] += 3
            if po[1] <= H:
                if pygame.Rect(px, py, pw, ph).colliderect(pygame.Rect(po[0], po[1], 20, 20)):
                    if po[2] == "SHIELD": shield_timer = 300
                    else: rapid_timer = 300
                else:
                    next_powerups.append(po)
        powerups = next_powerups

        # 6. Particles Engine Physics Updates
        next_particles = []
        for pt in particles:
            pt[0] += pt[2]
            pt[1] += pt[3]
            pt[4] -= 8
            if pt[4] > 0:
                next_particles.append(pt)
        particles = next_particles

    # --- Screen Draw Pipeline ---
    screen.fill((10, 8, 22))

    # Fast geometry draws
    for pt in particles: pygame.draw.circle(screen, (255, 100, 100), (pt[0], pt[1]), 2)
    for pb in p_bullets: pygame.draw.rect(screen, (0, 255, 255), (pb[0], pb[1], 4, 12))
    for bb in b_bullets: pygame.draw.line(screen, (255, 50, 50), (bb[0], bb[1]), (bb[0] + bb[2]*2, bb[1] + 15), 3)
    for po in powerups: pygame.draw.circle(screen, (255, 255, 0) if po[2] == "RAPID" else (0, 190, 255), (po[0]+10, po[1]+10), 8)
    
    if boss is None and not game_won:
        for en in enemies: pygame.draw.polygon(screen, (255, 60, 60), [(en[0]+16, en[1]), (en[0]+32, en[1]+24), (en[0], en[1]+24)])

    if boss and not game_won:
        bw = 100 + tier * 15
        pygame.draw.rect(screen, (200, 30, 100), (boss[0], boss[1], bw, 30), border_radius=5)
        pygame.draw.rect(screen, (80, 0, 0), (boss[0], boss[1] - 12, bw, 6))
        if boss[3] > 0:
            pygame.draw.rect(screen, (255, 0, 0), (boss[0], boss[1] - 12, int(bw * (boss[3] / boss[4])), 6))

    if p_health > 0 and not game_won:
        pygame.draw.polygon(screen, (0, 190, 255) if shield_timer > 0 else (0, 255, 150), [(px+25, py), (px, py+ph), (px+pw, py+ph)])
        if shield_timer > 0: pygame.draw.circle(screen, (0, 190, 255), (px+25, py+20), 30, 1)
    elif game_won:
        w_txt1 = font.render("VICTORY! ALL BOSS TIERS CRUSHED!", True, (0, 255, 150))
        w_txt2 = font.render("Press Any Key to Play Again and Reclaim Glory", True, (240, 240, 255))
        screen.blit(w_txt1, (W//2 - w_txt1.get_width()//2, H//2 - 20))
        screen.blit(w_txt2, (W//2 - w_txt2.get_width()//2, H//2 + 15))
    else:
        t_txt = font.render("GAME OVER - Press Any Key to Restart", True, (255, 60, 60))
        screen.blit(t_txt, (W//2 - t_txt.get_width()//2, H//2))

    # Static User Interface Panel Metrics Display
    screen.blit(font.render(f"SCORE: {score}  |  TIER: {tier if tier <= 5 else 'MAX'}", True, (240, 240, 255)), (15, 15))
    health_text = font.render(f"HP: {max(0, p_health)}/100", True, (0, 255, 150))
    screen.blit(health_text, (15, 42))
    pygame.draw.rect(screen, (40, 40, 50), (130, 48, 150, 14), border_radius=3)
    if p_health > 0:
        pygame.draw.rect(screen, (0, 255, 150), (130, 48, int(150 * (p_health / 100)), 14), border_radius=3)

    pygame.display.flip()
    clock.tick(60)
