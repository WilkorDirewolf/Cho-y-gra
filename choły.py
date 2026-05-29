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
pygame.display.set_caption("Krzykacz: Umysł Marii - Thriller Psychologiczny")
clock = pygame.time.Clock()

# --- STANY GRY ---
STATE_INTRO = "INTRO"
STATE_EXPLORE = "EXPLORE"
STATE_HOUSE = "HOUSE"
STATE_DIALOGUE = "DIALOGUE"
STATE_TRANSITION = "TRANSITION"
STATE_DICE_ROLL = "DICE_ROLL"
STATE_COMBAT = "COMBAT"
STATE_END = "END" 

current_map = "VILLAGE" # "VILLAGE" lub "HOSPITAL"
end_message = ""

# --- TYPY WALKI ---
BOSS_MAMUNA = "MAMUNA (Winna Odmieńca)"
BOSS_LATARNIK = "LATARNIK (Cień Macieja)"
BOSS_PIEN = "PIEN (Trauma Pożaru)"
BOSS_KRZYKACZ = "KRZYKACZ (Szaleństwo)"

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
        if width > 130: # Dla plebanii dodajemy okno
            pygame.draw.rect(surface, (220, 140, 30), (x + 20, y + 45, 25, 25))
            pygame.draw.rect(surface, (30, 20, 10), (x + 20, y + 45, 25, 25), 2)
        pygame.draw.polygon(surface, roof_color, [(x - 10, y + 30), (x + width // 2, y - 10), (x + width + 10, y + 30)])
    else:
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
    radius = int(15 + math.sin(anim_tick * 0.1) * 4)
    alpha_surf = pygame.Surface((60, 60), pygame.SRCALPHA)
    pygame.draw.circle(alpha_surf, (80, 20, 90, 80), (30, 30), radius)
    surface.blit(alpha_surf, (x - 10, y - 5))

def draw_monster_latarnik(surface, x, y, anim_tick):
    offset_y = int(math.sin(anim_tick * 0.1) * 5)
    pygame.draw.polygon(surface, (50, 50, 50), [(x, y+20+offset_y), (x+15, y-5+offset_y), (x+30, y+20+offset_y), (x+25, y+45+offset_y), (x+5, y+45+offset_y)])
    pygame.draw.circle(surface, (210, 210, 190), (x + 15, y + offset_y), 8)
    pygame.draw.circle(surface, (150, 0, 0), (x + 12, y - 1 + offset_y), 2)
    pygame.draw.circle(surface, (150, 0, 0), (x + 18, y - 1 + offset_y), 2)

def draw_monster_pien(surface, x, y):
    pygame.draw.rect(surface, (55, 45, 40), (x, y, 40, 50))
    pygame.draw.line(surface, (180, 20, 20), (x + 10, y + 15), (x + 30, y + 25), 3)
    pygame.draw.circle(surface, (255, 255, 255), (x + 20, y + 20), 3)

def draw_monster_mamuna(surface, x, y, anim_tick):
    offset_x = int(math.sin(anim_tick * 0.08) * 3)
    pygame.draw.ellipse(surface, (20, 45, 25), (x - 5 + offset_x, y + 5, 40, 40))
    pygame.draw.circle(surface, (140, 155, 120), (x + 15 + offset_x, y), 9)

def draw_monster_krzykacz(surface, x, y, anim_tick):
    scale = 1.0 + math.sin(anim_tick * 0.2) * 0.08
    w, h = int(35 * scale), int(45 * scale)
    pygame.draw.ellipse(surface, (70, 40, 85), (x - w//2 + 15, y - h//2 + 20, w, h))
    pygame.draw.circle(surface, (10, 5, 15), (x + 15, y + 22), int(8 * scale))

class Projectile:
    def __init__(self, x, y, vx, vy, color, radius=5):
        self.x, self.y, self.vx, self.vy, self.color, self.radius = x, y, vx, vy, color, radius
    def update(self):
        self.x += self.vx
        self.y += self.vy
    def draw(self, surface):
        pygame.draw.circle(surface, self.color, (int(self.x), int(self.y)), self.radius)

class House:
    def __init__(self, x, y, w, h, name, dialog_func, roof_color=(110, 90, 60), ruined=False):
        self.rect = pygame.Rect(x, y, w, h)
        self.door_rect = pygame.Rect(x + w//2 - 15, y + h - 15, 30, 20)
        self.name = name
        self.dialog_func = dialog_func
        self.roof_color = roof_color
        self.ruined = ruined

# --- DANE FABULARNE ---
clues_found = {"soltys": False, "zielarka": False, "ruiny": False}

def get_soltys_dialogue():
    return ("Sołtys Bieniasz: Wilki zjadły małego? Taa, tak najwygodniej mówić gminie.\nIdź pogadaj z tą starą wiedźmą, Zielarką, albo zbadaj zgliszcza chaty Marii na wschodzie.\nNikt tam od pożaru nie zaglądał.", 
            [("Zbadam ten ślad (Zapisz wskazówkę Sołtysa)", "CLUE_SOLTYS")])

def get_zielarka_dialogue():
    return ("Zielarka: Wilki? Bzdura! Tam wydarzyła się czysta, ludzka i nieludzka tragedia.\nSpalona chata Marii kryje w sobie prawdę gorszą niż dzikie zwierzęta.\nSprawdź piec...", 
            [("Zanotuj słowa Zielarki (Zapisz wskazówkę)", "CLUE_ZIELARKA")])

def get_ruiny_dialogue():
    return ("Osmalone ściany potęgują odór dawnego pożaru. W zrujnowanym piecu chlebowym,\npośród popiołu, widzisz drobne, zwęglone kości...\nIch budowa jest niepokojąca. Kształt czaszki... To nie było ludzkie niemowlę.", 
            [("Zabezpiecz dowód z pieca (Zapisz dowód)", "CLUE_RUINY")])

def get_ksiadz_dialogue():
    if clues_found["soltys"] and clues_found["zielarka"] and clues_found["ruiny"]:
        return ("Ksiądz Proboszcz: Widzę, że odkryłeś prawdę, panie Drozd.\nMaria i Maciej czekali na dziecko. Byli szczęśliwi. Ale tamtej nocy głupi Maciej\notworzył okno w pokoju dziecka, żeby zapalić. Wtedy weszła Mamuna...\nPodmieniła ich syna na odmieńca. Gdy Maria rano zobaczyła potworka, oszalała.\nSpaliła go w piecu, a z nim całą chatę. Zawieźli ją do zakładu w Choroszczy.", 
                [("Jestem psychologiem klinicznym. Muszę z nią pomówić. (Jedź do Choroszczy)", "GO_TO_CHOROSZCZ")])
    else:
        return ("Ksiądz Proboszcz: Szczęść Boże, przybyszu.\nWioska skrywa mrok, ale musisz najpierw zbadać zgliszcza i wypytać mieszkańców,\nzanim wyjawię ci całą, bolesną prawdę.", 
                [("Wrócę, gdy dowiem się więcej.", "LEAVE")])

def get_bed_dialogue():
    return ("To twoje posłanie w starej chacie po Mikołaju.\nChcesz odpocząć?", [("Prześpij się (Regeneracja HP)", "SLEEP"), ("Wyjdź", "LEAVE")])

houses = [
    House(250, 60, 160, 110, "Dom Sołtysa Bieniasza", get_soltys_dialogue),
    House(140, 320, 130, 90, "Chata po starym Mikołaju", get_bed_dialogue),
    House(780, 80, 140, 100, "Namiot Starej Zielarki", get_zielarka_dialogue),
    House(720, 320, 150, 110, "Spalona Chata Marii", get_ruiny_dialogue, ruined=True),
    House(60, 480, 150, 130, "Plebania", get_ksiadz_dialogue, roof_color=(120, 40, 30))
]

decorations_trees = [(40, 260), (50, 500), (420, 110), (360, 180), (460, 240), (280, 550), (660, 120), (690, 200), (880, 500), (900, 250)]
well_pos = pygame.Vector2(490, 420)
village_shadows = [(450, 560), (820, 120), (750, 550), (70, 560)]

monster_triggers_hospital = [
    {"rect": pygame.Rect(WIDTH//2 - 250, HEIGHT//2 - 200, 60, 60), "type": BOSS_LATARNIK, "beaten": False},
    {"rect": pygame.Rect(WIDTH//2 + 190, HEIGHT//2 - 200, 60, 60), "type": BOSS_PIEN, "beaten": False},
    {"rect": pygame.Rect(WIDTH//2 - 250, HEIGHT//2 + 150, 60, 60), "type": BOSS_MAMUNA, "beaten": False},
    {"rect": pygame.Rect(WIDTH//2 + 190, HEIGHT//2 + 150, 60, 60), "type": BOSS_KRZYKACZ, "beaten": False}
]

# Zmienne ogólne
current_state = STATE_INTRO
anim_tick = 0
active_house = None 
player_pos = pygame.Vector2(215, 410) 
player_hp, player_max_hp = 100, 100
base_attack, mod_attack, mod_stamina = 10, 0, 0

active_boss_type = None
boss_hp, boss_max_hp = 100, 100
boss_mod_attack, boss_mod_stamina = 0, 0

dialogue_title, dialogue_lines, dialogue_choices = "", [], []
current_choice_idx = 0

combat_projectiles, combat_bullets = [], []
combat_timer = 0
player_combat_pos = pygame.Vector2(WIDTH//2, HEIGHT//2 + 100)

font_main = pygame.font.SysFont("georgia", 20)
font_sub = pygame.font.SysFont("arial", 15)
font_title = pygame.font.SysFont("georgia", 24, bold=True)

intro_step = 0
intro_sequence = [
    {"title": "Wnętrze Żuka. Czuć benzynę.", "text": "Kierowca Władek: Mówię ci, panie Drozd. W Chołach to się porobiło niezłe bagno.\nDzieciaka w lesie znaleźli... rozszarpanego. Oficjalnie ponoć wilki."},
    {"title": "Droga błotnista, pełna cieni.", "text": "Władek: Ale baby we wsi swoje wiedzą. Coś tu śmierdzi kłamstwem.\nJako psycholog powinieneś pogadać z ludźmi. Tu każdy coś ukrywa.\nJa stąd spadam, tuż przed zmrokiem."}
]

transition_step = 0
transition_sequence = [
    {"title": "Trasa do Choroszczy...", "text": "Drozd odpala Żuka i odjeżdża z Chołów. Jako psycholog kliniczny wie,\nże prawdziwe potwory rzadko biegają fizycznie po lasach.\nCzasem gnieżdżą się głęboko w złamanym, ludzkim umyśle."},
    {"title": "Szpital Psychiatryczny", "text": "Sterylna, zamknięta sala w Choroszczy. Maria tkwi w katatonii.\nJej umysł to prawdziwe pole bitwy. Demony podążyły za nią,\nmaterializując się w jej pokoju. Czas wejść w jej koszmar i je zniszczyć."}
]

terrain_surface = pygame.Surface((WIDTH, HEIGHT))
for ty in range(0, HEIGHT, 50):
    for tx in range(0, WIDTH, 50):
        base_g = random.randint(25, 38)
        pygame.draw.rect(terrain_surface, (int(base_g*0.85), base_g, int(base_g*0.65)), (tx, ty, 50, 50))

# --- GŁÓWNA PĘTLA SYSTEMOWA ---
running = True
while running:
    anim_tick += 1
    dt = clock.tick(60)
    keys = pygame.key.get_pressed()

    # 1. LOGIKA RUCHU
    if current_state in [STATE_EXPLORE, STATE_HOUSE]:
        move_vector = pygame.Vector2(0, 0)
        if keys[pygame.K_w] or keys[pygame.K_UP]: move_vector.y -= 4
        if keys[pygame.K_s] or keys[pygame.K_DOWN]: move_vector.y += 4
        if keys[pygame.K_a] or keys[pygame.K_LEFT]: move_vector.x -= 4
        if keys[pygame.K_d] or keys[pygame.K_RIGHT]: move_vector.x += 4
        if move_vector.length() > 0: player_pos += move_vector.normalize() * 4

        if current_state == STATE_EXPLORE:
            player_pos.x = max(20, min(WIDTH-20, player_pos.x))
            player_pos.y = max(20, min(HEIGHT-20, player_pos.y))
            
            if current_map == "VILLAGE":
                for h in houses:
                    if h.door_rect.collidepoint(player_pos.x, player_pos.y):
                        current_state = STATE_HOUSE
                        active_house = h
                        player_pos = pygame.Vector2(WIDTH // 2, HEIGHT - 130)
                        break
            
            elif current_map == "HOSPITAL":
                for m in monster_triggers_hospital:
                    if not m["beaten"] and m["rect"].collidepoint(player_pos.x, player_pos.y):
                        active_boss_type = m["type"]
                        current_state = STATE_DICE_ROLL
                        p_d1, p_d2, m_d1, m_d2 = random.randint(1,6), random.randint(1,6), random.randint(1,6), random.randint(1,6)
                        mod_attack, mod_stamina = (p_d1 + p_d2) - 6, (p_d1 + p_d2) // 2
                        boss_mod_attack, boss_mod_stamina = (m_d1 + m_d2) - 6, (m_d1 + m_d2) // 2
                        boss_hp = boss_max_hp = 100 + (boss_mod_stamina * 5)
                        break
                
                if all(m["beaten"] for m in monster_triggers_hospital):
                    end_message = "Jako psycholog i tropiciel, Drozd oczyścił umysł Marii z koszmaru Chołów."
                    current_state = STATE_END

        elif current_state == STATE_HOUSE:
            dist = pygame.Vector2(player_pos.x, player_pos.y).distance_to(pygame.Vector2(WIDTH//2, HEIGHT//2))
            if dist < 60:
                current_state = STATE_DIALOGUE
                dialogue_title = active_house.name
                t, c = active_house.dialog_func()
                dialogue_lines, dialogue_choices = [t], c
                current_choice_idx = 0
            
            if player_pos.x < 50 or player_pos.x > WIDTH - 50 or player_pos.y < 50 or player_pos.y > HEIGHT - 50:
                current_state = STATE_EXPLORE
                player_pos = pygame.Vector2(active_house.door_rect.centerx, active_house.door_rect.bottom + 20)
                active_house = None

    # WALKA
    elif current_state == STATE_COMBAT:
        combat_timer += 1
        c_speed = 5
        if keys[pygame.K_w] or keys[pygame.K_UP]: player_combat_pos.y -= c_speed
        if keys[pygame.K_s] or keys[pygame.K_DOWN]: player_combat_pos.y += c_speed
        if keys[pygame.K_a] or keys[pygame.K_LEFT]: player_combat_pos.x -= c_speed
        if keys[pygame.K_d] or keys[pygame.K_RIGHT]: player_combat_pos.x += c_speed
        player_combat_pos.x = max(100, min(WIDTH-100, player_combat_pos.x))
        player_combat_pos.y = max(150, min(HEIGHT-50, player_combat_pos.y))
        
        # Proste zasady uszkodzeń dla wszystkich bossów dla zwięzłości
        if combat_timer % 40 == 0:
            dx, dy = player_combat_pos.x - (WIDTH//2), player_combat_pos.y - 220
            dist = math.hypot(dx, dy) if math.hypot(dx, dy) != 0 else 1
            combat_projectiles.append(Projectile(WIDTH//2, 220, (dx/dist)*6, (dy/dist)*6, (255, 60, 0), 8))
        if combat_timer % 60 == 0: boss_hp -= (base_attack + mod_attack)
        if keys[pygame.K_SPACE] and combat_timer % 15 == 0:
            combat_bullets.append(Projectile(player_combat_pos.x, player_combat_pos.y, 0, -8, (255, 255, 255), 4))

        for b in combat_bullets:
            b.update()
            if pygame.Vector2(b.x, b.y).distance_to(pygame.Vector2(WIDTH//2, 220)) < 30:
                boss_hp -= (base_attack + mod_attack + 2)
                combat_bullets.remove(b)
            elif b.y < 100: combat_bullets.remove(b)

        for p in combat_projectiles:
            p.update()
            if pygame.Vector2(p.x, p.y).distance_to(player_combat_pos) < 20:
                player_hp -= max(1, 6 + boss_mod_attack)
                combat_projectiles.remove(p)
            elif p.x < 0 or p.x > WIDTH or p.y < 0 or p.y > HEIGHT: combat_projectiles.remove(p)

        if boss_hp <= 0:
            for m in monster_triggers_hospital:
                if m["type"] == active_boss_type: m["beaten"] = True
            current_state = STATE_EXPLORE
            combat_projectiles.clear()
            combat_bullets.clear()
        elif player_hp <= 0:
            end_message = "Umysł Drozda uległ psychozie Marii."
            current_state = STATE_END

    # 2. EVENTY
    for event in pygame.event.get():
        if event.type == pygame.QUIT: running = False
        elif event.type == pygame.KEYDOWN:
            if current_state == STATE_INTRO:
                if event.key in [pygame.K_RETURN, pygame.K_SPACE]:
                    intro_step += 1
                    if intro_step >= len(intro_sequence): current_state = STATE_EXPLORE
            
            elif current_state == STATE_TRANSITION:
                if event.key in [pygame.K_RETURN, pygame.K_SPACE]:
                    transition_step += 1
                    if transition_step >= len(transition_sequence):
                        current_map = "HOSPITAL"
                        current_state = STATE_EXPLORE
                        player_pos = pygame.Vector2(WIDTH//2, HEIGHT - 100)

            elif current_state == STATE_DIALOGUE:
                if event.key in [pygame.K_w, pygame.K_UP]: current_choice_idx = (current_choice_idx - 1) % len(dialogue_choices)
                elif event.key in [pygame.K_s, pygame.K_DOWN]: current_choice_idx = (current_choice_idx + 1) % len(dialogue_choices)
                elif event.key in [pygame.K_RETURN, pygame.K_e]:
                    c_code = dialogue_choices[current_choice_idx][1]
                    if c_code == "CLUE_SOLTYS": clues_found["soltys"] = True
                    elif c_code == "CLUE_ZIELARKA": clues_found["zielarka"] = True
                    elif c_code == "CLUE_RUINY": clues_found["ruiny"] = True
                    elif c_code == "SLEEP": player_hp = player_max_hp
                    elif c_code == "GO_TO_CHOROSZCZ":
                        current_state = STATE_TRANSITION
                        continue
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

    # 3. RENDEROWANIE
    if current_state == STATE_INTRO:
        screen.fill((12, 15, 12))
        if intro_step < 1: draw_zuk(screen, WIDTH//2 - 100 + int(math.sin(anim_tick * 0.1) * 3), HEIGHT//2 - 60)
        else:
            draw_slavic_house(screen, WIDTH//2 - 100, HEIGHT//2 - 150, 200, 150, roof_color=(130, 50, 40))
            draw_drozd(screen, WIDTH//2 - 40, HEIGHT//2 + 20)
        title_surf = font_title.render(intro_sequence[intro_step]["title"], True, (180, 200, 180))
        screen.blit(title_surf, (80, HEIGHT - 180))
        for idx, l in enumerate(intro_sequence[intro_step]["text"].split('\n')):
            screen.blit(font_main.render(l, True, (240, 240, 220)), (80, HEIGHT - 130 + idx*30))
            
    elif current_state == STATE_TRANSITION:
        screen.fill((10, 12, 18))
        if transition_step == 0: draw_zuk(screen, WIDTH//2 - 100, HEIGHT//2 - 60)
        title_surf = font_title.render(transition_sequence[transition_step]["title"], True, (150, 180, 255))
        screen.blit(title_surf, (80, HEIGHT - 180))
        for idx, l in enumerate(transition_sequence[transition_step]["text"].split('\n')):
            screen.blit(font_main.render(l, True, (240, 240, 240)), (80, HEIGHT - 130 + idx*30))

    elif current_state in [STATE_EXPLORE, STATE_DICE_ROLL]:
        if current_map == "VILLAGE":
            screen.blit(terrain_surface, (0, 0))
            for tx, ty in decorations_trees: draw_tree(screen, tx, ty)
            draw_well(screen, int(well_pos.x), int(well_pos.y))
            for h in houses: draw_slavic_house(screen, h.rect.x, h.rect.y, h.rect.width, h.rect.height, h.roof_color, h.ruined)
            for sx, sy in village_shadows: draw_monster_shadow(screen, sx, sy, anim_tick)
            
            draw_drozd(screen, int(player_pos.x) - 15, int(player_pos.y) - 20)
            
            pygame.draw.rect(screen, (20, 20, 25), (10, 10, 310, 80))
            pygame.draw.rect(screen, (120, 100, 70), (10, 10, 310, 80), 2)
            screen.blit(font_sub.render("Śledztwo w Chołach", True, (200, 180, 140)), (20, 15))
            screen.blit(font_sub.render(f"1. Sołtys: {'[OK]' if clues_found['soltys'] else '[ ]'}", True, (200, 200, 200)), (20, 35))
            screen.blit(font_sub.render(f"2. Zielarka: {'[OK]' if clues_found['zielarka'] else '[ ]'}", True, (200, 200, 200)), (20, 50))
            screen.blit(font_sub.render(f"3. Ruiny: {'[OK]' if clues_found['ruiny'] else '[ ]'}", True, (200, 200, 200)), (170, 35))
            
        elif current_map == "HOSPITAL":
            screen.fill((180, 185, 190))
            for tx in range(0, WIDTH, 100): pygame.draw.line(screen, (160, 165, 170), (tx, 0), (tx, HEIGHT), 2)
            for ty in range(0, HEIGHT, 100): pygame.draw.line(screen, (160, 165, 170), (0, ty), (WIDTH, ty), 2)
            
            # Łóżko i Maria
            pygame.draw.rect(screen, (220, 220, 220), (WIDTH//2 - 30, HEIGHT//2 - 40, 60, 90), border_radius=5)
            pygame.draw.rect(screen, (255, 255, 255), (WIDTH//2 - 25, HEIGHT//2 - 35, 50, 25), border_radius=3)
            pygame.draw.circle(screen, (250, 220, 200), (WIDTH//2, HEIGHT//2 - 25), 10)
            pygame.draw.circle(screen, (60, 40, 30), (WIDTH//2, HEIGHT//2 - 25), 11, 3)
            
            for m in monster_triggers_hospital:
                if not m["beaten"]:
                    if m["type"] == BOSS_LATARNIK: draw_monster_latarnik(screen, m["rect"].x, m["rect"].y, anim_tick)
                    elif m["type"] == BOSS_PIEN: draw_monster_pien(screen, m["rect"].x, m["rect"].y)
                    elif m["type"] == BOSS_MAMUNA: draw_monster_mamuna(screen, m["rect"].x, m["rect"].y, anim_tick)
                    elif m["type"] == BOSS_KRZYKACZ: draw_monster_krzykacz(screen, m["rect"].x, m["rect"].y, anim_tick)
            
            draw_drozd(screen, int(player_pos.x) - 15, int(player_pos.y) - 20)
            
            pygame.draw.rect(screen, (20, 20, 25), (10, 10, 310, 50))
            pygame.draw.rect(screen, (120, 100, 70), (10, 10, 310, 50), 2)
            screen.blit(font_sub.render("Choroszcz: Zniszcz demony umysłu", True, (255, 100, 100)), (20, 20))

        if current_state == STATE_DICE_ROLL:
            pygame.draw.rect(screen, (10, 10, 15), (150, 180, WIDTH-300, 350))
            pygame.draw.rect(screen, (220, 50, 50), (150, 180, WIDTH-300, 350), 3)
            title = font_main.render(f"ZASADZKA BESTII: {active_boss_type}", True, (255, 50, 50))
            screen.blit(title, (WIDTH//2 - title.get_width()//2, 210))
            screen.blit(font_main.render(f"Atak ({mod_attack:+d}), Wytrz. ({mod_stamina:+d})", True, (100, 255, 100)), (200, 290))
            screen.blit(font_main.render("NACIŚNIJ [ENTER], ABY WALCZYĆ", True, (255, 255, 255)), (WIDTH//2 - 160, 450))

    elif current_state in [STATE_HOUSE, STATE_DIALOGUE]:
        screen.fill((25, 20, 15)) 
        pygame.draw.rect(screen, (45, 35, 25), (50, 50, WIDTH-100, HEIGHT-100), 8) 
        if active_house.ruined:
            pygame.draw.rect(screen, (30, 25, 25), (WIDTH//2 - 50, HEIGHT//2 - 40, 100, 80))
            pygame.draw.circle(screen, (10, 10, 10), (WIDTH//2, HEIGHT//2), 30)
        else:
            pygame.draw.rect(screen, (70, 50, 35), (WIDTH//2 - 40, HEIGHT//2 - 20, 80, 50))
            pygame.draw.circle(screen, (200, 150, 120), (WIDTH//2, HEIGHT//2 - 60), 10)
        draw_drozd(screen, int(player_pos.x) - 15, int(player_pos.y) - 20)
        
        if current_state == STATE_DIALOGUE:
            pygame.draw.rect(screen, (15, 12, 10), (50, 450, WIDTH-100, 220))
            pygame.draw.rect(screen, (140, 110, 80), (50, 450, WIDTH-100, 220), 4)
            screen.blit(font_main.render(dialogue_title, True, (255, 215, 0)), (80, 465))
            for idx, l in enumerate(dialogue_lines[0].split('\n')):
                screen.blit(font_sub.render(l, True, (230, 220, 210)), (80, 500 + idx*22))
            for idx, choice in enumerate(dialogue_choices):
                color = (255, 255, 100) if idx == current_choice_idx else (140, 140, 140)
                screen.blit(font_sub.render((" > " if idx == current_choice_idx else "   ") + choice[0], True, color), (80, 590 + idx * 25))

    elif current_state == STATE_COMBAT:
        screen.fill((10, 12, 18))
        pygame.draw.rect(screen, (150, 30, 30), (80, 100, WIDTH-160, HEIGHT-160), 3) 
        pygame.draw.rect(screen, (40, 40, 40), (80, 30, 250, 20))
        pygame.draw.rect(screen, (200, 30, 30), (80, 30, int(250 * (player_hp/player_max_hp)), 20))
        screen.blit(font_sub.render(f"Drozd HP: {player_hp}/{player_max_hp}", True, (255,255,255)), (85, 32))
        pygame.draw.rect(screen, (40, 40, 40), (WIDTH - 330, 30, 250, 20))
        pygame.draw.rect(screen, (160, 30, 160), (WIDTH - 330, 30, int(250 * max(0, boss_hp/boss_max_hp)), 20))
        
        bx, by = WIDTH // 2 - 15, 200
        if active_boss_type == BOSS_LATARNIK: draw_monster_latarnik(screen, bx, by, anim_tick)
        elif active_boss_type == BOSS_PIEN: draw_monster_pien(screen, bx, by)
        elif active_boss_type == BOSS_MAMUNA: draw_monster_mamuna(screen, bx, by, anim_tick)
        elif active_boss_type == BOSS_KRZYKACZ: draw_monster_krzykacz(screen, bx, by, anim_tick)

        for p in combat_projectiles: p.draw(screen)
        for b in combat_bullets: b.draw(screen)
        draw_drozd(screen, int(player_combat_pos.x) - 15, int(player_combat_pos.y) - 20)

    elif current_state == STATE_END:
        screen.fill((15, 10, 10))
        title_surf = font_main.render("ZAKOŃCZENIE ŚLEDZTWA", True, (200, 50, 50))
        screen.blit(title_surf, (WIDTH//2 - title_surf.get_width()//2, HEIGHT//2 - 60))
        msg_surf = font_sub.render(end_message, True, (220, 220, 200))
        screen.blit(msg_surf, (WIDTH//2 - msg_surf.get_width()//2, HEIGHT//2))

    pygame.display.flip()

pygame.quit()
sys.exit()
