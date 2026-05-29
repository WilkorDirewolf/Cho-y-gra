import pygame
import sys
import random
import math

# Inicjalizacja Pygame
pygame.init()
pygame.mixer.init()

# Konfiguracja okna
WIDTH, HEIGHT = 950, 700
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Krzykacz: Tajemnica Chołów - Edycja RPG")
clock = pygame.time.Clock()

# --- STANY GRY ---
STATE_EXPLORE = "EXPLORE"
STATE_HOUSE = "HOUSE"
STATE_DIALOGUE = "DIALOGUE"
STATE_DICE_ROLL = "DICE_ROLL"
STATE_COMBAT = "COMBAT"
STATE_END = "END" 

# Zmienna przechowująca skutek decyzji na końcu
end_message = ""

# --- TYPY WALKI ---
BOSS_MAMUNA = "MAMUNA"
BOSS_LATARNIK = "LATARNIK"
BOSS_PIEN = "PIEN"
BOSS_KRZYKACZ = "KRZYKACZ"

# --- ZASOBY AUDIO ---
current_music_state = None
def play_dynamic_music(state_type):
    global current_music_state
    if current_music_state == state_type:
        return
    current_music_state = state_type
    print(f"[AUDIO LOG]: Zmiana muzyki na styl: {state_type}")

# --- PROCEDURALNY SILNIK GRAFICZNY ---
def draw_drozd(surface, x, y):
    pygame.draw.rect(surface, (20, 20, 20), (x + 6, y + 34, 6, 8))
    pygame.draw.rect(surface, (20, 20, 20), (x + 18, y + 34, 6, 8))
    pygame.draw.rect(surface, (45, 50, 65), (x + 2, y + 14, 26, 22))
    pygame.draw.line(surface, (15, 15, 20), (x + 15, y + 14), (x + 15, y + 36), 2)
    pygame.draw.circle(surface, (230, 190, 160), (x + 15, y + 10), 7)
    pygame.draw.circle(surface, (10, 10, 15), (x + 12, y + 9), 1)
    pygame.draw.circle(surface, (10, 10, 15), (x + 18, y + 9), 1)
    pygame.draw.ellipse(surface, (25, 25, 30), (x - 2, y + 2, 34, 6))
    pygame.draw.rect(surface, (25, 25, 30), (x + 6, y - 2, 18, 6))

def draw_slavic_house(surface, x, y, width, height):
    pygame.draw.rect(surface, (85, 55, 35), (x, y + 30, width, height - 30))
    for i in range(y + 35, y + height, 12):
        pygame.draw.line(surface, (50, 30, 15), (x, i), (x + width, i), 2)
    pygame.draw.rect(surface, (40, 25, 10), (x + width//2 - 15, y + height - 40, 30, 40))
    pygame.draw.circle(surface, (200, 160, 40), (x + width//2 + 10, y + height - 20), 2)
    pygame.draw.rect(surface, (220, 140, 30), (x + 20, y + 45, 25, 25))
    pygame.draw.rect(surface, (30, 20, 10), (x + 20, y + 45, 25, 25), 2)
    pygame.draw.polygon(surface, (110, 90, 60), [(x - 10, y + 30), (x + width // 2, y - 10), (x + width + 10, y + 30)])
    pygame.draw.polygon(surface, (60, 45, 30), [(x - 10, y + 30), (x + width // 2, y - 10), (x + width + 10, y + 30)], 2)

def draw_monster_latarnik(surface, x, y, anim_tick):
    offset_y = int(math.sin(anim_tick * 0.1) * 5)
    pygame.draw.polygon(surface, (50, 50, 50), [(x, y+20+offset_y), (x+15, y-5+offset_y), (x+30, y+20+offset_y), (x+25, y+45+offset_y), (x+5, y+45+offset_y)])
    pygame.draw.circle(surface, (210, 210, 190), (x + 15, y + offset_y), 8)
    pygame.draw.circle(surface, (150, 0, 0), (x + 12, y - 1 + offset_y), 2)
    pygame.draw.circle(surface, (150, 0, 0), (x + 18, y - 1 + offset_y), 2)
    lantern_x = x + 35 + int(math.sin(anim_tick * 0.05) * 3)
    lantern_y = y + 15 + offset_y
    pygame.draw.line(surface, (10, 10, 10), (x + 20, y + 10 + offset_y), (lantern_x, lantern_y), 2)
    pygame.draw.circle(surface, (255, 30, 30), (lantern_x, lantern_y + 10), 10)
    pygame.draw.circle(surface, (255, 200, 200), (lantern_x, lantern_y + 10), 4)

def draw_monster_pien(surface, x, y):
    pygame.draw.rect(surface, (55, 45, 40), (x, y, 40, 50))
    pygame.draw.ellipse(surface, (35, 25, 20), (x, y - 5, 40, 15))
    pygame.draw.line(surface, (180, 20, 20), (x + 10, y + 15), (x + 30, y + 25), 3)
    pygame.draw.circle(surface, (255, 255, 255), (x + 20, y + 20), 3)
    pygame.draw.circle(surface, (200, 0, 0), (x + 20, y + 20), 1)

def draw_monster_mamuna(surface, x, y, anim_tick):
    offset_x = int(math.sin(anim_tick * 0.08) * 3)
    pygame.draw.ellipse(surface, (20, 45, 25), (x - 5 + offset_x, y + 5, 40, 40))
    pygame.draw.circle(surface, (140, 155, 120), (x + 15 + offset_x, y), 9)
    pygame.draw.circle(surface, (255, 255, 255), (x + 11 + offset_x, y - 1), 2)
    pygame.draw.circle(surface, (255, 255, 255), (x + 18 + offset_x, y - 1), 2)
    pygame.draw.line(surface, (100, 120, 90), (x + 5, y + 20), (x - 10 + offset_x, y + 35), 2)
    pygame.draw.line(surface, (100, 120, 90), (x + 25, y + 20), (x + 40 + offset_x, y + 35), 2)

def draw_monster_krzykacz(surface, x, y, anim_tick):
    scale = 1.0 + math.sin(anim_tick * 0.2) * 0.08
    w, h = int(35 * scale), int(45 * scale)
    pygame.draw.ellipse(surface, (70, 40, 85), (x - w//2 + 15, y - h//2 + 20, w, h))
    pygame.draw.circle(surface, (10, 5, 15), (x + 15, y + 22), int(8 * scale))
    pygame.draw.circle(surface, (255, 255, 255), (x + 7, y + 10), 3)
    pygame.draw.circle(surface, (255, 255, 255), (x + 23, y + 10), 3)

# --- KLASY MAPY I LOGIKI ---
class House:
    def __init__(self, x, y, w, h, name, npc_text, choices):
        self.rect = pygame.Rect(x, y, w, h)
        self.door_rect = pygame.Rect(x + w//2 - 15, y + h - 15, 30, 20)
        self.name = name
        self.npc_text = npc_text
        self.choices = choices

class Projectile:
    def __init__(self, x, y, vx, vy, color=(255, 50, 50), radius=5):
        self.x = x
        self.y = y
        self.vx = vx
        self.vy = vy
        self.color = color
        self.radius = radius

    def update(self):
        self.x += self.vx
        self.y += self.vy

    def draw(self, surface):
        pygame.draw.circle(surface, self.color, (int(self.x), int(self.y)), self.radius)

# INITIALIZATION DATA
current_state = STATE_EXPLORE
anim_tick = 0

# Statystyki gracza
player_pos = pygame.Vector2(150, 400)
player_hp = 100
player_max_hp = 100
base_attack = 10
mod_attack = 0
mod_stamina = 0

# Przeciwnicy na mapie
active_boss_type = None
boss_hp = 100
boss_max_hp = 100
boss_mod_attack = 0
boss_mod_stamina = 0

# Drzewo Dialogowe i Wybory Fabularne
dialogue_title = ""
dialogue_lines = []
dialogue_choices = []
current_choice_idx = 0
story_flags = {"spalona_chata_zbadana": False, "zaufanie_wioski": 0}

# Budynki (Dodano więcej podziałów na nowe linie dla lepszej czytelności)
houses = [
    House(100, 120, 160, 110, "Chata Sołtysa", 
          "Sołtys: Coś gnębi naszą wieś od lasu...\nLatarnik mami podróżnych,\na Krzykacz nie daje spać nocami. Pomożesz nam?",
          [("Obiecuję pozbyć się potworów (Dobra ścieżka)", "SOLTYS_GOOD"), 
           ("Zrobię to wyłącznie dla zapłaty (Ścieżka Najemnika)", "SOLTYS_GREED")]),
    House(550, 150, 140, 100, "Stara Zielarka", 
          "Zielarka: Czuję od Ciebie zapach śmierci, miastowy.\nJeśli ruszysz na Mamunę,\nstrzeż się jej pieśni hipnotycznej.",
          [("Weź amulet ochronny (-10 monet)", "AMULET"), ("Odejdź bez słowa", "LEAVE")])
]

# Pozycje potworów na mapie eksploracji
monster_triggers = [
    {"rect": pygame.Rect(420, 180, 40, 50), "type": BOSS_LATARNIK, "beaten": False},
    {"rect": pygame.Rect(780, 450, 40, 50), "type": BOSS_PIEN, "beaten": False},
    {"rect": pygame.Rect(750, 100, 40, 50), "type": BOSS_MAMUNA, "beaten": False},
    {"rect": pygame.Rect(120, 520, 40, 50), "type": BOSS_KRZYKACZ, "beaten": False}
]

# Inicjalizacja Minigier
combat_projectiles = []
combat_timer = 0
player_combat_pos = pygame.Vector2(WIDTH//2, HEIGHT//2 + 100)
combat_bullets = [] 

font_main = pygame.font.SysFont("georgia", 22)
font_sub = pygame.font.SysFont("arial", 16)

# Tło makiety wsi
terrain_surface = pygame.Surface((WIDTH, HEIGHT))
for ty in range(0, HEIGHT, 50):
    for tx in range(0, WIDTH, 50):
        base_g = random.randint(30, 45)
        base_r = int(base_g * 0.9)
        base_b = int(base_g * 0.7)
        pygame.draw.rect(terrain_surface, (base_r, base_g, base_b), (tx, ty, 50, 50))
        if random.random() > 0.85:
            pygame.draw.line(terrain_surface, (40, 55, 30), (tx+20, ty+20), (tx+23, ty+10), 2)

# --- GŁÓWNA PĘTLA SYSTEMOWA ---
running = True
while running:
    anim_tick += 1
    dt = clock.tick(60)
    keys = pygame.key.get_pressed()

    # ==========================================
    # 1. OBSŁUGA LOGIKI
    # ==========================================
    if current_state in [STATE_EXPLORE, STATE_HOUSE]:
        play_dynamic_music("EXPLORE")
        move_vector = pygame.Vector2(0, 0)
        if keys[pygame.K_w] or keys[pygame.K_UP]: move_vector.y -= 4
        if keys[pygame.K_s] or keys[pygame.K_DOWN]: move_vector.y += 4
        if keys[pygame.K_a] or keys[pygame.K_LEFT]: move_vector.x -= 4
        if keys[pygame.K_d] or keys[pygame.K_RIGHT]: move_vector.x += 4
        
        if move_vector.length() > 0:
            move_vector = move_vector.normalize() * 4
            player_pos += move_vector

        if current_state == STATE_EXPLORE:
            player_pos.x = max(20, min(WIDTH-20, player_pos.x))
            player_pos.y = max(20, min(HEIGHT-20, player_pos.y))
            
            # Wchodzenie do budynków
            for h in houses:
                if h.door_rect.collidepoint(player_pos.x, player_pos.y):
                    current_state = STATE_HOUSE
                    player_pos = pygame.Vector2(h.rect.x + h.rect.width//2, h.rect.y + h.rect.height - 30)
                    break
            
            # Startowanie walki
            for m in monster_triggers:
                if not m["beaten"] and m["rect"].collidepoint(player_pos.x, player_pos.y):
                    active_boss_type = m["type"]
                    current_state = STATE_DICE_ROLL
                    dice_timer = 0
                    p_dice1, p_dice2 = random.randint(1, 6), random.randint(1, 6)
                    m_dice1, m_dice2 = random.randint(1, 6), random.randint(1, 6)
                    mod_attack = (p_dice1 + p_dice2) - 6
                    mod_stamina = (p_dice1 + p_dice2) // 2
                    boss_mod_attack = (m_dice1 + m_dice2) - 6
                    boss_mod_stamina = (m_dice1 + m_dice2) // 2
                    boss_hp = 100 + (boss_mod_stamina * 5)
                    boss_max_hp = boss_hp
                    break
            
            # SPRAWDZENIE CZY WYGRALIŚMY GRĘ
            if all(m["beaten"] for m in monster_triggers):
                end_message = "Pokonałeś wszystkie potwory! Wioska Choły jest znów bezpieczna."
                if story_flags["zaufanie_wioski"] > 0:
                    end_message += " Zostałeś bohaterem."
                current_state = STATE_END

        elif current_state == STATE_HOUSE:
            in_any_house = False
            for h in houses:
                if h.rect.inflate(40, 40).collidepoint(player_pos.x, player_pos.y):
                    in_any_house = True
                    if pygame.Vector2(player_pos.x, player_pos.y).distance_to(pygame.Vector2(h.rect.centerx, h.rect.centery)) < 40:
                        current_state = STATE_DIALOGUE
                        dialogue_title = h.name
                        dialogue_lines = [h.npc_text]
                        dialogue_choices = h.choices
                        current_choice_idx = 0
            if not in_any_house:
                current_state = STATE_EXPLORE

    elif current_state == STATE_COMBAT:
        play_dynamic_music("BATTLE")
        combat_timer += 1
        
        c_speed = 5
        if keys[pygame.K_w] or keys[pygame.K_UP]: player_combat_pos.y -= c_speed
        if keys[pygame.K_s] or keys[pygame.K_DOWN]: player_combat_pos.y += c_speed
        if keys[pygame.K_a] or keys[pygame.K_LEFT]: player_combat_pos.x -= c_speed
        if keys[pygame.K_d] or keys[pygame.K_RIGHT]: player_combat_pos.x += c_speed
        player_combat_pos.x = max(100, min(WIDTH-100, player_combat_pos.x))
        player_combat_pos.y = max(150, min(HEIGHT-50, player_combat_pos.y))
        
        if active_boss_type == BOSS_LATARNIK:
            if combat_timer % 40 == 0:
                dx = player_combat_pos.x - (WIDTH//2)
                dy = player_combat_pos.y - 220
                dist = math.hypot(dx, dy) if math.hypot(dx, dy) != 0 else 1
                combat_projectiles.append(Projectile(WIDTH//2, 220, (dx/dist)*6, (dy/dist)*6, (255, 60, 0), 7))
            if combat_timer % 60 == 0:
                boss_hp -= (base_attack + mod_attack)

        elif active_boss_type == BOSS_MAMUNA:
            if combat_timer % 50 == 0:
                combat_projectiles.append(Projectile(WIDTH//2, 250, 0, 0, (100, 255, 100), 10))
            for p in combat_projectiles:
                if p.vx == 0 and p.vy == 0:
                    p.radius += 3 
                    if p.radius > 220: combat_projectiles.remove(p)
                    elif p.radius - 10 < player_combat_pos.distance_to(pygame.Vector2(WIDTH//2, 250)) < p.radius + 10:
                        player_hp -= max(1, 3 + boss_mod_attack)
            if combat_timer % 60 == 0:
                boss_hp -= (base_attack + mod_attack)

        elif active_boss_type == BOSS_PIEN:
            if combat_timer % 30 == 0:
                combat_projectiles.append(Projectile(player_combat_pos.x + random.randint(-20,20), player_combat_pos.y + random.randint(-20,20), 0, 0, (139, 69, 19), 2))
            for p in combat_projectiles:
                if p.color == (139, 69, 19):
                    p.radius += 0.5
                    if p.radius >= 15: 
                        if pygame.Vector2(p.x, p.y).distance_to(player_combat_pos) < 25:
                            player_hp -= max(1, 8 + boss_mod_attack)
                        combat_projectiles.remove(p)
            if combat_timer % 60 == 0:
                boss_hp -= (base_attack + mod_attack)

        elif active_boss_type == BOSS_KRZYKACZ:
            if combat_timer % 45 == 0:
                for angle in range(0, 360, 60):
                    rad = math.radians(angle)
                    combat_projectiles.append(Projectile(WIDTH//2, 220, math.cos(rad)*4, math.sin(rad)*4, (200, 100, 255), 6))
            if keys[pygame.K_SPACE] and combat_timer % 15 == 0:
                combat_bullets.append(Projectile(player_combat_pos.x, player_combat_pos.y, 0, -8, (255, 255, 255), 4))
                
            for b in combat_bullets:
                b.update()
                if pygame.Vector2(b.x, b.y).distance_to(pygame.Vector2(WIDTH//2, 220)) < 30:
                    boss_hp -= (base_attack + mod_attack + 2)
                    combat_bullets.remove(b)
                elif b.y < 100:
                    combat_bullets.remove(b)

        for p in combat_projectiles:
            if p.vx != 0 or p.vy != 0:
                p.update()
                if pygame.Vector2(p.x, p.y).distance_to(player_combat_pos) < 20:
                    player_hp -= max(1, 5 + boss_mod_attack)
                    combat_projectiles.remove(p)
                elif p.x < 0 or p.x > WIDTH or p.y < 0 or p.y > HEIGHT:
                    combat_projectiles.remove(p)

        if boss_hp <= 0:
            for m in monster_triggers:
                if m["type"] == active_boss_type: m["beaten"] = True
            current_state = STATE_EXPLORE
            combat_projectiles.clear()
            combat_bullets.clear()
        elif player_hp <= 0:
            end_message = "Jerzy Drozd poległ w Chołach... Zostałeś pokonany."
            current_state = STATE_END

    # ==========================================
    # 2. EVENT LOOP
    # ==========================================
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
            
        elif event.type == pygame.KEYDOWN:
            
            if current_state == STATE_DIALOGUE:
                if event.key == pygame.K_w or event.key == pygame.K_UP:
                    current_choice_idx = (current_choice_idx - 1) % len(dialogue_choices)
                elif event.key == pygame.K_s or event.key == pygame.K_DOWN:
                    current_choice_idx = (current_choice_idx + 1) % len(dialogue_choices)
                elif event.key == pygame.K_RETURN or event.key == pygame.K_e:
                    choice_code = dialogue_choices[current_choice_idx][1]
                    
                    # ZMIANA: Zamiast kończyć grę, gracz wraca do domu (i eksploracji) by walczyć
                    if choice_code == "SOLTYS_GOOD": 
                        story_flags["zaufanie_wioski"] += 5
                        current_state = STATE_HOUSE
                        player_pos.y += 50 
                    elif choice_code == "SOLTYS_GREED": 
                        story_flags["zaufanie_wioski"] -= 2
                        current_state = STATE_HOUSE
                        player_pos.y += 50 
                    elif choice_code == "AMULET": 
                        player_hp = min(120, player_hp + 20)
                        current_state = STATE_HOUSE
                        player_pos.y += 50 
                    elif choice_code == "LEAVE":
                        current_state = STATE_HOUSE
                        player_pos.y += 50

            elif current_state == STATE_END:
                if event.key == pygame.K_ESCAPE:
                    running = False
            
            elif current_state == STATE_DICE_ROLL:
                if event.key == pygame.K_RETURN or event.key == pygame.K_SPACE:
                    current_state = STATE_COMBAT
                    combat_timer = 0
                    combat_projectiles.clear()
                    player_combat_pos = pygame.Vector2(WIDTH//2, HEIGHT//2 + 150)

    # ==========================================
    # 3. RENDEROWANIE
    # ==========================================
    if current_state in [STATE_EXPLORE, STATE_DIALOGUE, STATE_DICE_ROLL]:
        screen.blit(terrain_surface, (0, 0))
        for h in houses:
            draw_slavic_house(screen, h.rect.x, h.rect.y, h.rect.width, h.rect.height)
            
        for m in monster_triggers:
            if not m["beaten"]:
                if m["type"] == BOSS_LATARNIK: draw_monster_latarnik(screen, m["rect"].x, m["rect"].y, anim_tick)
                elif m["type"] == BOSS_PIEN: draw_monster_pien(screen, m["rect"].x, m["rect"].y)
                elif m["type"] == BOSS_MAMUNA: draw_monster_mamuna(screen, m["rect"].x, m["rect"].y, anim_tick)
                elif m["type"] == BOSS_KRZYKACZ: draw_monster_krzykacz(screen, m["rect"].x, m["rect"].y, anim_tick)

        draw_drozd(screen, int(player_pos.x) - 15, int(player_pos.y) - 20)

    elif current_state == STATE_HOUSE:
        screen.fill((25, 20, 15)) 
        pygame.draw.rect(screen, (45, 35, 25), (50, 50, WIDTH-100, HEIGHT-100), 8) 
        pygame.draw.rect(screen, (70, 50, 35), (WIDTH//2 - 40, HEIGHT//2 - 20, 80, 50))
        pygame.draw.circle(screen, (200, 150, 120), (WIDTH//2, HEIGHT//2 - 60), 10)
        pygame.draw.rect(screen, (60, 90, 70), (WIDTH//2 - 12, HEIGHT//2 - 50, 24, 25))
        draw_drozd(screen, int(player_pos.x) - 15, int(player_pos.y) - 20)
        
        lbl = font_sub.render("Podejdź do mieszkańca, by rozmawiać. Wyjdź poza ramę, by opuścić dom.", True, (150, 150, 150))
        screen.blit(lbl, (70, HEIGHT - 40))

    elif current_state == STATE_COMBAT:
        screen.fill((10, 12, 18))
        pygame.draw.rect(screen, (150, 30, 30), (80, 100, WIDTH-160, HEIGHT-160), 3) 
        
        pygame.draw.rect(screen, (40, 40, 40), (80, 30, 250, 20))
        pygame.draw.rect(screen, (200, 30, 30), (80, 30, int(250 * (player_hp/player_max_hp)), 20))
        screen.blit(font_sub.render(f"Drozd HP: {player_hp}/{player_max_hp} (Mod. Ataku: +{mod_attack})", True, (255,255,255)), (85, 32))
        
        pygame.draw.rect(screen, (40, 40, 40), (WIDTH - 330, 30, 250, 20))
        pygame.draw.rect(screen, (160, 30, 160), (WIDTH - 330, 30, int(250 * max(0, boss_hp/boss_max_hp)), 20))
        screen.blit(font_sub.render(f"{active_boss_type} HP: {int(boss_hp)}/{int(boss_max_hp)}", True, (255,255,255)), (WIDTH - 325, 32))

        bx, by = WIDTH // 2 - 15, 200
        if active_boss_type == BOSS_LATARNIK: draw_monster_latarnik(screen, bx, by, anim_tick)
        elif active_boss_type == BOSS_PIEN: draw_monster_pien(screen, bx, by)
        elif active_boss_type == BOSS_MAMUNA: draw_monster_mamuna(screen, bx, by, anim_tick)
        elif active_boss_type == BOSS_KRZYKACZ: draw_monster_krzykacz(screen, bx, by, anim_tick)

        for p in combat_projectiles: p.draw(screen)
        for b in combat_bullets: b.draw(screen)

        draw_drozd(screen, int(player_combat_pos.x) - 15, int(player_combat_pos.y) - 20)
        
        if active_boss_type == BOSS_KRZYKACZ:
            screen.blit(font_sub.render("[SPACJA] - Strzał z Kuszy  [STRZAŁKI] - Uniki", True, (200, 200, 255)), (WIDTH//2 - 150, HEIGHT - 45))
        else:
            screen.blit(font_sub.render("[STRZAŁKI] - Unikaj ataków i przetrwaj, by zadać ciosy!", True, (255, 200, 200)), (WIDTH//2 - 180, HEIGHT - 45))

    elif current_state == STATE_DIALOGUE:
        pygame.draw.rect(screen, (15, 12, 10), (50, 450, WIDTH-100, 220))
        pygame.draw.rect(screen, (180, 140, 90), (50, 450, WIDTH-100, 220), 4)
        
        t_surf = font_main.render(dialogue_title, True, (255, 215, 0))
        screen.blit(t_surf, (80, 465))
        
        # POPRAWKA 1: Generowanie tekstu NPC ze złamaniem wierszy 
        lines = dialogue_lines[0].split('\n')
        for idx, l in enumerate(lines):
            l_surf = font_sub.render(l, True, (230, 220, 210))
            screen.blit(l_surf, (80, 500 + idx*22))
            
        # POPRAWKA 2: Przeniesienie opcji wyboru POD główny tekst (zamiast obok)
        for idx, choice in enumerate(dialogue_choices):
            color = (255, 255, 100) if idx == current_choice_idx else (140, 140, 140)
            prefix = " > " if idx == current_choice_idx else "   "
            c_surf = font_sub.render(prefix + choice[0], True, color)
            screen.blit(c_surf, (80, 580 + idx * 25))
            
        screen.blit(font_sub.render("[W/S] Wybór  [ENTER] Potwierdź", True, (100, 100, 100)), (80, 640))

    elif current_state == STATE_DICE_ROLL:
        pygame.draw.rect(screen, (10, 10, 15), (150, 180, WIDTH-300, 350))
        pygame.draw.rect(screen, (220, 50, 50), (150, 180, WIDTH-300, 350), 3)
        
        title = font_main.render(f"ZASADZKA! PRZECIWNIK: {active_boss_type}", True, (255, 50, 50))
        screen.blit(title, (WIDTH//2 - title.get_width()//2, 210))
        
        p_str = f"Twój rzut kośćmi: Mod. Ataku ({mod_attack: +d}), Mod. Wytrzymałości ({mod_stamina: +d})"
        m_str = f"Rzut wroga: Mod. Ataku ({boss_mod_attack: +d}), Mod. Wytrzymałości ({boss_mod_stamina: +d})"
        
        screen.blit(font_main.render(p_str, True, (100, 255, 100)), (200, 290))
        screen.blit(font_main.render(m_str, True, (255, 100, 100)), (200, 350))
        
        prompt = font_main.render("NACIŚNIJ [ENTER], ABY ROZPOCZĄĆ MINIGIERĘ WALKI", True, (255, 255, 255))
        screen.blit(prompt, (WIDTH//2 - prompt.get_width()//2, 450))
    
    elif current_state == STATE_END:
        screen.fill((15, 10, 10))
        
        title_surf = font_main.render("KONIEC", True, (200, 50, 50))
        screen.blit(title_surf, (WIDTH//2 - title_surf.get_width()//2, HEIGHT//2 - 60))
        
        msg_surf = font_sub.render(end_message, True, (220, 220, 200))
        screen.blit(msg_surf, (WIDTH//2 - msg_surf.get_width()//2, HEIGHT//2))
        
        exit_surf = font_sub.render("[Naciśnij ESC aby zamknąć grę]", True, (100, 100, 100))
        screen.blit(exit_surf, (WIDTH//2 - exit_surf.get_width()//2, HEIGHT - 50))

    pygame.display.flip()

pygame.quit()
sys.exit()
