import random

# --- Window Settings ---
TITLE = "Space Boss Rush"
WIDTH = 800
HEIGHT = 600

# --- State ---
game_state = "BALLS"  # BALLS, BOSS, GAME_OVER, VICTORY
boss_tier = 1
balls_destroyed = 0
balls_needed = 30
score = 0

# --- Classes ---
class Player:
    def __init__(self):
        self.x = WIDTH // 2
        self.y = HEIGHT - 50
        self.health = 100
        self.max_health = 100
        self.speed = 6
        self.cooldown = 0
        self.rapid_stacks = 0

    def update(self, move_dir):
        self.x += move_dir * self.speed
        if self.x < 20: self.x = 20
        if self.x > WIDTH - 20: self.x = WIDTH - 20
        if self.cooldown > 0: self.cooldown -= 1

    def shoot(self):
        delay = max(2, 20 - (self.rapid_stacks * 3))
        if self.cooldown == 0:
            self.cooldown = delay
            bullets.append(Bullet(self.x, self.y - 20))

class Bullet:
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.speed = 9
        self.alive = True

    def update(self):
        self.y -= self.speed
        if self.y < 0: self.alive = False

class RedBall:
    def __init__(self):
        self.x = random.randint(20, WIDTH - 20)
        self.y = random.randint(-100, -20)
        self.speed = random.uniform(2, 4)
        self.alive = True

    def update(self):
        self.y += self.speed
        if self.y > HEIGHT:
            self.x = random.randint(20, WIDTH - 20)
            self.y = random.randint(-100, -20)

class Boss:
    def __init__(self, tier):
        self.tier = tier
        self.size = 60 + (tier * 10)
        self.x = WIDTH // 2
        self.y = 80
        self.health = tier * 30
        self.max_health = self.health
        self.direction = 1
        self.speed = 2 + (tier * 0.5)
        self.shoot_timer = 0
        self.shoot_interval = max(15, 50 - (tier * 6))

    def update(self):
        self.x += self.speed * self.direction
        if self.x >= WIDTH - self.size or self.x <= self.size:
            self.direction *= -1

        self.shoot_timer += 1
        if self.shoot_timer >= self.shoot_interval:
            self.shoot_timer = 0
            boss_bullets.append(BossBullet(self.x, self.y + 20, self.tier))

class BossBullet:
    def __init__(self, x, y, tier):
        self.x = x
        self.y = y
        self.damage = 10 + (tier * 2)
        self.dy = 4 + tier
        self.dx = random.choice([-1.5, 0, 1.5]) if tier >= 3 else 0
        self.alive = True

    def update(self):
        self.x += self.dx
        self.y += self.dy
        if self.y > HEIGHT:
            self.alive = False

class Drop:
    def __init__(self, x, y, drop_type):
        self.x = x
        self.y = y
        self.type = drop_type 
        self.speed = 3
        self.alive = True

    def update(self):
        self.y += self.speed
        if self.y > HEIGHT:
            self.alive = False

# --- Setup ---
player = Player()
bullets = []
red_balls = [RedBall() for _ in range(8)]
boss_bullets = []
drops = []
boss = None
stars = [{"x": random.randint(0, WIDTH), "y": random.randint(0, HEIGHT), "speed": random.uniform(0.5, 3)} for _ in range(40)]

# --- Engine Loops ---
def update():
    global game_state, boss_tier, balls_destroyed, score, boss
    
    if game_state in ["GAME_OVER", "VICTORY"]:
        return

    for s in stars:
        s["y"] += s["speed"]
        if s["y"] > HEIGHT:
            s["y"] = 0
            s["x"] = random.randint(0, WIDTH)

    # Strictly horizontal WASD layout filter logic (strips W and S key registers entirely)
    move_dir = 0
    if keyboard.d: move_dir += 1
    if keyboard.a: move_dir -= 1
    player.update(move_dir)
    
    if keyboard.space or keyboard.j:
        player.shoot()

    for b in bullets: b.update()
    for d in drops: d.update()
    for bb in boss_bullets: bb.update()
    
    bullets[:] = [b for b in bullets if b.alive]
    drops[:] = [d for d in drops if d.alive]
    boss_bullets[:] = [bb for bb in boss_bullets if bb.alive]

    if game_state == "BALLS":
        for rb in red_balls:
            rb.update()
            for b in bullets:
                if abs(b.x - rb.x) < 20 and abs(b.y - rb.y) < 20:
                    rb.alive = False
                    b.alive = False
                    balls_destroyed += 1
                    score += 5
                    if random.random() < 0.40:
                        drops.append(Drop(rb.x, rb.y, "RAPID" if random.random() < 0.70 else "SHIELD"))

        for i, rb in enumerate(red_balls):
            if not rb.alive: red_balls[i] = RedBall()

        if balls_destroyed >= balls_needed:
            game_state = "BOSS"
            boss = Boss(boss_tier)
            boss_bullets.clear()

    elif game_state == "BOSS" and boss:
        boss.update()
        for b in bullets:
            if abs(b.x - boss.x) < (boss.size//2) and abs(b.y - boss.y) < (boss.size//2):
                b.alive = False
                boss.health -= 1
                score += 15
                if boss.health <= 0:
                    boss = None
                    if boss_tier >= 5:
                        game_state = "VICTORY"
                    else:
                        boss_tier += 1
                        game_state = "BALLS"
                        balls_destroyed = 0
                    break

    for d in drops:
        if abs(d.x - player.x) < 25 and abs(d.y - player.y) < 25:
            d.alive = False
            if d.type == "SHIELD":
                player.health = min(player.max_health, player.health + 25)
            else:
                player.rapid_stacks += 1

    for bb in boss_bullets:
        if abs(bb.x - player.x) < 22 and abs(bb.y - player.y) < 22:
            bb.alive = False
            player.health -= bb.damage
            if player.health <= 0:
                game_state = "GAME_OVER"

def draw():
    screen.fill((10, 12, 24))
    
    for s in stars:
        screen.draw.filled_circle((int(s["x"]), int(s["y"])), 1, (180, 180, 180))

    if game_state == "GAME_OVER":
        screen.draw.text("SYSTEM TERMINATED", center=(WIDTH // 2, HEIGHT // 2), color=(255, 40, 80), fontsize=60)
        screen.draw.text(f"FINAL SCORE: {score}", center=(WIDTH // 2, HEIGHT // 2 + 50), color=(255, 255, 255), fontsize=30)
        return

    if game_state == "VICTORY":
        screen.draw.text("UNIVERSAL VICTORY!", center=(WIDTH // 2, HEIGHT // 2), color=(0, 255, 150), fontsize=60)
        screen.draw.text(f"FINAL SCORE: {score}", center=(WIDTH // 2, HEIGHT // 2 + 50), color=(255, 255, 255), fontsize=30)
        return

    screen.draw.filled_polygon([(int(player.x), int(player.y - 20)), (int(player.x - 20), int(player.y + 20)), (int(player.x + 20), int(player.y + 20))], (0, 210, 255))
    
    for b in bullets:
        screen.draw.filled_rect(rect((int(b.x - 3), int(b.y - 8)), (6, 16)), (0, 255, 150))
        
    for d in drops:
        screen.draw.filled_circle((int(d.x), int(d.y)), 10, (255, 180, 0) if d.type == "RAPID" else (0, 150, 255))
        
    for bb in boss_bullets:
        screen.draw.filled_circle((int(bb.x), int(bb.y)), 6, (255, 255, 100))

    if game_state == "BALLS":
        for rb in red_balls:
            screen.draw.filled_circle((int(rb.x), int(rb.y)), 12, (255, 40, 80))
        screen.draw.text(f"RED BALLS: {balls_destroyed} / {balls_needed}", (WIDTH // 2 - 90, 20), color=(255, 40, 80), fontsize=30)
    elif game_state == "BOSS" and boss:
        screen.draw.filled_rect(rect((int(boss.x - boss.size//2), int(boss.y - boss.size//2)), (boss.size, boss.size)), (230, 0, 100))
        ratio = max(0.0, boss.health / boss.max_health)
        screen.draw.filled_rect(rect((WIDTH//2 - 200, 25), (400, 12)), (60, 20, 30))
        screen.draw.filled_rect(rect((WIDTH//2 - 200, 25), (int(400 * ratio), 12)), (230, 0, 100))
        screen.draw.text(f"BOSS TIER: {boss_tier} / 5", (WIDTH // 2 - 60, 45), color=(230, 0, 100), fontsize=24)

    screen.draw.filled_rect(rect((20, HEIGHT - 35), (200, 15)), (50, 50, 50))
    p_ratio = max(0.0, player.health / player.max_health)
    screen.draw.filled_rect(rect((20, HEIGHT - 35), (int(200 * p_ratio), 15)), (0, 210, 255))
    
    screen.draw.text(f"SCORE: {score}", (20, 20), color=(255, 255, 255), fontsize=24)
    screen.draw.text(f"RAPID SPEED STACKS: {player.rapid_stacks}", (20, 48), color=(255, 180, 0), fontsize=20)
