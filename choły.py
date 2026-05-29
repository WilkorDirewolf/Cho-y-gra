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
STATE_RUNNER = "RUNNER"
STATE_END = "END" 

current_map = "VILLAGE" 
end_message = ""

# --- TYPY WALKI ---
BOSS_MAMUNA = "MAMUNA (Pani Lasu)"
BOSS_LATARNIK = "LATARNIK (Zwodzący Cień)"
BOSS_PIEN = "PIEŃ (Zgniły Strażnik)"
BOSS_GAWRON = "GAWRON (Czarny Anioł)"
BOSS_SKRZEKACZ = "SKRZEKACZ (Demon)"
BOSS_KRZYKACZ_FOREST = "MŁODY KRZYKACZ"
BOSS_TRUE_KRZYKACZ = "KRZYKACZ (Ucieleśnienie Lasu)"

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
        pygame.draw.polygon(surface, roof_color, [(x - 10, y + 30), (x + width // 2, y - 10), (x + width + 10, y + 30)])
    else:
        pygame.draw.polygon(surface, (50, 45, 45), [(x - 10, y + 30), (x + width // 3, y + 5), (x + width + 10, y + 30)])
    pygame.draw.polygon(surface, (60, 45, 30) if not ruined else (10, 10, 10), [(x - 10, y + 30), (x + width // 2, y - 10), (x + width + 10, y + 30)], 2)

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

def draw_monster_latarnik(surface, x, y, anim_tick):
    offset_y = int(math.sin(anim_tick * 0.1) * 5)
    pygame.draw.polygon(surface, (30, 40, 50), [(x, y+20+offset_y), (x+15, y-5+offset_y), (x+30, y+20+offset_y), (x+25, y+45+offset_y), (x+5, y+45+offset_y)])
    pygame.draw.circle(surface, (210, 210, 190), (x + 15, y + offset_y), 8)
    pygame.draw.circle(surface, (150, 0, 0), (x + 12, y - 1 + offset_y), 2)
    pygame.draw.circle(surface, (150, 0, 0), (x + 18, y - 1 + offset_y), 2)
    # Latarnia
    pygame.draw.rect(surface, (200, 150, 50), (x + 30, y + 30 + offset_y, 10, 15))
    pygame.draw.circle(surface, (255, 255, 100), (x + 35, y + 37 + offset_y), 5)

def draw_monster_pien(surface, x, y):
    pygame.draw.rect(surface, (45, 35, 30), (x, y, 40, 50))
    pygame.draw.line(surface, (180, 20, 20), (x + 10, y + 15), (x + 30, y + 25), 3)
    pygame.draw.circle(surface, (180, 255, 100), (x + 20, y + 20), 3)
    
def draw_monster_gawron(surface, x, y):
    pygame.draw.ellipse(surface, (15, 15, 20), (x, y, 40, 60))
    pygame.draw.polygon(surface, (25, 25, 30), [(x, y+20), (x-30, y-20), (x+15, y+30)])
    pygame.draw.circle(surface, (30, 30, 35), (x+20, y-10), 12)
    pygame.draw.polygon(surface, (150, 150, 150), [(x+25, y-10), (x+45, y-5), (x+25, y+2)])

def draw_monster_skrzekacz(surface, x, y):
    pygame.draw.rect(surface, (40, 60, 30), (x, y, 40, 35), border_radius=8)
    pygame.draw.circle(surface, (255, 255, 50), (x+10, y+15), 5)
    pygame.draw.circle(surface, (255, 255, 50), (x+30, y+15), 5)
    pygame.draw.circle(surface, (0, 0, 0), (x+10, y+15), 2)
    pygame.draw.circle(surface, (0, 0, 0), (x+30, y+15), 2)

def draw_monster_mamuna(surface, x, y, anim_tick):
    offset_x = int(math.sin(anim_tick * 0.08) * 3)
    pygame.draw.ellipse(surface, (20, 45, 25), (x - 5 + offset_x, y + 5, 40, 40))
    pygame.draw.circle(surface, (100, 120, 80), (x + 15 + offset_x, y), 9)
    pygame.draw.circle(surface, (255, 0, 0), (x + 15 + offset_x, y), 3)

def draw_true_krzykacz(surface, x, y, anim_tick):
    scale = 1.2 + math.sin(anim_tick * 0.1) * 0.05
    w, h = int(50 * scale), int(90 * scale)
    pygame.draw.ellipse(surface, (40, 35, 45), (x - w//2 + 10, y - h//2 + 20, w, h))
    pygame.draw.polygon(surface, (30, 25, 35), [(x, y), (x-40, y-20), (x, y-40)])
    pygame.draw.polygon(surface, (30, 25, 35), [(x+20, y), (x+60, y-20), (x+20, y-40)])
    pygame.draw.line(surface, (200, 0, 0), (x-40, y-20), (x-55, y-10), 3)
    pygame.draw.line(surface, (200, 0, 0), (x+60, y-20), (x+75, y-10), 3)
    pygame.draw.polygon(surface, (220, 220, 200), [(x-15, y-h//2), (x+35, y-h//2), (x+10, y-h//2+30)])
    pygame.draw.circle(surface, (20, 0, 0), (x-2, y-h//2+10), 5)
    pygame.draw.circle(surface, (20, 0, 0), (x+22, y-h//2+10), 5)
    pygame.draw.line(surface, (150, 140, 120), (x-5, y-h//2), (x-30, y-h//2-40), 4)
    pygame.draw.line(surface, (150, 140, 120), (x+25, y-h//2), (x+50, y-h//2-40), 4)
    pygame.draw.line(surface, (150, 140, 120), (x-20, y-h//2-20), (x-35, y-h//2-10), 3)
    pygame.draw.line(surface, (150, 140, 120), (x+40, y-h//2-20), (x+55, y-h//2-10), 3)

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

class RunnerObstacle:
    def __init__(self, x, y, width, height, type_id, speed):
        self.rect = pygame.Rect(x, y, width, height)
        self.type = type_id # "LOG" lub "VINE"
        self.speed = speed
    def update(self):
        self.rect.x -= self.speed
    def draw(self, surface):
        color = (80, 50, 30) if self.type == "LOG" else (40, 100, 40)
        pygame.draw.rect(surface, color, self.rect, border_radius=4)

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
    "spotkal_dziadka": False,
    "zardzewialy_sztylet": False,
    "ma_amulet_zielarki": False,
    "wspolpraca_z_lusia": False,
    "rozmowa_pien": False,
    "rozmowa_gawron": False,
    "rozmowa_skrzekacz": False,
    "rozmowa_latarnik": False
}

def get_kapliczka_dialogue():
    if clues_found["zardzewialy_sztylet"]: return ("Stara kapliczka. Zabrałeś stąd już wszystko.", [("Odejdź", "LEAVE")])
    return ("Pod deskami starej kapliczki znajdujesz przedziwny artefakt...\nTo Zardzewiały Sztylet, emanujący chłodem.", 
            [("Zabierz sztylet", "CLUE_DAGGER"), ("Zostaw go", "LEAVE")])

def get_soltys_dialogue():
    if clues_found["zaufanie_soltysa"]: return ("Sołtys: Idź do Zielarki. Powiedz, że ja cię przysłałem.", [("Odejdź", "LEAVE")])
    return ("Sołtys: Czego tu szukasz? Wilki zjadły małego, to wielka tragedia.", [("Wrócę później.", "LEAVE")])

def get_zielarka_dialogue():
    if clues_found["zaufanie_zielarki"]: return ("Zielarka: Użyj tego Amuletu przeciw demonom... [ZDOBYTO AMULET]", [("Odejdź", "CLUE_AMULET")])
    if clues_found["zaufanie_soltysa"]:
        return ("Zielarka: Bieniasz cię przysłał? Zapłać 5 zł, a wskażę ci ruinę.", 
                [("Zapłać za wskazówkę (5 zł)", "PAY_ZIELARKA"), ("Odejdź", "LEAVE")])
    return ("Zielarka: Udowodnij najpierw, że tutejsi chcą z tobą gadać.", [("Wyjdź z namiotu", "LEAVE")])

def get_ruiny_dialogue():
    if clues_found["zaufanie_zielarki"] and not clues_found["dowod_kosci"]:
        return ("Rozgarniasz popiół w piecu. Znajdujesz zwęglone kości odmieńca...", 
                [("Zabezpiecz dowód", "CLUE_KOSCI")])
    elif clues_found["dowod_kosci"]: return ("Masz już dowód. Czas porozmawiać z księdzem.", [("Odejdź", "LEAVE")])
    return ("Osmalone ściany potęgują odór dawnego pożaru.", [("Odejdź", "LEAVE")])

def get_ksiadz_dialogue():
    if clues_found["rozmowa_maria"]:
        return ("Maria: Mamuna uciekła do Lasu... Błagam cię, pomścij mnie.", 
                [("Wyrusz z bronią do Głębokiego Lasu", "GO_TO_FOREST"), ("Daj mi chwilę", "LEAVE")])
    if clues_found["dowod_kosci"]:
        return ("Ksiądz: To prawda... Maria miała rację. Ukryłem ją u siebie.", [("Porozmawiaj z Marią", "TALK_MARIA")])
    return ("Ksiądz: Zdobądź zaufanie wsi, wtedy porozmawiamy.", [("Wyjdź", "LEAVE")])

def get_bed_dialogue():
    return ("Twoje posłanie w starej chacie po Mikołaju.", [("Prześpij się (Regeneracja HP)", "SLEEP"), ("Wyjdź", "LEAVE")])

houses = [
    House(250, 60, 160, 110, "Dom Sołtysa Bieniasza", get_soltys_dialogue),
    House(140, 320, 130, 90, "Chata po starym Mikołaju", get_bed_dialogue),
    House(780, 80, 140, 100, "Namiot Starej Zielarki", get_zielarka_dialogue),
    House(720, 320, 150, 110, "Spalona Chata Marii", get_ruiny_dialogue, ruined=True),
    House(60, 480, 150, 130, "Plebania", get_ksiadz_dialogue, roof_color=(120, 40, 30)),
    House(420, 240, 80, 100, "Stara Kapliczka", get_kapliczka_dialogue, roof_color=(80, 80, 90))
]

decorations_trees = [(40, 260), (50, 500), (360, 180), (280, 550), (660, 120), (690, 200), (880, 500), (900, 250)]
forest_trees = [(random.randint(-10, WIDTH-20), random.randint(-10, HEIGHT-20)) for _ in range(80)]

# Przerobione rozmieszczenie NPC w lesie
monster_triggers_forest = [
    {"rect": pygame.Rect(WIDTH//2 - 250, HEIGHT//2 - 200, 60, 60), "type": BOSS_LATARNIK, "beaten": False},
    {"rect": pygame.Rect(WIDTH//2 + 190, HEIGHT//2 - 200, 60, 60), "type": BOSS_PIEN, "beaten": False},
    {"rect": pygame.Rect(WIDTH//2 - 250, HEIGHT//2 + 150, 60, 60), "type": BOSS_KRZYKACZ_FOREST, "beaten": False},
    {"rect": pygame.Rect(WIDTH//2 + 190, HEIGHT//2 + 150, 60, 60), "type": BOSS_MAMUNA, "beaten": False},
    {"rect": pygame.Rect(WIDTH//2 - 50, HEIGHT//2 - 250, 60, 60), "type": BOSS_GAWRON, "beaten": False},
    {"rect": pygame.Rect(WIDTH//2 - 50, HEIGHT//2 + 200, 60, 60), "type": BOSS_SKRZEKACZ, "beaten": False}
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

# Parametry mechaniki Latarnika
latarnik_fatigue = 0
latarnik_max_fatigue = 40
latarnik_pos = pygame.Vector2(WIDTH//2, 200)

dialogue_title, dialogue_lines, dialogue_choices = "", [], []
current_choice_idx = 0

# Zmienne walki na arenie
combat_projectiles, combat_bullets = [], []
combat_timer = 0
player_combat_pos = pygame.Vector2(WIDTH//2, HEIGHT//2 + 100)

# Zmienne Runnera (Ucieczki)
runner_mode_vines = False
runner_player_y = HEIGHT - 150
runner_player_vy = 0
runner_is_jumping = False
runner_ground_y = HEIGHT - 150
runner_obstacles = []
runner_bolts = []
runner_dziadek_hp = 150
runner_dziadek_max_hp = 150
runner_timer = 0

font_main = pygame.font.SysFont("georgia", 20)
font_sub = pygame.font.SysFont("arial", 15)
font_title = pygame.font.SysFont("georgia", 24, bold=True)

terrain_surface = pygame.Surface((WIDTH, HEIGHT))
for ty in range(0, HEIGHT, 50):
    for tx in range(0, WIDTH, 50):
        base_g = random.randint(25, 38)
        pygame.draw.rect(terrain_surface, (int(base_g*0.85), base_g, int(base_g*0.65)), (tx, ty, 50, 50))

intro_sequence = [
    {"title": "Wnętrze Żuka. Czuć benzynę.", "text": "Kierowca Władek: W Chołach zjedli dzieciaka... węszy tu zło."},
    {"title": "Wioska Choły.", "text": "Porozmawiaj z ludźmi. Znajdź poszlaki, by popchnąć sprawę do przodu."}
]
intro_step = 0

# --- GŁÓWNA PĘTLA ---
running = True
while running:
    anim_tick += 1
    clock.tick(60)
    keys = pygame.key.get_pressed()

    # 1. RUCH / EKSPLORACJA
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
                        
                        # Przechwytywanie dialogów demonów
                        if active_boss_type == BOSS_MAMUNA and not clues_found["mamuna_rozmowa"]:
                            current_state = STATE_DIALOGUE
                            dialogue_title = "Leże Mamuny - Konfrontacja"
                            dialogue_lines = ["Mamuna gładzi ludzkie niemowlę...", "Zostaw nas w spokoju, a las nie skrzywdzi was więcej."]
                            dialogue_choices = [("Oddaj dziecko i giń z moich rąk!", "FIGHT_MAMUNA"), ("Opuść broń. (Zostaw dziecko Mamunie)", "SPARE_MAMUNA")]
                            current_choice_idx = 0
                            clues_found["mamuna_rozmowa"] = True
                            player_pos.y += 20 
                            break
                        elif active_boss_type == BOSS_LATARNIK and not clues_found["rozmowa_latarnik"]:
                            current_state = STATE_DIALOGUE
                            dialogue_title = "Spotkanie z Latarnikiem"
                            dialogue_lines = ["Latarnik drży zawieszony w powietrzu. Trzyma żarzącą się latarnię z głowy chochlika."]
                            dialogue_choices = [("Zaatakuj Latarnika", "START_LATARNIK_FIGHT")]
                            if clues_found["ma_amulet_zielarki"]:
                                dialogue_choices.insert(0, ("Podaj mu amulet od Zielarki (Osłabi to jego ataki)", "GIVE_AMULET"))
                            current_choice_idx = 0
                            clues_found["rozmowa_latarnik"] = True
                            player_pos.y += 20
                            break
                        elif active_boss_type == BOSS_PIEN and not clues_found["rozmowa_pien"]:
                            current_state = STATE_DIALOGUE
                            dialogue_title = "Spotkanie z Pniem"
                            dialogue_lines = ["Demon Pień o aparycji tłustego prosiaka z głową łosia chrumka groźnie."]
                            dialogue_choices = [("Pytaj o Latarnika", "INFO_LATARNIK"), ("Zdradź się jako demon łowca (Walka)", "START_GENERIC_FIGHT")]
                            current_choice_idx = 0
                            player_pos.y += 20
                            break
                        elif active_boss_type == BOSS_GAWRON and not clues_found["rozmowa_gawron"]:
                            current_state = STATE_DIALOGUE
                            dialogue_title = "Spotkanie z Gawronem"
                            dialogue_lines = ["Gawron - anioł z głową czarnego ptaka, przygląda ci się podejrzliwie."]
                            dialogue_choices = [("Gdzie leży legowisko Krzykacza?", "INFO_KRZYKACZ_LAIR"), ("Zdradź się (Walka)", "START_GENERIC_FIGHT")]
                            current_choice_idx = 0
                            player_pos.y += 20
                            break
                        elif active_boss_type == BOSS_SKRZEKACZ and not clues_found["rozmowa_skrzekacz"]:
                            current_state = STATE_DIALOGUE
                            dialogue_title = "Spotkanie ze Skrzekaczem"
                            dialogue_lines = ["Zza liści wyłania się Skrzekacz, cichy demon bagienny."]
                            dialogue_choices = [("Pytaj o Lusię", "INFO_LUSIA"), ("Zdradź się (Walka)", "START_GENERIC_FIGHT")]
                            current_choice_idx = 0
                            player_pos.y += 20
                            break
                        elif m["beaten"] == False and active_boss_type not in [BOSS_LATARNIK, BOSS_PIEN, BOSS_GAWRON, BOSS_SKRZEKACZ, BOSS_MAMUNA]:
                            # Inne bezpośrednie walki
                            current_state = STATE_DICE_ROLL
                            boss_hp = boss_max_hp = 100
                            break
            
            elif current_map == "STRANGE_PLACE":
                if pygame.Vector2(player_pos.x, player_pos.y).distance_to(pygame.Vector2(WIDTH//2, HEIGHT//2 - 50)) < 70:
                    current_state = STATE_DIALOGUE
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

    # WALKA - ARENA
    elif current_state == STATE_COMBAT:
        combat_timer += 1
        c_speed = 5
        if keys[pygame.K_w] or keys[pygame.K_UP]: player_combat_pos.y -= c_speed
        if keys[pygame.K_s] or keys[pygame.K_DOWN]: player_combat_pos.y += c_speed
        if keys[pygame.K_a] or keys[pygame.K_LEFT]: player_combat_pos.x -= c_speed
        if keys[pygame.K_d] or keys[pygame.K_RIGHT]: player_combat_pos.x += c_speed
        player_combat_pos.x = max(100, min(WIDTH-100, player_combat_pos.x))
        player_combat_pos.y = max(150, min(HEIGHT-50, player_combat_pos.y))
        
        # LOGIKA LATARNIKA (zależna od zmęczenia i wyborów)
        if active_boss_type == BOSS_LATARNIK:
            speed_multiplier = max(0.2, 1.0 - (latarnik_fatigue / latarnik_max_fatigue))
            latarnik_pos.x += math.sin(combat_timer * 0.1) * 15 * speed_multiplier
            latarnik_pos.y += math.cos(combat_timer * 0.15) * 10 * speed_multiplier
            latarnik_pos.x = max(100, min(WIDTH-100, latarnik_pos.x))
            latarnik_pos.y = max(50, min(HEIGHT//2, latarnik_pos.y))
            
            if combat_timer % max(10, int(35 * speed_multiplier)) == 0:
                dx, dy = player_combat_pos.x - latarnik_pos.x, player_combat_pos.y - latarnik_pos.y
                dist = math.hypot(dx, dy) if math.hypot(dx, dy) != 0 else 1
                combat_projectiles.append(Projectile(latarnik_pos.x, latarnik_pos.y, (dx/dist)*8, (dy/dist)*8, (0, 255, 255), 8))
        else:
            # Atak standardowych Bossów
            fire_rate = 40 if active_boss_type != BOSS_TRUE_KRZYKACZ else 25
            if combat_timer % fire_rate == 0:
                dx, dy = player_combat_pos.x - (WIDTH//2), player_combat_pos.y - 220
                dist = math.hypot(dx, dy) if math.hypot(dx, dy) != 0 else 1
                spd = 6 if active_boss_type != BOSS_TRUE_KRZYKACZ else 9
                color = (255, 60, 0) if active_boss_type != BOSS_TRUE_KRZYKACZ else (100, 0, 0)
                combat_projectiles.append(Projectile(WIDTH//2, 220, (dx/dist)*spd, (dy/dist)*spd, color, 10))
            
        # Strzelanie gracza
        if keys[pygame.K_SPACE] and combat_timer % 15 == 0:
            combat_bullets.append(Projectile(player_combat_pos.x, player_combat_pos.y, 0, -10, (255, 255, 255), 4))

        for b in combat_bullets:
            b.update()
            target_pos = latarnik_pos if active_boss_type == BOSS_LATARNIK else pygame.Vector2(WIDTH//2, 220)
            if pygame.Vector2(b.x, b.y).distance_to(target_pos) < 45:
                boss_hp -= max(1, 10 + mod_attack)
                combat_bullets.remove(b)
            elif b.y < 100: combat_bullets.remove(b)

        for p in combat_projectiles:
            p.update()
            if pygame.Vector2(p.x, p.y).distance_to(player_combat_pos) < 20:
                dmg = max(1, 10 + boss_mod_attack)
                if active_boss_type == BOSS_TRUE_KRZYKACZ: dmg = 15
                player_hp -= dmg
                combat_projectiles.remove(p)
            elif p.x < 0 or p.x > WIDTH or p.y < 0 or p.y > HEIGHT:
                # MECHANIKA ZMĘCZENIA - Każdy udany unik gracza przeciwko Latarnikowi
                if active_boss_type == BOSS_LATARNIK and latarnik_fatigue < latarnik_max_fatigue:
                    latarnik_fatigue += 1
                combat_projectiles.remove(p)

        # INSTA-KILL KRZYKACZA
        if active_boss_type == BOSS_TRUE_KRZYKACZ and player_hp < player_max_hp / 3:
            end_message = "Krzykacz ryczy przeraźliwie, podnosi cię potężnymi łapami...\nJego kościana szczęka jelenia zamyka się na twojej głowie.\nZostałeś pożarty. (GAME OVER)"
            current_state = STATE_END

        elif boss_hp <= 0:
            if active_boss_type == BOSS_TRUE_KRZYKACZ:
                end_message = "Zabiłeś Krzykacza. Prastara obrona lasu padła...\nDrwale z urzędu wkrótce zetną wszystko. Las umrze, ale Choły są bezpieczne."
                current_state = STATE_END
            else:
                for m in monster_triggers_forest:
                    if m["type"] == active_boss_type: m["beaten"] = True
                current_state = STATE_EXPLORE
                combat_projectiles.clear()
                combat_bullets.clear()
                
        elif player_hp <= 0:
            end_message = "Ciało Drozda dołączyło do rosnącej listy ofiar Przeklętego Lasu..."
            current_state = STATE_END

    # WALKA - RUNNER (Ucieczka przed Dziadkiem)
    elif current_state == STATE_RUNNER:
        runner_timer += 1
        
        runner_player_vy += 1 
        runner_player_y += runner_player_vy
        if runner_player_y >= runner_ground_y:
            runner_player_y = runner_ground_y
            runner_is_jumping = False

        if (keys[pygame.K_SPACE] or keys[pygame.K_UP] or keys[pygame.K_w]) and not runner_is_jumping:
            runner_player_vy = -16
            runner_is_jumping = True

        if random.randint(1, 60) == 1:
            o_type = "LOG"
            if runner_mode_vines and random.choice([True, False]): o_type = "VINE"
            runner_obstacles.append(RunnerObstacle(WIDTH + 50, runner_ground_y + 10, 30, 40, o_type, 7))

        for o in runner_obstacles[:]:
            o.update()
            if o.rect.colliderect(pygame.Rect(400, runner_player_y, 30, 40)):
                player_hp -= 15
                runner_obstacles.remove(o)
            elif o.rect.right < 0:
                runner_obstacles.remove(o)

        for b in runner_bolts[:]:
            b.x -= 10
            if b.x < 150:
                runner_dziadek_hp -= 10
                runner_bolts.remove(b)

        if runner_dziadek_hp <= 0:
            end_message = "Zgubiłeś Dziadka i zgładziłeś go z kuszy!\nUratowałeś drwali z urzędu. Lecz twój konflikt z Lasem dopiero się zaczął..."
            current_state = STATE_END
        elif player_hp <= 0:
            end_message = "Potknąłeś się, a pnącza Leśnego Dziadka wciągnęły cię pod ziemię.\nStałeś się nawozem dla umierającej puszczy. (GAME OVER)"
            current_state = STATE_END

    # 2. EVENTY KEYBOARD
    for event in pygame.event.get():
        if event.type == pygame.QUIT: running = False
        elif event.type == pygame.KEYDOWN:
            
            c_code = getattr(event, 'c_code', None)

            if current_state == STATE_INTRO:
                if event.key in [pygame.K_RETURN, pygame.K_SPACE]:
                    intro_step += 1
                    if intro_step >= len(intro_sequence): current_state = STATE_EXPLORE
            
            elif current_state == STATE_TRANSITION:
                if event.key in [pygame.K_RETURN, pygame.K_SPACE]:
                    current_map = "FOREST"
                    current_state = STATE_EXPLORE
                    player_pos = pygame.Vector2(WIDTH//2, HEIGHT - 100)

            elif current_state == STATE_RUNNER:
                if event.key in [pygame.K_e, pygame.K_RETURN] and runner_timer % 15 != 0:
                    runner_bolts.append(pygame.Rect(400, runner_player_y + 10, 15, 5))

            elif current_state == STATE_DIALOGUE:
                if event.key in [pygame.K_w, pygame.K_UP] and not c_code: 
                    current_choice_idx = (current_choice_idx - 1) % len(dialogue_choices)
                elif event.key in [pygame.K_s, pygame.K_DOWN] and not c_code: 
                    current_choice_idx = (current_choice_idx + 1) % len(dialogue_choices)
                elif event.key in [pygame.K_RETURN, pygame.K_e, pygame.K_SPACE] or c_code:
                    if not c_code and len(dialogue_choices) > 0:
                        c_code = dialogue_choices[current_choice_idx][1]
                    
                    if c_code == "CLUE_TOTEM": clues_found["znaleziono_totem"] = True
                    elif c_code == "CLUE_DAGGER": clues_found["zardzewialy_sztylet"] = True
                    elif c_code == "CLUE_AMULET": 
                        clues_found["ma_amulet_zielarki"] = True
                        current_state = STATE_EXPLORE
                        continue
                    elif c_code and c_code.startswith("PAY_"):
                        if player_money >= 5:
                            player_money -= 5
                            if c_code == "PAY_ZIELARKA": clues_found["zaufanie_zielarki"] = True
                        else:
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
                    
                    # LOGIKA NPC W LESIE
                    elif c_code == "INFO_LATARNIK":
                        dialogue_title = "Wiedza Demona Pnia"
                        dialogue_lines = ["Pień: Na tym piętrze lasu ukrywa się Latarnik.", "Jego latarnia z głowy chochlika wybudzi samego Krzykacza!"]
                        dialogue_choices = [("Zrozumiałem.", "CROSS_DECISION")]
                        current_choice_idx = 0
                        clues_found["rozmowa_pien"] = True
                        continue
                    elif c_code == "INFO_KRZYKACZ_LAIR":
                        dialogue_title = "Wiedza Gawrona"
                        dialogue_lines = ["Gawron: Ostateczne leże Krzykacza znajduje się tuż obok...", "Śpij, jeśli nie chcesz zginąć z jego pazurów."]
                        dialogue_choices = [("Zrozumiałem.", "CROSS_DECISION")]
                        current_choice_idx = 0
                        clues_found["rozmowa_gawron"] = True
                        continue
                    elif c_code == "INFO_LUSIA":
                        dialogue_title = "Tajemnica Lusi"
                        dialogue_lines = ["Skrzekacz: Lusia to patron tego lasu! Jeśli będzie miała ochotę,", "może zrównać Choły z ziemią na pstryknięcie palcem."]
                        dialogue_choices = [("To zmienia postać rzeczy.", "CROSS_DECISION")]
                        current_choice_idx = 0
                        clues_found["rozmowa_skrzekacz"] = True
                        continue
                    elif c_code == "CROSS_DECISION":
                        dialogue_title = "Rozwidlenie Ścieżek"
                        dialogue_lines = ["Wybierz mądrze co dalej."]
                        dialogue_choices = [("Wróc do eksploracji", "LEAVE")]
                        if clues_found["rozmowa_pien"]: dialogue_choices.append(("Idź zniszczyć Latarnika", "START_LATARNIK_FIGHT"))
                        if clues_found["rozmowa_gawron"]: dialogue_choices.append(("Idź do leża Krzykacza", "START_KRZYKACZ_FIGHT"))
                        if clues_found["rozmowa_skrzekacz"]: dialogue_choices.append(("Próbuj zwerbować Lusię (Teleport)", "RECRUIT_LUSIA"))
                        current_choice_idx = 0
                        continue

                    # ZWERBOWANIE LUSI
                    elif c_code == "RECRUIT_LUSIA":
                        clues_found["wspolpraca_z_lusia"] = True
                        dialogue_title = "Pomoc Patronki"
                        dialogue_lines = ["Lusia decyduje się pomóc. Teleportuje cię od razu do leża Latarnika!"]
                        dialogue_choices = [("Zawalcz z nim (Masz wsparcie!)", "START_LATARNIK_FIGHT")]
                        current_choice_idx = 0
                        continue

                    # WALKI Z NPC
                    elif c_code == "START_GENERIC_FIGHT":
                        current_state = STATE_COMBAT
                        boss_hp = boss_max_hp = 150
                        boss_mod_attack = 0
                        combat_timer = 0
                        combat_projectiles.clear()
                        continue
                    
                    elif c_code == "GIVE_AMULET":
                        dialogue_title = "Osłabienie Latarnika"
                        dialogue_lines = ["Rzucasz mu amulet Zielarki. Jego światło przygasa! (Atak osłabiony)"]
                        dialogue_choices = [("Zakończ to!", "START_LATARNIK_FIGHT_AMULET")]
                        current_choice_idx = 0
                        continue

                    elif c_code.startswith("START_LATARNIK_FIGHT"):
                        current_state = STATE_COMBAT
                        active_boss_type = BOSS_LATARNIK
                        latarnik_fatigue = 0
                        boss_hp = boss_max_hp = 200
                        
                        # Obliczanie kar i bonusów
                        boss_mod_attack = -2 if clues_found["ma_amulet_zielarki"] else 2
                        mod_attack = 0 if clues_found["wspolpraca_z_lusia"] else -2

                        combat_timer = 0
                        combat_projectiles.clear()
                        continue

                    # LOGIKA JĄDRA LASU (Wywód Drzewa, Drwale i Krzykacz)
                    elif c_code == "TALK_TO_TREE":
                        dialogue_title = "Rozmowa z Duchem Lasu"
                        dialogue_lines = [
                            "Duch Lasu: 'Mój czas dobiega końca. A jakby tego było mało, urząd powiatowy",
                            "chce przysłać drwali z piłami, by ściąć resztę Chołów!'",
                            "Leśny Dziadek uśmiecha się zimno: 'Obudzimy Krzykacza. Przerobi ich",
                            "wszystkich na gęsty, mięsny dżem. Las pochłonie ich krew.'",
                            "Drozd ukrywa przerażenie... Musi powstrzymać rzeź, ale jak?"
                        ]
                        dialogue_choices = [
                            ("Atakuj Dziadka kuszą z zaskoczenia! (Walka - Trudne)", "TREE_FIGHT_DZIADEK"),
                            ("Okłam ich: 'Urząd wycofał drwali!' (Test Charyzmy)", "TREE_LIE_1")
                        ]
                        if clues_found.get("z_lusia", False):
                            dialogue_choices.append(("Przekonaj Lusię by ich powstrzymała (+2 Charyzma)", "TREE_LUSIA"))
                        if clues_found.get("zardzewialy_sztylet", False):
                            dialogue_choices.append(("[PRZEDMIOT] Wbij Zardzewiały Sztylet w Drzewo!", "TREE_STAB"))
                        
                        current_choice_idx = 0
                        player_pos.y += 20 
                        continue

                    elif c_code == "TREE_STAB":
                        dialogue_title = "Krzykacz Przebudzony!"
                        dialogue_lines = [
                            "Wbijasz sztylet w rdzeń Ducha Lasu. Drzewo wyje z bólu!",
                            "Ziemia pęka. Z otchłani wynurza się gigantyczny wilk z czaszką jelenia.",
                            "Prawdziwy Krzykacz ryczy. Rozpoczyna się ostateczna bitwa."
                        ]
                        dialogue_choices = [("Zdobądź broń, to jest to! (Walka o życie)", "START_KRZYKACZ_FIGHT")]
                        current_choice_idx = 0
                        continue
                        
                    elif c_code == "START_KRZYKACZ_FIGHT":
                        current_state = STATE_COMBAT
                        active_boss_type = BOSS_TRUE_KRZYKACZ
                        boss_hp = boss_max_hp = 300
                        boss_mod_attack = 5
                        combat_timer = 0
                        combat_projectiles.clear()
                        continue

                    elif c_code == "TREE_FIGHT_DZIADEK":
                        current_state = STATE_RUNNER
                        runner_mode_vines = False
                        runner_dziadek_hp = runner_dziadek_max_hp = 150
                        runner_obstacles.clear()
                        runner_timer = 0
                        continue

                    elif c_code == "TREE_LIE_1":
                        roll = random.randint(1,6) + random.randint(1,6)
                        if roll >= 7:
                            dialogue_title = "Charyzma (Sukces!)"
                            dialogue_lines = [
                                "Dziadek zawahał się, ale Duch Lasu wtrąca się:",
                                "Duch Lasu: 'Czuję kłamstwo. Korzenie mówią co innego. Śledzą nas.'",
                                "Musisz przekonać Ducha, że masz pewne źródło z Urzędu (Próg: rzuć 6)."
                            ]
                            dialogue_choices = [("Spróbuj przekonać Ducha (Rzut 1d6)", "TREE_LIE_2")]
                            current_choice_idx = 0
                        else:
                            dialogue_title = "Charyzma (Porażka!)"
                            dialogue_lines = ["Leśny Dziadek: 'Łżesz, psie miastowy!' Rzuca się na ciebie!"]
                            dialogue_choices = [("Uciekaj! (Walka)", "TREE_FIGHT_DZIADEK")]
                            current_choice_idx = 0
                        continue

                    elif c_code == "TREE_LIE_2":
                        roll = random.randint(1,6)
                        if roll == 6:
                            end_message = "Wynik: 6! Duch Lasu uwierzył ci, że jesteś ich wtyczką w urzędzie.\nWypuszczenie Krzykacza zostaje opóźnione o 3 dni. Uratowałeś drwali!\n(SUKCES - Koniec Epizodu)"
                            current_state = STATE_END
                        else:
                            dialogue_title = "Charyzma (Porażka!)"
                            dialogue_lines = [f"Wynik: {roll}. Duch Lasu oplata cię pnączami! 'KŁAMCA!'"]
                            dialogue_choices = [("Uciekaj! (Walka z przeszkodami pnączy)", "TREE_FIGHT_DZIADEK_HARD")]
                            current_choice_idx = 0
                        continue

                    elif c_code == "TREE_LUSIA":
                        roll = random.randint(1,6) + random.randint(1,6) + 2
                        if roll >= 8:
                            end_message = f"Wynik z Lusią: {roll}. Lusia staje w twojej obronie.\nOna przekonuje Ducha Lasu, by odroczyć pobudkę Krzykacza o 3 dni.\nPokój, póki co, został zachowany. (SUKCES - Koniec Epizodu)"
                            current_state = STATE_END
                        else:
                            dialogue_title = "Zdrada!"
                            dialogue_lines = [
                                f"Wynik: {roll} (Porażka!). Lusia odsuwa się z odrazą.",
                                "Lusia: 'On kłamie Ojcze! To zdrajca, zabijcie go!'",
                                "Ziemia pod tobą eksploduje tysiącem pnączy!"
                            ]
                            dialogue_choices = [("Uciekaj! (Walka + Pnącza)", "TREE_FIGHT_DZIADEK_HARD")]
                            current_choice_idx = 0
                        continue
                        
                    elif c_code == "TREE_FIGHT_DZIADEK_HARD":
                        current_state = STATE_RUNNER
                        runner_mode_vines = True
                        runner_dziadek_hp = runner_dziadek_max_hp = 180
                        runner_obstacles.clear()
                        runner_timer = 0
                        continue

                    if current_map == "VILLAGE":
                        current_state = STATE_HOUSE
                        player_pos.y += 70 
                    else:
                        current_state = STATE_EXPLORE
                        player_pos.y += 20

            elif current_state == STATE_END:
                if event.key == pygame.K_ESCAPE: running = False

    # 3. RENDEROWANIE
    if current_state == STATE_INTRO:
        screen.fill((12, 15, 12))
        screen.blit(font_title.render(intro_sequence[intro_step]["title"], True, (180, 200, 180)), (80, HEIGHT - 180))
        screen.blit(font_main.render(intro_sequence[intro_step]["text"], True, (240, 240, 220)), (80, HEIGHT - 130))
            
    elif current_state == STATE_TRANSITION:
        screen.fill((10, 15, 12))
        screen.blit(font_title.render("Wejście w głąb puszczy...", True, (120, 180, 120)), (80, HEIGHT - 180))

    elif current_state in [STATE_EXPLORE, STATE_HOUSE, STATE_DIALOGUE, STATE_DICE_ROLL]:
        if current_map == "VILLAGE":
            if current_state == STATE_HOUSE or (current_state == STATE_DIALOGUE and active_house is not None):
                # Tło wnętrza
                screen.fill((10, 10, 12))
                
                # Podłoga i ściany
                pygame.draw.rect(screen, (50, 40, 30), (50, 50, WIDTH - 100, HEIGHT - 100))
                pygame.draw.rect(screen, (30, 20, 15), (50, 50, WIDTH - 100, HEIGHT - 100), 10)
                
                # Środek pokoju z "dywanem" pokazujący graczowi dokąd iść (triggeruje dialog)
                pygame.draw.circle(screen, (80, 40, 30), (WIDTH//2, HEIGHT//2), 65) 
                pygame.draw.circle(screen, (200, 180, 150), (WIDTH//2, HEIGHT//2), 20) # Ikonka NPC
                
                # Wyświetlanie UI domku
                house_name = active_house.name if active_house else "Wnętrze"
                screen.blit(font_title.render("Wnętrze: " + house_name, True, (220, 200, 150)), (70, 70))
                screen.blit(font_sub.render("Podejdź na środek, aby porozmawiać. Przejdź za krawędź ekranu, by wyjść.", True, (150, 150, 150)), (70, 110))
            else:
                screen.blit(terrain_surface, (0, 0))
                for tx, ty in decorations_trees: draw_tree(screen, tx, ty)
                draw_well(screen, 490, 420)
                for h in houses:
                    draw_slavic_house(screen, h.rect.x, h.rect.y, h.rect.width, h.rect.height, h.roof_color, h.ruined)
        
        elif current_map == "FOREST":
            screen.fill((20, 25, 20))
            for tx, ty in forest_trees: draw_tree(screen, tx, ty)
        
        elif current_map == "STRANGE_PLACE":
            screen.fill((15, 10, 20)) 
            draw_wielkie_drzewo(screen, WIDTH//2 - 60, HEIGHT//2 - 150)
            if clues_found.get("z_lusia", False): draw_lusia(screen, WIDTH//2 + 80, HEIGHT//2 + 50)
            draw_lesny_dziadek(screen, WIDTH//2 - 80, HEIGHT//2 + 50)

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
        
        # Wyrysowanie specyficznego bossa
        if active_boss_type == BOSS_TRUE_KRZYKACZ: 
            draw_true_krzykacz(screen, WIDTH//2, 220, anim_tick)
        elif active_boss_type == BOSS_LATARNIK:
            draw_monster_latarnik(screen, int(latarnik_pos.x - 15), int(latarnik_pos.y), anim_tick)
        elif active_boss_type == BOSS_PIEN:
            draw_monster_pien(screen, WIDTH//2 - 20, 200)
        elif active_boss_type == BOSS_GAWRON:
            draw_monster_gawron(screen, WIDTH//2 - 15, 200)
        elif active_boss_type == BOSS_SKRZEKACZ:
            draw_monster_skrzekacz(screen, WIDTH//2 - 20, 200)

        draw_drozd(screen, int(player_combat_pos.x), int(player_combat_pos.y))
        for p in combat_projectiles: p.draw(screen)
        for b in combat_bullets: b.draw(screen)

    elif current_state == STATE_RUNNER:
        screen.fill((15, 25, 15))
        pygame.draw.line(screen, (80, 60, 40), (0, runner_ground_y + 40), (WIDTH, runner_ground_y + 40), 10)
        
        # UI
        pygame.draw.rect(screen, (0, 0, 50), (20, 20, 200, 20))
        pygame.draw.rect(screen, (0, 100, 255), (20, 20, 200 * (player_hp / player_max_hp), 20))
        screen.blit(font_sub.render("HP Drozda", True, (255,255,255)), (25, 22))

        pygame.draw.rect(screen, (50, 0, 0), (WIDTH - 220, 20, 200, 20))
        pygame.draw.rect(screen, (255, 0, 0), (WIDTH - 220, 20, 200 * (runner_dziadek_hp / runner_dziadek_max_hp), 20))
        screen.blit(font_sub.render("HP Leśnego Dziadka", True, (255,255,255)), (WIDTH - 215, 22))

        screen.blit(font_main.render("[SPACE] - Skok  |  [E] - Strzał do tyłu", True, (150, 150, 150)), (WIDTH//2 - 150, 60))

        # Rysowanie jednostek
        draw_drozd(screen, 400, int(runner_player_y))
        draw_lesny_dziadek(screen, 100, runner_ground_y + int(math.sin(runner_timer*0.2)*5))
        
        for o in runner_obstacles: o.draw(screen)
        for b in runner_bolts: pygame.draw.rect(screen, (200, 200, 200), b)

    elif current_state == STATE_DICE_ROLL:
        screen.fill((20, 20, 25))
        screen.blit(font_main.render("[Wciśnij ENTER]", True, (100, 100, 100)), (WIDTH//2 - 100, HEIGHT//2))

    elif current_state == STATE_END:
        screen.fill((0, 0, 0))
        for idx, l in enumerate(end_message.split('\n')):
            screen.blit(font_title.render(l, True, (200, 50, 50)), (WIDTH//2 - 400, HEIGHT//2 - 50 + idx*40))
        screen.blit(font_sub.render("[ESC] - Wyjście", True, (100,100,100)), (WIDTH//2 - 50, HEIGHT - 50))

    pygame.display.flip()

pygame.quit()
sys.exit()
