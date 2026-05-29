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
pygame.display.set_caption("Krzykacz: Tajemnica Chołów - Śledztwo RPG")
clock = pygame.time.Clock()

# --- STANY GRY ---
STATE_INTRO = "INTRO"
STATE_EXPLORE = "EXPLORE"
STATE_HOUSE = "HOUSE"
STATE_DIALOGUE = "DIALOGUE"
STATE_DICE_ROLL = "DICE_ROLL"
STATE_COMBAT = "COMBAT"
STATE_END = "END" 

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

def draw_slavic_house(surface, x, y, width, height, roof_color=(110, 90, 60), ruined=False):
    base_color = (85, 55, 35) if not ruined else (40, 35, 35)
    line_color = (50, 30, 15) if not ruined else (20, 20, 20)
    
    pygame.draw.rect(surface, base_color, (x, y + 30, width, height - 30))
    for i in range(y + 35, y + height, 12):
        pygame.draw.line(surface, line_color, (x, i), (x + width, i), 2)
    
    pygame.draw.rect(surface, (40, 25, 10) if not ruined else (15, 15, 15), (x + width//2 - 15, y + height - 40, 30, 40))
    if not ruined:
        pygame.draw.circle(surface, (200, 160, 40), (x + width//2 + 10, y + height - 20), 2)
        pygame.draw.rect(surface, (220, 140, 30), (x + 20, y + 45, 25, 25))
        pygame.draw.rect(surface, (30, 20, 10), (x + 20, y + 45, 25, 25), 2)
        pygame.draw.polygon(surface, roof_color, [(x - 10, y + 30), (x + width // 2, y - 10), (x + width + 10, y + 30)])
    else:
        # Zrujnowany, dziurawy dach
        pygame.draw.polygon(surface, (50, 45, 45), [(x - 10, y + 30), (x + width // 3, y + 5), (x + width + 10, y + 30)])
    
    pygame.draw.polygon(surface, (60, 45, 30) if not ruined else (10, 10, 10), [(x - 10, y + 30), (x + width // 2, y - 10), (x + width + 10, y + 30)], 2)

def draw_zuk(surface, x, y):
    pygame.draw.rect(surface, (80, 110, 90), (x, y, 220, 90), border_radius=12)
    pygame.draw.rect(surface, (90, 85, 75), (x+5, y-20, 140, 110), border_radius=5)
    pygame.draw.line(surface, (60, 55, 45), (x+40, y-20), (x+40, y+90), 3)
    pygame.draw.line(surface, (60, 55, 45), (x+90, y-20), (x+90, y+90), 3)
    pygame.draw.polygon(surface, (120, 160, 190), [(x+155, y+10), (x+195, y+25), (x+205, y+50), (x+155, y+50)])
    pygame.draw.circle(surface, (20, 20, 20), (x + 50, y + 90), 22)
    pygame.draw.circle(surface, (100, 100, 100), (x + 50, y + 90), 8)
    pygame.draw.circle(surface, (20, 20, 20), (x + 170, y + 90), 22)
    pygame.draw.circle(surface, (100, 100, 100), (x + 170, y + 90), 8)
    pygame.draw.circle(surface, (255, 255, 180), (x + 215, y + 65), 7)

def draw_tree(surface, x, y):
    pygame.draw.rect(surface, (50, 35, 25), (x + 12, y + 24, 8, 16))
    pygame.draw.circle(surface, (25, 45, 25), (x + 16, y + 16), 18)
    pygame.draw.circle(surface, (30, 55, 30), (x + 12, y + 6), 14)

def draw_well(surface, x, y):
    pygame.draw.ellipse(surface, (80, 80, 85), (x, y + 18, 45, 25))
    pygame.draw.ellipse(surface, (40, 40, 45), (x + 4, y + 20, 37, 19))
    pygame.draw.line(surface, (95, 65, 45), (x + 6, y + 20), (x + 6, y + 2), 3)
    pygame.draw.line(surface, (95, 65, 45), (x + 39, y + 20), (x + 39, y + 2), 3)
    pygame.draw.polygon(surface, (130, 65, 40), [(x - 4, y + 4), (x + 22, y - 12), (x + 49, y + 4)])

def draw_monster_shadow(surface, x, y, anim_tick):
    # Mglisty, pulsujący cień potwora przed odkryciem prawdy
    radius = int(15 + math.sin(anim_tick * 0.1) * 4)
    alpha_surf = pygame.Surface((60, 60), pygame.SRCALPHA)
    pygame.draw.circle(alpha_surf, (80, 20, 90, 100), (30, 30), radius)
    surface.blit(alpha_surf, (x - 10, y - 5))

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

def draw_monster_krzykacz(surface, x, y, anim_tick):
    scale = 1.0 + math.sin(anim_tick * 0.2) * 0.08
    w, h = int(35 * scale), int(45 * scale)
    pygame.draw.ellipse(surface, (70, 40, 85), (x - w//2 + 15, y - h//2 + 20, w, h))
    pygame.draw.circle(surface, (10, 5, 15), (x + 15, y + 22), int(8 * scale))
    pygame.draw.circle(surface, (255, 255, 255), (x + 7, y + 10), 3)
    pygame.draw.circle(surface, (255, 255, 255), (x + 23, y + 10), 3)

# --- KLASY GRAFICZNE I DIALOGOWE ---
class House:
    def __init__(self, x, y, w, h, name, npc_text, choices, roof_color=(110, 90, 60), ruined=False):
        self.rect = pygame.Rect(x, y, w, h)
        self.door_rect = pygame.Rect(x + w//2 - 15, y + h - 15, 30, 20)
        self.name = name
        self.npc_text = npc_text
        self.choices = choices
        self.roof_color = roof_color
        self.ruined = ruined

class Projectile:
    def __init__(self, x, y, vx, vy, color=(255, 50, 50), radius=5):
        self.x, self.y = x, y
        self.vx, self.vy = vx, vy
        self.color = color
        self.radius = radius
    def update(self):
        self.x += self.vx
        self.y += self.vy
    def draw(self, surface):
        pygame.draw.circle(surface, self.color, (int(self.x), int(self.y)), self.radius)

# --- INICJACJA DANYCH SYSTEMOWYCH ---
current_state = STATE_INTRO
anim_tick = 0
active_house = None 

# System Śledztwa i Prawdy Fabularnej
clues_found = {"soltys": False, "zielarka": False, "ruiny": False}
investigation_complete = False

intro_step = 0
intro_sequence = [
    {"title": "Wnętrze Żuka. Czuć zapach tanich fajek, benzyny i leśnej wilgoci.", 
     "text": "Kierowca Władek: Mówię ci, panie Drozd. W Chołach to się porobiło niezłe bagno.\nDzieciaka w lesie znaleźli... rozszarpanego. Oficjalnie ponoć wilki zeszły z gór."},
    {"title": "Silnik rzęzi, a ciemny las za szybą zdaje się zacieśniać wokół auta.", 
     "text": "Kierowca Władek: Ale baby we wsi swoje wiedzą. Coś tu śmierdzi kłamstwem na kilometr.\nLudzie boją się własnego cienia. Ja stąd spadam przed zmrokiem."},
    {"title": "Błotnista droga przed chatą sołtysa. Wokół panuje nienaturalna cisza.", 
     "text": "Sołtys Piotr Bieniasz: Kolejny miastowy węszy... Słuchaj, Drozd.\nDostaniesz klucz do starej chaty po Mikołaju na skraju wsi. Zszedł na zawał parę lat temu.\nRozejrzyj się, popytaj, ale nie obiecuj sobie za wiele po tych bękartach z Chołów."}
]

player_pos = pygame.Vector2(215, 410) 
player_hp, player_max_hp = 100, 100
base_attack, mod_attack, mod_stamina = 10, 0, 0

active_boss_type = None
boss_hp, boss_max_hp = 100, 100
boss_mod_attack, boss_mod_stamina = 0, 0

dialogue_title = ""
dialogue_lines = []
dialogue_choices = []
current_choice_idx = 0

# Lokacje budynków
houses = [
    House(80, 100, 160, 110, "Dom Sołtysa Bieniasza", 
          "Sołtys Bieniasz: Wilki zjadły małego? Taa, tak najwygodniej mówić gminie.\nIdź pogadaj z tą starą wiedźmą, Zielarką, albo zobacz spaloną chatę Elżbiety na wschodzie.\nNikt tam od roku nie wchodzi, odkąd uciekła do lasu.",
          [("Zbadam ten ślad (Zapisz wskazówkę Sołtysa)", "CLUE_SOLTYS")]),
    
    House(140, 320, 130, 90, "Chata po starym Mikołaju", 
          "Twoja kryjówka. Pachnie stęchłym kurzem, ale łóżko jest całe.\nChcesz odpocząć?",
          [("Prześpij się (Regeneracja HP)", "SLEEP"), ("Wyjdź", "LEAVE")]),
    
    House(480, 80, 140, 100, "Namiot Starej Zielarki", 
          "Zielarka: Wilki? Głupcy wierzą w wilki! Bestie szanują krew, a tam była czysta nienawiść.\nTo jej rodzona matka, Elżbieta! Krzykacz odebrał jej rozum.\nNapaliła w piecu chlebowym i wrzuciła małego żywcem... Słyszałam ten pisk...",
          [("Wysłuchaj wstrząsającej prawdy (Zapisz wskazówkę Zielarki)", "CLUE_ZIELARKA")]),
    
    House(720, 320, 150, 110, "Spalona Chata Elżbiety", 
          "Osmalone ściany potęgują odór dawnego spalonego mięsa.\nW centralnym punkcie stoi zrujnowany piec chlebowy.\nW środku, pośród popiołu, widzisz drobne, zwęglone ludzkie kości...",
          [("Przeszukaj piec chlebowy (Zapisz dowód ze zgliszcz)", "CLUE_RUINY")], ruined=True)
]

# Dekoracje na mapie (Drzewa i Studnia)
decorations_trees = [(40, 260), (50, 500), (320, 110), (360, 180), (410, 240), (280, 550), (660, 120), (690, 200), (880, 500), (900, 250)]
well_pos = pygame.Vector2(450, 420)

monster_triggers = [
    {"rect": pygame.Rect(450, 560, 40, 50), "type": BOSS_LATARNIK, "beaten": False},
    {"rect": pygame.Rect(820, 120, 40, 50), "type": BOSS_PIEN, "beaten": False},
    {"rect": pygame.Rect(750, 550, 40, 50), "type": BOSS_MAMUNA, "beaten": False},
    {"rect": pygame.Rect(70, 560, 40, 50), "type": BOSS_KRZYKACZ, "beaten": False}
]

combat_projectiles = []
combat_timer = 0
player_combat_pos = pygame.Vector2(WIDTH//2, HEIGHT//2 + 100)
combat_bullets = [] 

font_main = pygame.font.SysFont("georgia", 20)
font_sub = pygame.font.SysFont("arial", 15)
font_title = pygame.font.SysFont("georgia", 24, bold=True)

# Generowanie tła makiety wsi
terrain_surface = pygame.Surface((WIDTH, HEIGHT))
for ty in range(0, HEIGHT, 50):
    for tx in range(0, WIDTH, 50):
        base_g = random.randint(25, 38)
        pygame.draw.rect(terrain_surface, (int(base_g*0.85), base_g, int(base_g*0.65)), (tx, ty, 50, 50))
        if random.random() > 0.88:
            pygame.draw.line(terrain_surface, (35, 48, 25), (tx+20, ty+20), (tx+22, ty+10), 2)

# --- GŁÓWNA PĘTLA SYSTEMOWA ---
running = True
while running:
    anim_tick += 1
    dt = clock.tick(60)
    keys = pygame.key.get_pressed()

    # Sprawdzenie postępu śledztwa
    if not investigation_complete and all(clues_found.values()):
        investigation_complete = True
        print("[FABUŁA LOG]: Prawda wyszła na jaw. Koszmary zmaterializowały się na mapie.")

    # ==========================================
    # 1. OBSŁUGA LOGIKI PORUSZANIA I AKCJI
    # ==========================================
    if current_state in [STATE_EXPLORE, STATE_HOUSE]:
        play_dynamic_music("EXPLORE")
        move_vector = pygame.Vector2(0, 0)
        if keys[pygame.K_w] or keys[pygame.K_UP]: move_vector.y -= 4
        if keys[pygame.K_s] or keys[pygame.K_DOWN]: move_vector.y += 4
        if keys[pygame.K_a] or keys[pygame.K_LEFT]: move_vector.x -= 4
        if keys[pygame.K_d] or keys[pygame.K_RIGHT]: move_vector.x += 4
        
        if move_vector.length() > 0:
            player_pos += move_vector.normalize() * 4

        if current_state == STATE_EXPLORE:
            player_pos.x = max(20, min(WIDTH-20, player_pos.x))
            player_pos.y = max(20, min(HEIGHT-20, player_pos.y))
            
            # Kolizje z domami i wejście
            for h in houses:
                if h.door_rect.collidepoint(player_pos.x, player_pos.y):
                    current_state = STATE_HOUSE
                    active_house = h
                    player_pos = pygame.Vector2(WIDTH // 2, HEIGHT - 130)
                    break
            
            # Reakcja na potwory
            for m in monster_triggers:
                if not m["beaten"] and m["rect"].collidepoint(player_pos.x, player_pos.y):
                    if investigation_complete:
                        active_boss_type = m["type"]
                        current_state = STATE_DICE_ROLL
                        p_dice1, p_dice2 = random.randint(1, 6), random.randint(1, 6)
                        m_dice1, m_dice2 = random.randint(1, 6), random.randint(1, 6)
                        mod_attack = (p_dice1 + p_dice2) - 6
                        mod_stamina = (p_dice1 + p_dice2) // 2
                        boss_mod_attack = (m_dice1 + m_dice2) - 6
                        boss_mod_stamina = (m_dice1 + m_dice2) // 2
                        boss_hp = 100 + (boss_mod_stamina * 5)
                        boss_max_hp = boss_hp
                    break
            
            if all(m["beaten"] for m in monster_triggers) and investigation_complete:
                end_message = "Odkryłeś prawdę i zgładziłeś demony zrodzone z koszmaru Chołów. Sprawa zamknięta."
                current_state = STATE_END

        elif current_state == STATE_HOUSE:
            dist_to_npc = pygame.Vector2(player_pos.x, player_pos.y).distance_to(pygame.Vector2(WIDTH//2, HEIGHT//2))
            if dist_to_npc < 60:
                current_state = STATE_DIALOGUE
                dialogue_title = active_house.name
                dialogue_lines = [active_house.npc_text]
                dialogue_choices = active_house.choices
                current_choice_idx = 0
            
            if player_pos.x < 50 or player_pos.x > WIDTH - 50 or player_pos.y < 50 or player_pos.y > HEIGHT - 50:
                current_state = STATE_EXPLORE
                player_pos = pygame.Vector2(active_house.door_rect.centerx, active_house.door_rect.bottom + 20)
                active_house = None

    # Logika zręcznościowej walki
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
            if combat_timer % 60 == 0: boss_hp -= (base_attack + mod_attack)

        elif active_boss_type == BOSS_MAMUNA:
            if combat_timer % 50 == 0:
                combat_projectiles.append(Projectile(WIDTH//2, 250, 0, 0, (100, 255, 100), 10))
            for p in combat_projectiles:
                if p.vx == 0 and p.vy == 0:
                    p.radius += 3 
                    if p.radius > 220: combat_projectiles.remove(p)
                    elif p.radius - 10 < player_combat_pos.distance_to(pygame.Vector2(WIDTH//2, 250)) < p.radius + 10:
                        player_hp -= max(1, 3 + boss_mod_attack)
            if combat_timer % 60 == 0: boss_hp -= (base_attack + mod_attack)

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
            if combat_timer % 60 == 0: boss_hp -= (base_attack + mod_attack)

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
                elif b.y < 100: combat_bullets.remove(b)

        for p in combat_projectiles:
            if p.vx != 0 or p.vy != 0:
                p.update()
                if pygame.Vector2(p.x, p.y).distance_to(player_combat_pos) < 20:
                    player_hp -= max(1, 5 + boss_mod_attack)
                    combat_projectiles.remove(p)
                elif p.x < 0 or p.x > WIDTH or p.y < 0 or p.y > HEIGHT: combat_projectiles.remove(p)

        if boss_hp <= 0:
            for m in monster_triggers:
                if m["type"] == active_boss_type: m["beaten"] = True
            current_state = STATE_EXPLORE
            combat_projectiles.clear()
            combat_bullets.clear()
        elif player_hp <= 0:
            end_message = "Jerzy Drozd zginął, pochłonięty przez szaleństwo Chołów."
            current_state = STATE_END

    # ==========================================
    # 2. SEKCJA EVENTÓW KLAWIATURY
    # ==========================================
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
            
        elif event.type == pygame.KEYDOWN:
            if current_state == STATE_INTRO:
                if event.key in [pygame.K_RETURN, pygame.K_SPACE]:
                    intro_step += 1
                    if intro_step >= len(intro_sequence):
                        current_state = STATE_EXPLORE

            elif current_state == STATE_DIALOGUE:
                if event.key in [pygame.K_w, pygame.K_UP]:
                    current_choice_idx = (current_choice_idx - 1) % len(dialogue_choices)
                elif event.key in [pygame.K_s, pygame.K_DOWN]:
                    current_choice_idx = (current_choice_idx + 1) % len(dialogue_choices)
                elif event.key in [pygame.K_RETURN, pygame.K_e]:
                    choice_code = dialogue_choices[current_choice_idx][1]
                    
                    if choice_code == "CLUE_SOLTYS":
                        clues_found["soltys"] = True
                    elif choice_code == "CLUE_ZIELARKA":
                        clues_found["zielarka"] = True
                    elif choice_code == "CLUE_RUINY":
                        clues_found["ruiny"] = True
                    elif choice_code == "SLEEP":
                        player_hp = player_max_hp
                    
                    current_state = STATE_HOUSE
                    player_pos.y += 70 

            elif current_state == STATE_END:
                if event.key == pygame.K_ESCAPE: running = False
            
            elif current_state == STATE_DICE_ROLL:
                if event.key in [pygame.K_RETURN, pygame.K_SPACE]:
                    current_state = STATE_COMBAT
                    combat_timer = 0
                    combat_projectiles.clear()
                    player_combat_pos = pygame.Vector2(WIDTH//2, HEIGHT//2 + 150)

    # ==========================================
    # 3. RENDEROWANIE EKRANÓW
    # ==========================================
    
    # INTRO CUTSCENKA
    if current_state == STATE_INTRO:
        screen.fill((12, 15, 12))
        if intro_step < 2:
            pygame.draw.rect(screen, (30, 28, 25), (0, HEIGHT//2 + 50, WIDTH, HEIGHT//2))
            draw_zuk(screen, WIDTH//2 - 100 + int(math.sin(anim_tick * 0.1) * 3), HEIGHT//2 - 60 + int(math.cos(anim_tick * 0.2) * 2))
        else:
            draw_slavic_house(screen, WIDTH//2 - 100, HEIGHT//2 - 150, 200, 150, roof_color=(130, 50, 40))
            draw_drozd(screen, WIDTH//2 - 40, HEIGHT//2 + 20)
            pygame.draw.rect(screen, (80, 50, 30), (WIDTH//2 + 20, HEIGHT//2 + 20, 20, 35))
            pygame.draw.circle(screen, (220, 180, 150), (WIDTH//2 + 30, HEIGHT//2 + 15), 10)

        pygame.draw.rect(screen, (15, 12, 10), (50, HEIGHT - 200, WIDTH-100, 160))
        pygame.draw.rect(screen, (100, 120, 90), (50, HEIGHT - 200, WIDTH-100, 160), 3)
        
        title_surf = font_title.render(intro_sequence[intro_step]["title"], True, (180, 200, 180))
        screen.blit(title_surf, (80, HEIGHT - 180))
        lines = intro_sequence[intro_step]["text"].split('\n')
        for idx, l in enumerate(lines):
            screen.blit(font_main.render(l, True, (240, 240, 220)), (80, HEIGHT - 130 + idx*30))

    # MAPA ŚWIATA (EKSPLORACJA / KOŚCI)
    elif current_state in [STATE_EXPLORE, STATE_DICE_ROLL]:
        screen.blit(terrain_surface, (0, 0))
        
        # Rysowanie dekoracji mapy
        for tx, ty in decorations_trees: draw_tree(screen, tx, ty)
        draw_well(screen, int(well_pos.x), int(well_pos.y))
        
        for h in houses:
            draw_slavic_house(screen, h.rect.x, h.rect.y, h.rect.width, h.rect.height, h.roof_color, h.ruined)
            
        # Potwory ujawniają się dopiero po śledztwie
        for m in monster_triggers:
            if not m["beaten"]:
                if investigation_complete:
                    if m["type"] == BOSS_LATARNIK: draw_monster_latarnik(screen, m["rect"].x, m["rect"].y, anim_tick)
                    elif m["type"] == BOSS_PIEN: draw_monster_pien(screen, m["rect"].x, m["rect"].y)
                    elif m["type"] == BOSS_MAMUNA: draw_monster_mamuna(screen, m["rect"].x, m["rect"].y, anim_tick)
                    elif m["type"] == BOSS_KRZYKACZ: draw_monster_krzykacz(screen, m["rect"].x, m["rect"].y, anim_tick)
                else:
                    draw_monster_shadow(screen, m["rect"].x, m["rect"].y, anim_tick)

        draw_drozd(screen, int(player_pos.x) - 15, int(player_pos.y) - 20)
        
        # Interfejs śledztwa w rogu
        pygame.draw.rect(screen, (20, 20, 25), (10, 10, 310, 80))
        pygame.draw.rect(screen, (120, 100, 70), (10, 10, 310, 80), 2)
        txt_col = (100, 255, 100) if investigation_complete else (200, 180, 140)
        status_txt = "Koszmary nadeszły!" if investigation_complete else "Śledztwo: Zbierz dowody"
        screen.blit(font_sub.render(status_txt, True, txt_col), (20, 15))
        screen.blit(font_sub.render(f"1. Zeznanie Sołtysa: {'[OK]' if clues_found['soltys'] else '[ ]'}", True, (200, 200, 200)), (20, 35))
        screen.blit(font_sub.render(f"2. Prawda Zielarki: {'[OK]' if clues_found['zielarka'] else '[ ]'}", True, (200, 200, 200)), (20, 50))
        screen.blit(font_sub.render(f"3. Piec w ruinach: {'[OK]' if clues_found['ruiny'] else '[ ]'}", True, (200, 200, 200)), (170, 35))

        if current_state == STATE_DICE_ROLL:
            pygame.draw.rect(screen, (10, 10, 15), (150, 180, WIDTH-300, 350))
            pygame.draw.rect(screen, (220, 50, 50), (150, 180, WIDTH-300, 350), 3)
            title = font_main.render(f"ZASADZKA BESTII: {active_boss_type}", True, (255, 50, 50))
            screen.blit(title, (WIDTH//2 - title.get_width()//2, 210))
            p_str = f"Modyfikatory Walki: Atak ({mod_attack:+d}), Wytrzymałość ({mod_stamina:+d})"
            m_str = f"Modyfikatory Wroga: Atak ({boss_mod_attack:+d}), Wytrzymałość ({boss_mod_stamina:+d})"
            screen.blit(font_main.render(p_str, True, (100, 255, 100)), (200, 290))
            screen.blit(font_main.render(m_str, True, (255, 100, 100)), (200, 350))
            prompt = font_main.render("NACIŚNIJ [ENTER], ABY PODJĄĆ WALKĘ", True, (255, 255, 255))
            screen.blit(prompt, (WIDTH//2 - prompt.get_width()//2, 450))

    # WNĘTRZA BUDYNKÓW / INTERAKCJA
    elif current_state in [STATE_HOUSE, STATE_DIALOGUE]:
        screen.fill((25, 20, 15)) 
        pygame.draw.rect(screen, (45, 35, 25), (50, 50, WIDTH-100, HEIGHT-100), 8) 
        
        # Wnętrze (w zależności od ruin)
        if active_house.ruined:
            pygame.draw.rect(screen, (30, 25, 25), (WIDTH//2 - 50, HEIGHT//2 - 40, 100, 80)) # Piec chlebowy
            pygame.draw.circle(screen, (10, 10, 10), (WIDTH//2, HEIGHT//2), 30) # Czeluść pieca
        else:
            pygame.draw.rect(screen, (70, 50, 35), (WIDTH//2 - 40, HEIGHT//2 - 20, 80, 50))
            pygame.draw.circle(screen, (200, 150, 120), (WIDTH//2, HEIGHT//2 - 60), 10)
        
        draw_drozd(screen, int(player_pos.x) - 15, int(player_pos.y) - 20)
        
        if current_state == STATE_HOUSE:
            lbl = font_sub.render("Podejdź bliżej centrum, aby zbadać/rozmawiać. Wyjdź poza ramę okna, aby wyjść.", True, (150, 150, 150))
            screen.blit(lbl, (70, HEIGHT - 40))
            
        elif current_state == STATE_DIALOGUE:
            pygame.draw.rect(screen, (15, 12, 10), (50, 450, WIDTH-100, 220))
            pygame.draw.rect(screen, (140, 110, 80) if not active_house.ruined else (100, 50, 50), (50, 450, WIDTH-100, 220), 4)
            screen.blit(font_main.render(dialogue_title, True, (255, 215, 0)), (80, 465))
            lines = dialogue_lines[0].split('\n')
            for idx, l in enumerate(lines):
                screen.blit(font_sub.render(l, True, (230, 220, 210)), (80, 500 + idx*22))
            for idx, choice in enumerate(dialogue_choices):
                color = (255, 255, 100) if idx == current_choice_idx else (140, 140, 140)
                prefix = " > " if idx == current_choice_idx else "   "
                screen.blit(font_sub.render(prefix + choice[0], True, color), (80, 580 + idx * 25))

    # ARENA MINIGIER WALKI
    elif current_state == STATE_COMBAT:
        screen.fill((10, 12, 18))
        pygame.draw.rect(screen, (150, 30, 30), (80, 100, WIDTH-160, HEIGHT-160), 3) 
        pygame.draw.rect(screen, (40, 40, 40), (80, 30, 250, 20))
        pygame.draw.rect(screen, (200, 30, 30), (80, 30, int(250 * (player_hp/player_max_hp)), 20))
        screen.blit(font_sub.render(f"Drozd HP: {player_hp}/{player_max_hp}", True, (255,255,255)), (85, 32))
        pygame.draw.rect(screen, (40, 40, 40), (WIDTH - 330, 30, 250, 20))
        pygame.draw.rect(screen, (160, 30, 160), (WIDTH - 330, 30, int(250 * max(0, boss_hp/boss_max_hp)), 20))
        screen.blit(font_sub.render(f"{active_boss_type} HP: {int(boss_hp)}", True, (255,255,255)), (WIDTH - 325, 32))

        bx, by = WIDTH // 2 - 15, 200
        if active_boss_type == BOSS_LATARNIK: draw_monster_latarnik(screen, bx, by, anim_tick)
        elif active_boss_type == BOSS_PIEN: draw_monster_pien(screen, bx, by)
        elif active_boss_type == BOSS_MAMUNA: draw_monster_mamuna(screen, bx, by, anim_tick)
        elif active_boss_type == BOSS_KRZYKACZ: draw_monster_krzykacz(screen, bx, by, anim_tick)

        for p in combat_projectiles: p.draw(screen)
        for b in combat_bullets: b.draw(screen)
        draw_drozd(screen, int(player_combat_pos.x) - 15, int(player_combat_pos.y) - 20)

    # KONIEC GRY
    elif current_state == STATE_END:
        screen.fill((15, 10, 10))
        title_surf = font_main.render("ZAKOŃCZENIE ŚLEDZTWA", True, (200, 50, 50))
        screen.blit(title_surf, (WIDTH//2 - title_surf.get_width()//2, HEIGHT//2 - 60))
        msg_surf = font_sub.render(end_message, True, (220, 220, 200))
        screen.blit(msg_surf, (WIDTH//2 - msg_surf.get_width()//2, HEIGHT//2))

    pygame.display.flip()

pygame.quit()
sys.exit()
