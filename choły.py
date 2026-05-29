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
pygame.display.set_caption("Krzykacz: Polowanie na Mamunę - Mroczna Baśń")
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

current_map = "VILLAGE" # "VILLAGE", "FOREST", "STRANGE_PLACE"
end_message = ""

# --- TYPY WALKI ---
BOSS_MAMUNA = "MAMUNA (Pani Lasu)"
BOSS_LATARNIK = "LATARNIK (Zwodzący Cień)"
BOSS_PIEN = "PIEN (Zgniły Strażnik)"
BOSS_KRZYKACZ = "KRZYKACZ (Bestia Dźwięku)"
BOSS_TLUM = "TŁUM WIEŚNIAKÓW"

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

def draw_lusia(surface, x, y):
    pygame.draw.polygon(surface, (15, 10, 10), [(x - 10, y + 10), (x + 10, y + 10), (x + 15, y + 30), (x - 15, y + 30)])
    pygame.draw.rect(surface, (120, 30, 40), (x - 10, y + 14, 20, 26)) 
    pygame.draw.circle(surface, (230, 190, 170), (x, y + 10), 8) 
    pygame.draw.circle(surface, (255, 40, 40), (x - 3, y + 9), 2) 
    pygame.draw.circle(surface, (255, 40, 40), (x + 3, y + 9), 2) 

def draw_slavic_house(surface, x, y, width, height, roof_color=(110, 90, 60), ruined=False):
    base_color = (85, 55, 35) if not ruined else (40, 35, 35)
    line_color = (50, 30, 15) if not ruined else (20, 20, 20)
    pygame.draw.rect(surface, base_color, (x, y + 30, width, height - 30))
    for i in range(y + 35, y + height, 12):
        pygame.draw.line(surface, line_color, (x, i), (x + width, i), 2)
    pygame.draw.rect(surface, (40, 25, 10) if not ruined else (15, 15, 15), (x + width//2 - 15, y + height - 40, 30, 40))
    if not ruined:
        if width > 130: 
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
    pygame.draw.rect(surface, (30, 20, 15), (x + 12, y + 24, 8, 16))
    pygame.draw.circle(surface, (15, 35, 15), (x + 16, y + 16), 18)
    pygame.draw.circle(surface, (20, 45, 20), (x + 12, y + 6), 14)

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
    pygame.draw.polygon(surface, (30, 40, 50), [(x, y+20+offset_y), (x+15, y-5+offset_y), (x+30, y+20+offset_y), (x+25, y+45+offset_y), (x+5, y+45+offset_y)])
    pygame.draw.circle(surface, (210, 210, 190), (x + 15, y + offset_y), 8)
    pygame.draw.circle(surface, (150, 0, 0), (x + 12, y - 1 + offset_y), 2)
    pygame.draw.circle(surface, (150, 0, 0), (x + 18, y - 1 + offset_y), 2)

def draw_monster_pien(surface, x, y):
    pygame.draw.rect(surface, (45, 35, 30), (x, y, 40, 50))
    pygame.draw.line(surface, (180, 20, 20), (x + 10, y + 15), (x + 30, y + 25), 3)
    pygame.draw.circle(surface, (180, 255, 100), (x + 20, y + 20), 3)

def draw_monster_mamuna(surface, x, y, anim_tick):
    offset_x = int(math.sin(anim_tick * 0.08) * 3)
    pygame.draw.ellipse(surface, (20, 45, 25), (x - 5 + offset_x, y + 5, 40, 40))
    pygame.draw.circle(surface, (100, 120, 80), (x + 15 + offset_x, y), 9)
    pygame.draw.circle(surface, (255, 0, 0), (x + 15 + offset_x, y), 3)

def draw_monster_krzykacz(surface, x, y, anim_tick):
    scale = 1.0 + math.sin(anim_tick * 0.2) * 0.08
    w, h = int(35 * scale), int(45 * scale)
    pygame.draw.ellipse(surface, (70, 40, 85), (x - w//2 + 15, y - h//2 + 20, w, h))
    pygame.draw.circle(surface, (10, 5, 15), (x + 15, y + 22), int(8 * scale))

def draw_mob(surface, x, y, anim_tick):
    for i in range(3):
        offset_y = int(math.sin(anim_tick * 0.1 + i) * 5)
        px, py = x - 30 + i*35, y + offset_y
        pygame.draw.rect(surface, (70, 40, 30), (px, py, 20, 30))
        pygame.draw.circle(surface, (200, 150, 120), (px + 10, py - 5), 8)
        pygame.draw.line(surface, (60, 30, 10), (px + 15, py + 10), (px + 25, py - 10), 3)
        pygame.draw.circle(surface, (255, 100, 0), (px + 25, py - 12), 5)

def draw_lesny_dziadek(surface, x, y):
    pygame.draw.rect(surface, (30, 50, 30), (x - 15, y - 40, 30, 80)) 
    pygame.draw.polygon(surface, (40, 70, 40), [(x-20, y+20), (x+20, y+20), (x, y-50)])
    pygame.draw.polygon(surface, (50, 80, 30), [(x-10, y-10), (x+10, y-10), (x, y+30)])
    pygame.draw.circle(surface, (200, 200, 50), (x - 6, y - 20), 3)
    pygame.draw.circle(surface, (200, 200, 50), (x + 6, y - 20), 3)
    pygame.draw.line(surface, (60, 40, 20), (x + 25, y - 30), (x + 25, y + 40), 4)

def draw_wielkie_drzewo(surface, x, y):
    pygame.draw.rect(surface, (45, 30, 20), (x, y, 120, 200), border_radius=10)
    pygame.draw.ellipse(surface, (20, 40, 25), (x - 80, y - 100, 280, 150))
    pygame.draw.ellipse(surface, (15, 30, 20), (x - 40, y - 120, 200, 130))
    pygame.draw.ellipse(surface, (30, 20, 15), (x + 30, y + 50, 20, 10)) 
    pygame.draw.ellipse(surface, (30, 20, 15), (x + 70, y + 50, 20, 10)) 
    pygame.draw.polygon(surface, (30, 20, 15), [(x + 60, y + 65), (x + 50, y + 90), (x + 70, y + 90)]) 
    pygame.draw.ellipse(surface, (25, 15, 10), (x + 40, y + 110, 40, 15)) 

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
clues_found = {
    "znaleziono_totem": False, 
    "zaufanie_soltysa": False, 
    "zaufanie_zielarki": False, 
    "dowod_kosci": False,
    "rozmowa_maria": False,
    "mamuna_rozmowa": False,
    "z_lusia": False,
    "spotkal_dziadka": False
}

def get_kapliczka_dialogue():
    if clues_found["znaleziono_totem"]: return ("Stara kapliczka. Nic tu więcej nie znajdziesz.", [("Odejdź", "LEAVE")])
    return ("Zaglądasz za starą kapliczkę. Wśród liści leży nadpalona, drewniana figurka...\nNależy do kogoś, komu spłonął dom.", 
            [("Zabierz nadpalony talizman", "CLUE_TOTEM"), ("Zostaw to", "LEAVE")])

def get_soltys_dialogue():
    if clues_found["zaufanie_soltysa"]: return ("Sołtys: Idź do Zielarki. Powiedz, że ja cię przysłałem.", [("Odejdź", "LEAVE")])
    if clues_found["znaleziono_totem"]:
        return ("Sołtys: Skąd masz ten talizman?! Dobra, to nie były wilki...\nAle darmowej wiedzy tu nie ma. Zapłać mi za fatygę.", 
                [("Przekup Sołtysa (5 zł)", "PAY_SOLTYS"), ("Zostaw go", "LEAVE")])
    return ("Sołtys: Czego tu szukasz? Wilki zjadły małego, to wielka tragedia.\nNie wtykaj nosa w nieswoje sprawy.", [("Wrócę później.", "LEAVE")])

def get_zielarka_dialogue():
    if clues_found["zaufanie_zielarki"]: return ("Zielarka: Przeszukaj piec w spalonej chacie.", [("Odejdź", "LEAVE")])
    if clues_found["zaufanie_soltysa"]:
        return ("Zielarka: Bieniasz cię przysłał? Złóż ofiarę, a wskażę ci, czego szukać w ruinach.", 
                [("Zapłać za wskazówkę (5 zł)", "PAY_ZIELARKA"), ("Odejdź", "LEAVE")])
    return ("Zielarka: Udowodnij najpierw, że tutejsi chcą z tobą gadać.\nBez błogosławieństwa Sołtysa nic ci nie powiem.", [("Wyjdź z namiotu", "LEAVE")])

def get_ruiny_dialogue():
    if clues_found["zaufanie_zielarki"] and not clues_found["dowod_kosci"]:
        return ("Rozgarniasz popiół w piecu. Znajdujesz drobne, zwęglone kości...\nIch budowa jest nienaturalna. Ktokolwiek tu spłonął, nie był człowiekiem.", 
                [("Zabezpiecz dowód (Kości odmieńca)", "CLUE_KOSCI")])
    elif clues_found["dowod_kosci"]: return ("Masz już dowód. Czas porozmawiać z księdzem.", [("Odejdź", "LEAVE")])
    return ("Osmalone ściany potęgują odór dawnego pożaru. Musisz kogoś wypytać, czego tu szukać.", [("Odejdź", "LEAVE")])

def get_ksiadz_dialogue():
    if clues_found["rozmowa_maria"]:
        return ("Maria (trzęsąc się): Mamuna uciekła do Głębokiego Lasu...\nZabrała moje prawdziwe dziecko! Błagam cię, Drozd, pomścij mnie.", 
                [("Wyrusz z bronią do Głębokiego Lasu", "GO_TO_FOREST"), ("Daj mi chwilę", "LEAVE")])
    if clues_found["dowod_kosci"]:
        return ("Ksiądz: Znalazłeś kości odmieńca. Więc to prawda... Maria wcale nie oszalała.\nUkryłem ją u siebie. Porozmawiaj z nią.", [("Porozmawiaj z Marią", "TALK_MARIA")])
    return ("Ksiądz: Szczęść Boże. Wioska skrywa mrok. Zdobądź ich zaufanie, wtedy porozmawiamy.", [("Wyjdź", "LEAVE")])

def get_bed_dialogue():
    return ("Twoje posłanie w starej chacie po Mikołaju. Odpocznij przed trudami śledztwa.", 
            [("Prześpij się (Regeneracja HP)", "SLEEP"), ("Wyjdź", "LEAVE")])

houses = [
    House(250, 60, 160, 110, "Dom Sołtysa Bieniasza", get_soltys_dialogue),
    House(140, 320, 130, 90, "Chata po starym Mikołaju", get_bed_dialogue),
    House(780, 80, 140, 100, "Namiot Starej Zielarki", get_zielarka_dialogue),
    House(720, 320, 150, 110, "Spalona Chata Marii", get_ruiny_dialogue, ruined=True),
    House(60, 480, 150, 130, "Plebania", get_ksiadz_dialogue, roof_color=(120, 40, 30)),
    House(420, 240, 80, 100, "Stara Kapliczka", get_kapliczka_dialogue, roof_color=(80, 80, 90))
]

decorations_trees = [(40, 260), (50, 500), (360, 180), (280, 550), (660, 120), (690, 200), (880, 500), (900, 250)]
well_pos = pygame.Vector2(490, 420)
village_shadows = [(450, 560), (820, 120), (750, 550), (70, 560)]
forest_trees = [(random.randint(-10, WIDTH-20), random.randint(-10, HEIGHT-20)) for _ in range(80)]

monster_triggers_forest = [
    {"rect": pygame.Rect(WIDTH//2 - 250, HEIGHT//2 - 200, 60, 60), "type": BOSS_LATARNIK, "beaten": False},
    {"rect": pygame.Rect(WIDTH//2 + 190, HEIGHT//2 - 200, 60, 60), "type": BOSS_PIEN, "beaten": False},
    {"rect": pygame.Rect(WIDTH//2 - 250, HEIGHT//2 + 150, 60, 60), "type": BOSS_KRZYKACZ, "beaten": False},
    {"rect": pygame.Rect(WIDTH//2 + 190, HEIGHT//2 + 150, 60, 60), "type": BOSS_MAMUNA, "beaten": False}
]

# Zmienne ogólne
current_state = STATE_INTRO
anim_tick = 0
active_house = None 
player_pos = pygame.Vector2(215, 410) 
player_hp, player_max_hp = 100, 100
player_money = 10 
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

intro_sequence = [
    {"title": "Wnętrze Żuka. Czuć benzynę.", "text": "Kierowca Władek: Mówię ci, panie Drozd. W Chołach to się porobiło niezłe bagno.\nDzieciaka w lesie znaleźli... rozszarpanego. Oficjalnie ponoć wilki."},
    {"title": "Droga błotnista, pełna cieni.", "text": "Władek: Ale baby we wsi swoje wiedzą. Coś tu śmierdzi kłamstwem.\nJako psycholog powinieneś pogadać z ludźmi. Zmusić ich do gadania."}
]
intro_step = 0

transition_sequence = [
    {"title": "Na skraju lasu...", "text": "Drozd zostawia wieś za plecami i z bronią w ręku wkracza w gęstwinę.\nJako psycholog zawsze szukał racjonalnego wytłumaczenia, ale..."},
    {"title": "Głęboki Las (Leże Mamuny)", "text": "To, co czai się w głębi kniei, nie jest tylko zrodzone z obłędu.\nCzas wyciągnąć broń i na własne oczy ujrzeć legendę..."}
]
transition_step = 0

terrain_surface = pygame.Surface((WIDTH, HEIGHT))
for ty in range(0, HEIGHT, 50):
    for tx in range(0, WIDTH, 50):
        base_g = random.randint(25, 38)
        pygame.draw.rect(terrain_surface, (int(base_g*0.85), base_g, int(base_g*0.65)), (tx, ty, 50, 50))

# --- GŁÓWNA PĘTLA ---
running = True
while running:
    anim_tick += 1
    clock.tick(60)
    keys = pygame.key.get_pressed()

    # 1. RUCH
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
            
            elif current_map == "FOREST":
                for m in monster_triggers_forest:
                    if not m["beaten"] and m["rect"].collidepoint(player_pos.x, player_pos.y):
                        active_boss_type = m["type"]
                        if active_boss_type == BOSS_MAMUNA and not clues_found["mamuna_rozmowa"]:
                            current_state = STATE_DIALOGUE
                            dialogue_title = "Leże Mamuny - Konfrontacja"
                            dialogue_lines = [
                                "Mamuna z czułością gładzi owinięte w szmaty ludzkie niemowlę...",
                                "Mamuna: Stój, łowco! Ta samica wcale go nie chciała, spaliła moje rodzone w piecu!",
                                "Zostaw nas w spokoju i pozwól mi je odchować, a las nigdy więcej was nie skrzywdzi."
                            ]
                            dialogue_choices = [
                                ("Oddaj dziecko i giń z moich rąk!", "FIGHT_MAMUNA"),
                                ("Opuść broń. (Zostaw dziecko Mamunie)", "SPARE_MAMUNA")
                            ]
                            current_choice_idx = 0
                            clues_found["mamuna_rozmowa"] = True
                            player_pos.y += 20 
                            break
                        else:
                            current_state = STATE_DICE_ROLL
                            p_d1, p_d2 = random.randint(1,6), random.randint(1,6)
                            m_d1, m_d2 = random.randint(1,6), random.randint(1,6)
                            mod_attack, mod_stamina = (p_d1 + p_d2) - 6, (p_d1 + p_d2) // 2
                            boss_mod_attack, boss_mod_stamina = (m_d1 + m_d2) - 6, (m_d1 + m_d2) // 2
                            boss_hp = boss_max_hp = 100 + (boss_mod_stamina * 5)
                            break
            
            elif current_map == "STRANGE_PLACE":
                # Interakcja z Drzewem w nieznanym wymiarze
                if pygame.Vector2(player_pos.x, player_pos.y).distance_to(pygame.Vector2(WIDTH//2, HEIGHT//2 - 50)) < 70:
                    current_state = STATE_DIALOGUE
                    # Emulacja wciśnięcia klawisza dla wywołania dialogu drzewa
                    pygame.event.post(pygame.event.Event(pygame.KEYDOWN, key=pygame.K_RETURN, c_code="TALK_TO_TREE"))

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
        
        if combat_timer % 40 == 0:
            dx, dy = player_combat_pos.x - (WIDTH//2), player_combat_pos.y - 220
            dist = math.hypot(dx, dy) if math.hypot(dx, dy) != 0 else 1
            combat_projectiles.append(Projectile(WIDTH//2, 220, (dx/dist)*6, (dy/dist)*6, (255, 60, 0), 8))
        if combat_timer % 60 == 0: boss_hp -= (base_attack + mod_attack)
        if keys[pygame.K_SPACE] and combat_timer % 15 == 0:
            combat_bullets.append(Projectile(player_combat_pos.x, player_combat_pos.y, 0, -8, (255, 255, 255), 4))

        for b in combat_bullets:
            b.update()
            if pygame.Vector2(b.x, b.y).distance_to(pygame.Vector2(WIDTH//2, 220)) < 35:
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
            if active_boss_type == BOSS_TLUM:
                current_state = STATE_DIALOGUE
                dialogue_title = "Cisza po burzy"
                dialogue_lines = [
                    "Zbroczony krwią stoisz nad ciałami mieszkańców Chołów.",
                    "Przetrwałeś nocną masakrę. Twoje dłonie się trzęsą.",
                    "Droga do Wrocławia stoi otworem, ale mroczny las wciąż wzywa..."
                ]
                dialogue_choices = [
                    ("Wsiądź do Żuka i wracaj do Wrocławia (Koniec Gry)", "END_WROCLAW"),
                    ("Skieruj się do lasu, by dokończyć śledztwo", "GO_FOREST_ALONE")
                ]
                current_choice_idx = 0
                combat_projectiles.clear()
                combat_bullets.clear()

            elif active_boss_type == BOSS_MAMUNA:
                current_state = STATE_DIALOGUE
                dialogue_title = "Nocny Atak w Chołach"
                dialogue_lines = [
                    "Mamuna padła martwa. Odzyskałeś dziecko i wróciłeś do chaty we wsi.",
                    "W nocy budzi cię swąd dymu. Przez okno widzisz Sołtysa i tłum z pochodniami!",
                    "Z cienia w pokoju wyłania się Lusia, córka Sołtysa. Jej oczy nienaturalnie błyszczą.",
                    "Lusia: 'Chcą cię spalić za węszenie! Podaj mi dłoń, znam pradawne ścieżki!'"
                ]
                dialogue_choices = [
                    ("Złap Lusię za rękę (Teleportacja z Lusią)", "LUSIA_TELEPORT"),
                    ("Odepchnij ją. Ucieknę sam oknem! (Test Zręczności)", "LUSIA_REJECT")
                ]
                current_choice_idx = 0
                combat_projectiles.clear()
                combat_bullets.clear()
            else:
                for m in monster_triggers_forest:
                    if m["type"] == active_boss_type: m["beaten"] = True
                current_state = STATE_EXPLORE
                combat_projectiles.clear()
                combat_bullets.clear()
        elif player_hp <= 0:
            end_message = "Ciało Drozda dołączyło do rosnącej listy ofiar Przeklętego Lasu..."
            current_state = STATE_END

    # 2. EVENTY KEYBOARD
    for event in pygame.event.get():
        if event.type == pygame.QUIT: running = False
        elif event.type == pygame.KEYDOWN:
            
            # Wstrzyknięcie z emulacji z STATE_EXPLORE (drzewo)
            if hasattr(event, 'c_code'):
                c_code = event.c_code
            else:
                c_code = None

            if current_state == STATE_INTRO:
                if event.key in [pygame.K_RETURN, pygame.K_SPACE]:
                    intro_step += 1
                    if intro_step >= len(intro_sequence): current_state = STATE_EXPLORE
            
            elif current_state == STATE_TRANSITION:
                if event.key in [pygame.K_RETURN, pygame.K_SPACE]:
                    transition_step += 1
                    if transition_step >= len(transition_sequence):
                        current_map = "FOREST"
                        current_state = STATE_EXPLORE
                        player_pos = pygame.Vector2(WIDTH//2, HEIGHT - 100)

            elif current_state == STATE_DIALOGUE:
                if event.key in [pygame.K_w, pygame.K_UP] and not c_code: 
                    current_choice_idx = (current_choice_idx - 1) % len(dialogue_choices)
                elif event.key in [pygame.K_s, pygame.K_DOWN] and not c_code: 
                    current_choice_idx = (current_choice_idx + 1) % len(dialogue_choices)
                elif event.key in [pygame.K_RETURN, pygame.K_e, pygame.K_SPACE] or c_code:
                    if not c_code and len(dialogue_choices) > 0:
                        c_code = dialogue_choices[current_choice_idx][1]
                    
                    if c_code == "CLUE_TOTEM": clues_found["znaleziono_totem"] = True
                    elif c_code and c_code.startswith("PAY_"):
                        if player_money >= 5:
                            player_money -= 5
                            if c_code == "PAY_SOLTYS": clues_found["zaufanie_soltysa"] = True
                            elif c_code == "PAY_ZIELARKA": clues_found["zaufanie_zielarki"] = True
                        else:
                            dialogue_title = "Brak gotówki"
                            dialogue_lines = ["Nie masz czym zapłacić..."]
                            dialogue_choices = [("Odejdź...", "LEAVE")]
                            current_choice_idx = 0
                            continue
                    elif c_code == "CLUE_KOSCI": clues_found["dowod_kosci"] = True
                    elif c_code == "SLEEP": player_hp = player_max_hp
                    elif c_code == "TALK_MARIA":
                        clues_found["rozmowa_maria"] = True
                        dialogue_title = "Rozmowa z Marią"
                        t, c = get_ksiadz_dialogue()
                        dialogue_lines, dialogue_choices = [t], c
                        current_choice_idx = 0
                        continue
                    elif c_code == "GO_TO_FOREST":
                        current_state = STATE_TRANSITION
                        continue
                    elif c_code == "FIGHT_MAMUNA":
                        current_state = STATE_DICE_ROLL
                        active_boss_type = BOSS_MAMUNA
                        p_d1, p_d2 = random.randint(1,6), random.randint(1,6)
                        m_d1, m_d2 = random.randint(1,6), random.randint(1,6)
                        mod_attack, mod_stamina = (p_d1 + p_d2) - 6, (p_d1 + p_d2) // 2
                        boss_mod_attack, boss_mod_stamina = (m_d1 + m_d2) - 6, (m_d1 + m_d2) // 2
                        boss_hp = boss_max_hp = 100 + (boss_mod_stamina * 5)
                        continue
                    elif c_code == "SPARE_MAMUNA":
                        dialogue_title = "Nocny Atak w Chołach"
                        dialogue_lines = [
                            "Zostawiłeś dziecko Mamunie i w poczuciu rezygnacji wróciłeś do chaty we wsi.",
                            "W nocy budzi cię swąd dymu. Przez okno widzisz Sołtysa i tłum z pochodniami!",
                            "Z cienia w pokoju wyłania się Lusia, córka Sołtysa. Jej oczy nienaturalnie błyszczą.",
                            "Lusia: 'Chcą cię spalić za węszenie! Podaj mi dłoń, znam pradawne ścieżki!'"
                        ]
                        dialogue_choices = [
                            ("Złap Lusię za rękę (Teleportacja z Lusią)", "LUSIA_TELEPORT"),
                            ("Odepchnij ją. Ucieknę sam oknem! (Test Zręczności)", "LUSIA_REJECT")
                        ]
                        current_choice_idx = 0
                        continue
                    
                    # Logika Nocnego Ataku i Lusi
                    elif c_code == "LUSIA_TELEPORT":
                        clues_found["z_lusia"] = True
                        current_map = "STRANGE_PLACE"
                        current_state = STATE_DIALOGUE
                        dialogue_title = "Jądro Lasu"
                        dialogue_lines = [
                            "Teleportujesz się z Lusią przed gigantyczne Drzewo z ludzką twarzą.",
                            "Lusia: 'To duch lasu, mój prawdziwy ojciec. Bieniasz tylko mnie krył.'",
                            "Podejdź i z nim porozmawiaj."
                        ]
                        dialogue_choices = [("Zbadaj Wielkie Drzewo", "EXPLORE_TREE")]
                        current_choice_idx = 0
                        player_pos = pygame.Vector2(WIDTH//2, HEIGHT//2 + 150)
                        continue
                        
                    elif c_code == "LUSIA_REJECT":
                        roll = random.randint(1,6) + random.randint(1,6)
                        if roll >= 7:
                            end_message = f"Wynik Zręczności: {roll} (Sukces!). Zwinny jak kot wyskakujesz oknem,\nomijasz widły i znikasz w ciemnościach lasu. Udało ci się ujść z życiem."
                            current_state = STATE_END
                        else:
                            dialogue_title = "Zasadzka!"
                            dialogue_lines = [
                                f"Wynik Zręczności: {roll} (Porażka!). Potykasz się o framugę",
                                "i spadasz prosto w rozwścieczony tłum z pochodniami!",
                                "Sołtys Bieniasz: 'Zabić miastowego! Wie za dużo!'"
                            ]
                            dialogue_choices = [("Wyciągnij broń i walcz o życie!", "FIGHT_MOB")]
                            current_choice_idx = 0
                        continue
                        
                    elif c_code == "FIGHT_MOB":
                        current_state = STATE_COMBAT
                        active_boss_type = BOSS_TLUM
                        boss_hp = boss_max_hp = 180
                        boss_mod_attack, boss_mod_stamina = 2, 8
                        player_combat_pos = pygame.Vector2(WIDTH//2, HEIGHT//2 + 150)
                        continue
                        
                    elif c_code == "END_WROCLAW":
                        end_message = "Uciekłeś z Chołów, zostawiając za sobą stos ciał.\nWrocław wydaje się bezpieczny, ale w nocy wciąż słyszysz wycie z Głębokiego Lasu..."
                        current_state = STATE_END
                        continue
                        
                    elif c_code == "GO_FOREST_ALONE":
                        current_map = "FOREST"
                        clues_found["z_lusia"] = False
                        current_state = STATE_DIALOGUE
                        dialogue_title = "Zagubiony w Gęstwinie"
                        dialogue_lines = [
                            "Błąkasz się po lesie, oganiając od wilków.",
                            "Nagle drogę zachodzi ci potężna, pokryta mchem i liśćmi sylwetka.",
                            "Leśny Dziadek: 'Ludzki smród... Skądżeś się tu wziął, robaku?'"
                        ]
                        dialogue_choices = [
                            ("Powiedz prawdę o wyrżnięciu wioski", "DZIADEK_TRUTH"),
                            ("Skłam, że szukasz ziół (Test Charyzmy)", "DZIADEK_LIE")
                        ]
                        current_choice_idx = 0
                        player_pos = pygame.Vector2(WIDTH//2, HEIGHT - 50)
                        continue

                    elif c_code == "DZIADEK_TRUTH":
                        end_message = "Leśny Dziadek ryknął gniewem. 'Krew za krew!'\nZanim zdążyłeś dobyć broni, korzenie przebiły twoją klatkę piersiową."
                        current_state = STATE_END
                        continue

                    elif c_code == "DZIADEK_LIE":
                        roll = random.randint(1,6) + random.randint(1,6)
                        if roll >= 7:
                            dialogue_title = "Leśny Dziadek - Przekonany"
                            dialogue_lines = [
                                f"Wynik Charyzmy: {roll} (Sukces!). Dziadek mruczy pod nosem.",
                                "Leśny Dziadek: 'Zioła, powiadasz... Chodź za mną, zaprowadzę cię do Jądra Lasu.'",
                                "Oplata cię winorośl i ciągnie w górę, na wyższe piętro lasu."
                            ]
                            dialogue_choices = [("Podążaj za dziadkiem", "MEET_TREE_ALONE")]
                            current_choice_idx = 0
                        else:
                            end_message = f"Wynik Charyzmy: {roll} (Porażka!). Dziadek przejrzał twoje kłamstwo.\nZostałeś wchłonięty przez puszczę, stając się nawozem."
                            current_state = STATE_END
                        continue
                        
                    elif c_code == "MEET_TREE_ALONE":
                        clues_found["z_lusia"] = False
                        clues_found["spotkal_dziadka"] = True
                        current_map = "STRANGE_PLACE"
                        current_state = STATE_EXPLORE
                        player_pos = pygame.Vector2(WIDTH//2, HEIGHT//2 + 150)
                        continue

                    elif c_code == "EXPLORE_TREE":
                        current_state = STATE_EXPLORE
                        continue

                    elif c_code == "TALK_TO_TREE":
                        dialogue_title = "Rozmowa z Duchem Lasu"
                        dialogue_lines = [
                            "Drzewo dygocze: 'Człowiecze... Mój czas dobiega końca.'",
                            "'Ludzie przestali wierzyć w demony. Las umiera, bo zapomnieli o strachu.'",
                            "'Nasza moc słabnie z każdym zgaszonym ogniskiem, z każdą ściętą sosną...'"
                        ]
                        if clues_found.get("z_lusia", False):
                            dialogue_lines.append("Nagle pojawia się Leśny Dziadek. Pyta Lusię kim jesteś.")
                            dialogue_lines.append("Lusia szybko nakłada ci maskę jelenia. 'To nowy demon, ojcze.'")
                        else:
                            dialogue_lines.append("Lusia stoi obok pnia, spoglądając na ciebie z nieufnością.")
                            dialogue_lines.append("Zaraz potem zjawia się Leśny Dziadek i staje u twego boku.")
                            
                        dialogue_choices = [("Wysłuchaj proroctwa (Ciąg dalszy nastąpi...)", "GAME_TBC")]
                        current_choice_idx = 0
                        player_pos.y += 20 # Przesunięcie by gracz nie wpadł w pętlę od razu
                        continue
                        
                    elif c_code == "GAME_TBC":
                        end_message = "Koniec Rozdziału 1. Odkryłeś tajemnice Głębokiego Lasu.\nDrozd stoi przed wyborem: uratować umierający mit, czy go zniszczyć?"
                        current_state = STATE_END
                        continue

                    # Jeśli to zwykłe opuszczenie lokacji/dialogu (LEAVE)
                    if current_map == "VILLAGE":
                        current_state = STATE_HOUSE
                        player_pos.y += 70 
                    else:
                        current_state = STATE_EXPLORE
                        player_pos.y += 20

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
        screen.blit(font_title.render(intro_sequence[intro_step]["title"], True, (180, 200, 180)), (80, HEIGHT - 180))
        for idx, l in enumerate(intro_sequence[intro_step]["text"].split('\n')):
            screen.blit(font_main.render(l, True, (240, 240, 220)), (80, HEIGHT - 130 + idx*30))
            
    elif current_state == STATE_TRANSITION:
        screen.fill((10, 15, 12))
        screen.blit(font_title.render(transition_sequence[transition_step]["title"], True, (120, 180, 120)), (80, HEIGHT - 180))
        for idx, l in enumerate(transition_sequence[transition_step]["text"].split('\n')):
            screen.blit(font_main.render(l, True, (200, 210, 200)), (80, HEIGHT - 130 + idx*30))

    elif current_state in [STATE_EXPLORE, STATE_HOUSE, STATE_DIALOGUE, STATE_DICE_ROLL]:
        if current_map == "VILLAGE":
            screen.blit(terrain_surface, (0, 0))
            for tx, ty in decorations_trees: draw_tree(screen, tx, ty)
            draw_well(screen, int(well_pos.x), int(well_pos.y))
            for h in houses:
                draw_slavic_house(screen, h.rect.x, h.rect.y, h.rect.width, h.rect.height, h.roof_color, h.ruined)
        
        elif current_map == "FOREST":
            screen.fill((20, 25, 20))
            for tx, ty in forest_trees: draw_tree(screen, tx, ty)
            for m in monster_triggers_forest:
                if not m["beaten"]:
                    pygame.draw.rect(screen, (255, 0, 0), m["rect"], 2) 
        
        elif current_map == "STRANGE_PLACE":
            screen.fill((15, 10, 20)) 
            draw_wielkie_drzewo(screen, WIDTH//2 - 60, HEIGHT//2 - 150)
            if clues_found.get("z_lusia", False):
                draw_lusia(screen, WIDTH//2 + 80, HEIGHT//2 + 50)
            elif clues_found.get("spotkal_dziadka", False):
                draw_lesny_dziadek(screen, WIDTH//2 + 80, HEIGHT//2 + 50)

        if current_state in [STATE_EXPLORE, STATE_HOUSE]:
            draw_drozd(screen, int(player_pos.x), int(player_pos.y))

        if current_state == STATE_DIALOGUE:
            pygame.draw.rect(screen, (20, 20, 25), (40, HEIGHT - 220, WIDTH - 80, 200), border_radius=10)
            pygame.draw.rect(screen, (150, 140, 120), (40, HEIGHT - 220, WIDTH - 80, 200), 2, border_radius=10)
            screen.blit(font_title.render(dialogue_title, True, (200, 180, 150)), (60, HEIGHT - 200))
            for idx, line in enumerate(dialogue_lines):
                screen.blit(font_main.render(line, True, (220, 220, 220)), (60, HEIGHT - 160 + idx * 25))
            for idx, choice in enumerate(dialogue_choices):
                color = (255, 200, 50) if idx == current_choice_idx else (150, 150, 150)
                screen.blit(font_main.render(f"> {choice[0]}", True, color), (60, HEIGHT - 70 + idx * 25))

    elif current_state == STATE_COMBAT:
        screen.fill((15, 10, 10))
        pygame.draw.rect(screen, (50, 0, 0), (WIDTH//2 - 100, 50, 200, 20))
        pygame.draw.rect(screen, (255, 0, 0), (WIDTH//2 - 100, 50, 200 * (boss_hp / boss_max_hp), 20))
        screen.blit(font_title.render(active_boss_type, True, (200, 50, 50)), (WIDTH//2 - 150, 15))
        
        pygame.draw.rect(screen, (0, 0, 50), (20, HEIGHT - 40, 200, 20))
        pygame.draw.rect(screen, (0, 100, 255), (20, HEIGHT - 40, 200 * (player_hp / player_max_hp), 20))
        screen.blit(font_sub.render(f"HP Drozda: {player_hp}/{player_max_hp}", True, (200, 200, 255)), (20, HEIGHT - 65))

        if active_boss_type == BOSS_TLUM:
            draw_mob(screen, WIDTH//2, 220, anim_tick)
        elif active_boss_type == BOSS_LATARNIK:
            draw_monster_latarnik(screen, WIDTH//2 - 15, 200, anim_tick)
        elif active_boss_type == BOSS_PIEN:
            draw_monster_pien(screen, WIDTH//2 - 20, 200)
        elif active_boss_type == BOSS_KRZYKACZ:
            draw_monster_krzykacz(screen, WIDTH//2, 220, anim_tick)
        elif active_boss_type == BOSS_MAMUNA:
            draw_monster_mamuna(screen, WIDTH//2, 220, anim_tick)

        draw_drozd(screen, int(player_combat_pos.x), int(player_combat_pos.y))
        for p in combat_projectiles: p.draw(screen)
        for b in combat_bullets: b.draw(screen)

    elif current_state == STATE_DICE_ROLL:
        screen.fill((20, 20, 25))
        screen.blit(font_title.render("Test Inicjatywy i Przewagi!", True, (200, 200, 150)), (WIDTH//2 - 150, HEIGHT//2 - 100))
        screen.blit(font_main.render(f"Rzut Drozda: {p_d1} + {p_d2} = {p_d1+p_d2}", True, (150, 200, 150)), (WIDTH//2 - 120, HEIGHT//2 - 40))
        screen.blit(font_main.render(f"Rzut Bestii: {m_d1} + {m_d2} = {m_d1+m_d2}", True, (200, 100, 100)), (WIDTH//2 - 120, HEIGHT//2))
        screen.blit(font_main.render("[Wciśnij ENTER aby walczyć (Spacja to strzał)]", True, (100, 100, 100)), (WIDTH//2 - 180, HEIGHT//2 + 60))

    elif current_state == STATE_END:
        screen.fill((0, 0, 0))
        for idx, l in enumerate(end_message.split('\n')):
            screen.blit(font_title.render(l, True, (200, 50, 50)), (WIDTH//2 - 350, HEIGHT//2 - 50 + idx*40))

    pygame.display.flip()

pygame.quit()
sys.exit()
