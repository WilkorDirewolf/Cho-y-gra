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

current_map = "VILLAGE" # "VILLAGE" lub "FOREST"
end_message = ""

# --- TYPY WALKI ---
BOSS_MAMUNA = "MAMUNA (Pani Lasu)"
BOSS_LATARNIK = "LATARNIK (Zwodzący Cień)"
BOSS_PIEN = "PIEN (Zgniły Strażnik)"
BOSS_KRZYKACZ = "KRZYKACZ (Bestia Dźwięku)"

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
    "mamuna_rozmowa": False  # Nowa flaga dla finałowego wyboru
}

def get_kapliczka_dialogue():
    if clues_found["znaleziono_totem"]:
        return ("Stara, opuszczona kapliczka obok lasu. Ktoś rzadko tu zagląda.\nNic tu więcej nie znajdziesz.", 
                [("Odejdź", "LEAVE")])
    return ("Zaglądasz za starą, zarośniętą mchem kapliczkę na skraju wsi.\nWśród zgniłych liści leży nadpalona, drewniana figurka...\nWygląda jak prymitywny talizman ochronny. Należy do kogoś, komu spłonął dom.", 
            [("Zabierz nadpalony talizman (Dowód)", "CLUE_TOTEM"), ("Zostaw to", "LEAVE")])

def get_soltys_dialogue():
    if clues_found["zaufanie_soltysa"]:
        return ("Sołtys Bieniasz: Dałem ci słowo, wziąłem zapłatę, a ty zrób swoje.\nIdź do Zielarki. Powiedz, że ja cię przysłałem.", 
                [("Odejdź", "LEAVE")])
    if clues_found["znaleziono_totem"]:
        return ("Sołtys Bieniasz: Czego znowu... Skąd to masz?! To... talizman Marii.\nDobra, widzę, że węszyć nie przestaniesz. To nie były wilki, panie Drozd.\nAle darmowej wiedzy tu nie ma. Zapłać mi za fatygę i milczenie przed gminą.", 
                [("Przekup Sołtysa (5 zł)", "PAY_SOLTYS"), ("Zostaw go", "LEAVE")])
    return ("Sołtys Bieniasz: Czego tu szukasz, miastowy? Mówiłem milicji:\nWilki zjadły małego, to wielka tragedia. Koniec kropka.\nNie wtykaj nosa w nieswoje sprawy.", 
            [("Wrócę, gdy znajdę dowód, że kłamiecie.", "LEAVE")])

def get_zielarka_dialogue():
    if clues_found["zaufanie_zielarki"]:
        return ("Zielarka: Las wszystko widział, las wszystko pamięta...\nIdź do spalonej chaty. Przeszukaj piec chlebowy, a odnajdziesz prawdę.", 
                [("Odejdź", "LEAVE")])
    if clues_found["zaufanie_soltysa"]:
        return ("Zielarka: Bieniasz cię przysłał? Głupiec... Ale widzę, że masz talizman Marii.\nDuchy nie przemówią jednak za darmo. Złóż ofiarę dla mieszkańców lasu,\na wskażę ci, czego szukać w ruinach.", 
                [("Zapłać za wskazówkę (5 zł)", "PAY_ZIELARKA"), ("Odejdź", "LEAVE")])
    return ("Zielarka: Czuję od ciebie smród miasta i niewiary. Jesteś ślepy.\nUdowodnij najpierw, że w ogóle tutejsi chcą z tobą gadać.\nBez błogosławieństwa Sołtysa nic ci nie powiem.", 
            [("Wyjdź z namiotu", "LEAVE")])

def get_ruiny_dialogue():
    if clues_found["zaufanie_zielarki"] and not clues_found["dowod_kosci"]:
        return ("Rozgarniasz popiół w głębi spalonego pieca tak, jak mówiła Zielarka.\nZnajdujesz drobne, zwęglone kości... Ale ich budowa jest nienaturalna.\nKształt czaszki, proporcje kończyn... To nie było ludzkie niemowlę.\nKtokolwiek tu spłonął, nie był człowiekiem.", 
                [("Zabezpiecz dowód (Prawdziwe kości z pieca)", "CLUE_KOSCI")])
    elif clues_found["dowod_kosci"]:
        return ("Spalona chata Marii. Masz już dowód. Czas porozmawiać z księdzem.", 
                [("Odejdź", "LEAVE")])
    return ("Osmalone ściany potęgują odór dawnego pożaru. Domostwo zamieniło się w ruinę.\nSterta gruzu jest zbyt duża, by ją przeszukać bez dokładnej wskazówki.\nMusisz wypytać lokalnych mieszkańców, czego tu właściwie szukać.", 
            [("Odejdź, by zebrać informacje", "LEAVE")])

def get_ksiadz_dialogue():
    if clues_found["rozmowa_maria"]:
        return ("Maria (trzęsąc się): Mamuna uciekła do Głębokiego Lasu za wsią...\nZabrała moje prawdziwe dziecko, a tego potwora spaliłam w piecu!\nBłagam cię, Drozd... znajdź to przeklęte leże i pomścij mnie.", 
                [("Wyrusz z bronią do Głębokiego Lasu", "GO_TO_FOREST"), ("Daj mi chwilę", "LEAVE")])
    if clues_found["dowod_kosci"]:
        return ("Ksiądz Proboszcz: Znalazłeś kości odmieńca. Więc to wszystko prawda...\nMaria wcale nie oszalała z żalu. Ukryłem ją u siebie na plebanii.\nPorozmawiaj z nią. Może wskaże ci drogę do leśnego leża Mamuny.", 
                [("Podejdź i porozmawiaj z Marią", "TALK_MARIA")])
    else:
        return ("Ksiądz Proboszcz: Szczęść Boże, przybyszu. Wioska skrywa wielki mrok.\nNie do mnie jednak należy łamanie tajemnicy milczenia sąsiadów.\nZdobądź ich zaufanie, przeszukaj okolicę. Wtedy wyjawię ci bolesną prawdę.", 
                [("Wrócę, gdy dowiem się więcej.", "LEAVE")])

def get_bed_dialogue():
    return ("To twoje posłanie w starej chacie po Mikołaju.\nChcesz odpocząć i zregenerować siły przed trudami śledztwa?", 
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

# Wygenerowanie gęstego lasu do Mapy 2
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

intro_step = 0
intro_sequence = [
    {"title": "Wnętrze Żuka. Czuć benzynę.", "text": "Kierowca Władek: Mówię ci, panie Drozd. W Chołach to się porobiło niezłe bagno.\nDzieciaka w lesie znaleźli... rozszarpanego. Oficjalnie ponoć wilki."},
    {"title": "Droga błotnista, pełna cieni.", "text": "Władek: Ale baby we wsi swoje wiedzą. Coś tu śmierdzi kłamstwem.\nJako psycholog powinieneś pogadać z ludźmi. Zmusić ich do gadania, pokazać, że nie odpuścisz.\nMasz 10 złotych, czasem łapówka rozwiązuje język. Ja stąd spadam."}
]

transition_step = 0
transition_sequence = [
    {"title": "Na skraju lasu...", "text": "Drozd zostawia wieś za plecami i z bronią w ręku wkracza w gęstwinę.\nJako psycholog zawsze szukał racjonalnego wytłumaczenia świata. Ale po tym,\nco zobaczył w piecu i usłyszał od Marii, wie jedno..."},
    {"title": "Głęboki Las (Leże Mamuny)", "text": "To, co czai się w głębi kniei, nie jest tylko zrodzone z obłędu.\nDemoniczne byty, o których opowiadali wieśniacy, istnieją tu w formie fizycznej.\nCzas wyciągnąć broń i na własne oczy ujrzeć legendę..."}
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
    clock.tick(60)
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
            
            elif current_map == "FOREST":
                for m in monster_triggers_forest:
                    if not m["beaten"] and m["rect"].collidepoint(player_pos.x, player_pos.y):
                        active_boss_type = m["type"]
                        
                        # ZDARZENIE SPECJALNE: Wybór moralny Mamuny
                        if active_boss_type == BOSS_MAMUNA and not clues_found["mamuna_rozmowa"]:
                            current_state = STATE_DIALOGUE
                            dialogue_title = "Leże Mamuny - Konfrontacja"
                            dialogue_lines = [
                                "Z mroku wyłania się przerażająca sylwetka... jednak potwór jest dziwnie spokojny.",
                                "Mamuna z czułością gładzi owinięte w szmaty ludzkie niemowlę po główce...\n",
                                "Mamuna: Stój, łowco! Dlaczego chcesz mu to odebrać? Ta samica wcale go nie chciała,",
                                "spaliła w piecu moje rodzone... A to maleństwo pokochałam jak własne!",
                                "Zostaw nas w spokoju i pozwól mi je odchować, a las nigdy więcej was nie skrzywdzi."
                            ]
                            dialogue_choices = [
                                ("Milcz, potworze! Oddaj dziecko i giń z moich rąk!", "FIGHT_MAMUNA"),
                                ("Opuść broń. (Zostaw dziecko pod opieką Mamuny)", "SPARE_MAMUNA")
                            ]
                            current_choice_idx = 0
                            clues_found["mamuna_rozmowa"] = True
                            player_pos.y += 20 # Wycofanie krok w dół
                            break
                        else:
                            # Standardowa walka z pomiotami
                            current_state = STATE_DICE_ROLL
                            p_d1, p_d2 = random.randint(1,6), random.randint(1,6)
                            m_d1, m_d2 = random.randint(1,6), random.randint(1,6)
                            mod_attack, mod_stamina = (p_d1 + p_d2) - 6, (p_d1 + p_d2) // 2
                            boss_mod_attack, boss_mod_stamina = (m_d1 + m_d2) - 6, (m_d1 + m_d2) // 2
                            boss_hp = boss_max_hp = 100 + (boss_mod_stamina * 5)
                            break
                
                # Zwykłe zwycięstwo po wybiciu wszystkich
                if all(m["beaten"] for m in monster_triggers_forest):
                    end_message = "Mamuna padła martwa. Odzyskałeś skradzione dziecko...\nJednak w jego maleńkich oczach widać było już mroczną dzikość lasu.\nZło zostało wyplenione, ale brzemię tej nocy pozostanie w tobie na zawsze."
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
            for m in monster_triggers_forest:
                if m["type"] == active_boss_type: m["beaten"] = True
            current_state = STATE_EXPLORE
            combat_projectiles.clear()
            combat_bullets.clear()
        elif player_hp <= 0:
            end_message = "Ciało Drozda dołączyło do rosnącej listy ofiar Przeklętego Lasu..."
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
                        current_map = "FOREST"
                        current_state = STATE_EXPLORE
                        player_pos = pygame.Vector2(WIDTH//2, HEIGHT - 100)

            elif current_state == STATE_DIALOGUE:
                if event.key in [pygame.K_w, pygame.K_UP]: current_choice_idx = (current_choice_idx - 1) % len(dialogue_choices)
                elif event.key in [pygame.K_s, pygame.K_DOWN]: current_choice_idx = (current_choice_idx + 1) % len(dialogue_choices)
                elif event.key in [pygame.K_RETURN, pygame.K_e]:
                    c_code = dialogue_choices[current_choice_idx][1]
                    
                    if c_code == "CLUE_TOTEM": clues_found["znaleziono_totem"] = True
                    elif c_code.startswith("PAY_"):
                        cost = 5
                        if player_money >= cost:
                            player_money -= cost
                            if c_code == "PAY_SOLTYS": clues_found["zaufanie_soltysa"] = True
                            elif c_code == "PAY_ZIELARKA": clues_found["zaufanie_zielarki"] = True
                        else:
                            dialogue_title = "Brak gotówki"
                            dialogue_lines = ["Drozd przeszukuje kieszenie. Brakuje mu pieniędzy na zapłatę..."]
                            dialogue_choices = [("Odejdź...", "LEAVE")]
                            current_choice_idx = 0
                            continue

                    elif c_code == "CLUE_KOSCI": clues_found["dowod_kosci"] = True
                    elif c_code == "SLEEP": player_hp = player_max_hp
                    
                    elif c_code == "TALK_MARIA":
                        clues_found["rozmowa_maria"] = True
                        dialogue_title = "Plebania - Rozmowa z Marią"
                        t, c = get_ksiadz_dialogue()
                        dialogue_lines, dialogue_choices = [t], c
                        current_choice_idx = 0
                        continue

                    elif c_code == "GO_TO_FOREST":
                        current_state = STATE_TRANSITION
                        continue
                    
                    # Logika dla wyboru finałowego Mamuny
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
                        end_message = "Drozd opuścił las, zostawiając dziecko istocie, która być może kochała je bardziej\nniż biologiczna matka... Mroczna tajemnica Chołów połączyła dwa światy na zawsze."
                        current_state = STATE_END
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
        screen.fill((10, 15, 12))
        title_surf = font_title.render(transition_sequence[transition_step]["title"], True, (120, 180, 120))
        screen.blit(title_surf, (80, HEIGHT - 180))
        for idx, l in enumerate(transition_sequence[transition_step]["text"].split('\n')):
            screen.blit(font_main.render(l, True, (200, 210, 200)), (80, HEIGHT - 130 + idx*30))

    elif current_state in [STATE_EXPLORE, STATE_DICE_ROLL]:
        if current_map == "VILLAGE":
            screen.blit(terrain_surface, (0, 0))
            for tx, ty in decorations_trees: draw_tree(screen, tx, ty)
            draw_well(screen, int(well_pos.x), int(well_pos.y))
            for h in houses: draw_slavic_house(screen, h.rect.x, h.rect.y, h.rect.width, h.rect.height, h.roof_color, h.ruined)
            for sx, sy in village_shadows: draw_monster_shadow(screen, sx, sy, anim_tick)
            
            draw_drozd(screen, int(player_pos.x) - 15, int(player_pos.y) - 20)
            
            pygame.draw.rect(screen, (20, 20, 25), (10, 10, 420, 105))
            pygame.draw.rect(screen, (120, 100, 70), (10, 10, 420, 105), 2)
            screen.blit(font_sub.render("Śledztwo w Chołach (Wymaga zaufania)", True, (200, 180, 140)), (20, 15))
            screen.blit(font_sub.render(f"1. Zbadaj poszlaki: {'[OK]' if clues_found['znaleziono_totem'] else '[ ]'}", True, (200, 200, 200)), (20, 40))
            screen.blit(font_sub.render(f"2. Przekup Sołtysa: {'[OK]' if clues_found['zaufanie_soltysa'] else '[ ]'}", True, (200, 200, 200)), (20, 60))
            screen.blit(font_sub.render(f"3. Ofiara u Zielarki: {'[OK]' if clues_found['zaufanie_zielarki'] else '[ ]'}", True, (200, 200, 200)), (20, 80))
            screen.blit(font_sub.render(f"4. Przeszukaj Ruiny: {'[OK]' if clues_found['dowod_kosci'] else '[ ]'}", True, (240, 200, 200)), (220, 40))
            screen.blit(font_sub.render(f"Gotówka Drozda: {player_money} zł", True, (150, 255, 150)), (220, 60))
            
        elif current_map == "FOREST":
            screen.fill((15, 22, 18)) # Ciemnozielony mrok lasu
            
            # Polana w środku
            pygame.draw.circle(screen, (25, 30, 22), (WIDTH//2, HEIGHT//2), 160)
            pygame.draw.circle(screen, (40, 25, 20), (WIDTH//2, HEIGHT//2), 60) # Centralne krwawe zarośla

            # Rysowanie wygenerowanego lasu z zachowaniem głębi
            for tx, ty in forest_trees: draw_tree(screen, tx, ty)
            
            for m in monster_triggers_forest:
                if not m["beaten"]:
                    pygame.draw.circle(screen, (20, 10, 10), (m["rect"].x + 30, m["rect"].y + 30), 40)
                    if m["type"] == BOSS_LATARNIK: draw_monster_latarnik(screen, m["rect"].x, m["rect"].y, anim_tick)
                    elif m["type"] == BOSS_PIEN: draw_monster_pien(screen, m["rect"].x, m["rect"].y)
                    elif m["type"] == BOSS_MAMUNA: draw_monster_mamuna(screen, m["rect"].x, m["rect"].y, anim_tick)
                    elif m["type"] == BOSS_KRZYKACZ: draw_monster_krzykacz(screen, m["rect"].x, m["rect"].y, anim_tick)
            
            draw_drozd(screen, int(player_pos.x) - 15, int(player_pos.y) - 20)
            
            pygame.draw.rect(screen, (20, 25, 20), (10, 10, 310, 50))
            pygame.draw.rect(screen, (80, 120, 70), (10, 10, 310, 50), 2)
            screen.blit(font_sub.render("Głęboki Las: Rozwiąż sprawę", True, (150, 255, 150)), (20, 20))

        if current_state == STATE_DICE_ROLL:
            pygame.draw.rect(screen, (10, 10, 15), (150, 180, WIDTH-300, 350))
            pygame.draw.rect(screen, (220, 50, 50), (150, 180, WIDTH-300, 350), 3)
            title = font_main.render(f"ZASADZKA BESTII: {active_boss_type}", True, (255, 50, 50))
            screen.blit(title, (WIDTH//2 - title.get_width()//2, 210))
            screen.blit(font_main.render(f"Twój Atak ({mod_attack:+d}), Witalność Bestii ({mod_stamina:+d})", True, (100, 255, 100)), (200, 290))
            screen.blit(font_main.render("NACIŚNIJ [ENTER], ABY OTWORZYĆ OGIEŃ", True, (255, 255, 255)), (WIDTH//2 - 200, 450))

    elif current_state in [STATE_HOUSE, STATE_DIALOGUE]:
        screen.fill((25, 20, 15)) 
        pygame.draw.rect(screen, (45, 35, 25), (50, 50, WIDTH-100, HEIGHT-100), 8) 
        if active_house and active_house.ruined:
            pygame.draw.rect(screen, (30, 25, 25), (WIDTH//2 - 50, HEIGHT//2 - 40, 100, 80))
            pygame.draw.circle(screen, (10, 10, 10), (WIDTH//2, HEIGHT//2), 30)
        else:
            pygame.draw.rect(screen, (70, 50, 35), (WIDTH//2 - 40, HEIGHT//2 - 20, 80, 50))
            pygame.draw.circle(screen, (200, 150, 120), (WIDTH//2, HEIGHT//2 - 60), 10)
        draw_drozd(screen, int(player_pos.x) - 15, int(player_pos.y) - 20)
        
        if current_state == STATE_DIALOGUE:
            pygame.draw.rect(screen, (15, 12, 10), (50, 430, WIDTH-100, 240))
            pygame.draw.rect(screen, (140, 110, 80), (50, 430, WIDTH-100, 240), 4)
            screen.blit(font_main.render(dialogue_title, True, (255, 215, 0)), (80, 445))
            
            # Bezpieczne renderowanie tekstu dialogu
            for dialog_line in dialogue_lines:
                for idx, l in enumerate(dialog_line.split('\n')):
                    screen.blit(font_sub.render(l, True, (230, 220, 210)), (80, 480 + idx*22))
            
            for idx, choice in enumerate(dialogue_choices):
                color = (255, 255, 100) if idx == current_choice_idx else (140, 140, 140)
                screen.blit(font_sub.render((" > " if idx == current_choice_idx else "   ") + choice[0], True, color), (80, 580 + idx * 25))

    elif current_state == STATE_COMBAT:
        screen.fill((15, 20, 15)) # Tło walki pasujące do lasu
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
        screen.blit(title_surf, (WIDTH//2 - title_surf.get_width()//2, HEIGHT//2 - 80))
        
        # Wielolinijkowe renderowanie wiadomości końcowej
        for idx, line in enumerate(end_message.split('\n')):
            msg_surf = font_sub.render(line, True, (220, 220, 200))
            screen.blit(msg_surf, (WIDTH//2 - msg_surf.get_width()//2, HEIGHT//2 - 20 + idx*30))
            
        exit_surf = font_sub.render("[ Wciśnij ESC, aby zamknąć ]", True, (100, 100, 100))
        screen.blit(exit_surf, (WIDTH//2 - exit_surf.get_width()//2, HEIGHT - 100))

    pygame.display.flip()

pygame.quit()
sys.exit()
