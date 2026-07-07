import random
import time
import sys

# Smooth text scrolling effect
def type_text(text, delay=0.02):
    for char in text:
        sys.stdout.write(char)
        sys.stdout.flush()
        time.sleep(delay)
    print()

# Character Stats Setup
class Player:
    def __init__(self):
        self.hp = 100
        self.max_hp = 100
        self.attack = 15
        self.gold = 0
        self.weapon = "Rusty Cyber-Blade"
        self.inventory = ["Nano-Bandaid"]

# Random Enemy Generator
class Enemy:
    def __init__(self, floor):
        prefixes = ["Glitchy", "Corrupted", "Neon", "Overclocked", "Quantum"]
        types = ["Scrapper", "Drone", "Android", "Cyborg", "AI-Beast"]
        self.name = f"{random.choice(prefixes)} {random.choice(types)}"
        self.hp = random.randint(30, 60) + (floor * 10)
        self.attack = random.randint(8, 15) + (floor * 3)
        self.gold = random.randint(10, 40) + (floor * 5)

# Main Game Loop
def play_game():
    player = Player()
    floor = 1
    
    type_text("🌐 INITIALIZING CYBER-DUNGEON ESCAPE...", 0.05)
    time.sleep(0.5)
    
    while player.hp > 0:
        type_text(f"\n--- 💾 GRID FLOOR: {floor} ---")
        type_text(f"HP: {player.hp}/{player.max_hp} | Weapon: {player.weapon} | Gold: {player.gold}💵")
        
        # Pick room type randomly
        room_event = random.choice(["combat", "combat", "loot", "mystery", "shop"])
        
        if room_event == "combat":
            enemy = Enemy(floor)
            type_text(f"⚠️ WARNING! A {enemy.name} (HP: {enemy.hp}) drops from the ceiling grid!")
            
            while enemy.hp > 0 and player.hp > 0:
                action = input("Do you want to (A)ttack, (U)se Item, or (R)un? ").lower()
                
                if action == 'a':
                    dmg_to_enemy = random.randint(int(player.attack * 0.8), int(player.attack * 1.2))
                    enemy.hp -= dmg_to_enemy
                    type_text(f"⚔️ You slash the {enemy.name} with your {player.weapon} for {dmg_to_enemy} dmg!")
                    
                    if enemy.hp > 0:
                        dmg_to_player = random.randint(int(enemy.attack * 0.8), int(enemy.attack * 1.2))
                        player.hp -= dmg_to_player
                        type_text(f"⚡ The {enemy.name} counters and hits you for {dmg_to_player} dmg!")
                
                elif action == 'u':
                    if "Nano-Bandaid" in player.inventory:
                        player.inventory.remove("Nano-Bandaid")
                        player.hp = min(player.max_hp, player.hp + 40)
                        type_text(f"💉 Applied Nano-Bandaid! Recharged 40 HP. Current HP: {player.hp}")
                    else:
                        type_text("❌ Your inventory is empty!")
                
                elif action == 'r':
                    if random.random() > 0.5:
                        type_text("💨 You successfully hacked the door open and escaped!")
                        break
                    else:
                        dmg_to_player = enemy.attack
                        player.hp -= dmg_to_player
                        type_text(f"❌ Escape failed! The {enemy.name} blasts you for {dmg_to_player} dmg as you trip!")
            
            if enemy.hp <= 0:
                type_text(f"💀 Defeated {enemy.name}! Found {enemy.gold} credits.")
                player.gold += enemy.gold
                if random.random() > 0.6:
                    player.inventory.append("Nano-Bandaid")
                    type_text("📦 Found a leftover Nano-Bandaid on the scrap pile!")
                    
        elif room_event == "loot":
            weapons = ["Laser-Katana", "Plasma-Rifle", "Sonic-Maul", "Photon-Saber"]
            if random.random() > 0.5:
                player.weapon = random.choice(weapons)
                player.attack += random.randint(5, 12)
                type_text(f"🎁 LOOT COMPARTMENT DETECTED! Equipping: {player.weapon} (Attack Boosted!)")
            else:
                found_gold = random.randint(20, 100)
                player.gold += found_gold
                type_text(f"💰 Siphoned an unlocked crypto terminal! Gained {found_gold} credits.")
                
        elif room_event == "mystery":
            type_text("❓ You find a strange neon vending machine flickering in the dark.")
            choice = input("Kick it for free loot? (y/n): ").lower()
            if choice == 'y':
                if random.random() > 0.4:
                    player.max_hp += 20
                    player.hp += 20
                    type_text("🥤 It dropped a Super-Charge Soda! Max HP permanent increase!")
                else:
                    player.hp -= 15
                    type_text("💥 ERROR! The terminal short-circuited and shocked you for 15 dmg!")
            else:
                type_text("Sensible move. You safely bypass the machine.")
                
        elif room_event == "shop":
            type_text(f"🏪 A friendly Black-Market Drone hovers near. You have {player.gold} credits.")
           
            if buy == 'y':
                if player.gold >= 30:
                    player.gold -= 30
                    player.inventory.append("Nano-Bandaid")
                    type_text("🛍️ Purchase confirmed! Item added to grid storage.")
                else:
                    type_text("❌ Insufficient credits!")
            else:
                type_text("You wave the drone away.")

        if player.hp > 0:
            input("\n[Press Enter to advance deeper into the grid...]")
            floor += 1

    type_text("\n💀 SYSTEM CRASH... PLAYER FLATLINED. GAME OVER. 💀")
    type_text(f"You survived until Floor {floor} and acquired {player.gold} total credits.")

# Run the game launcher
if __name__ == "__main__":
    play_game()
