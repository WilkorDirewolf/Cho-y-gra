import pygame
import sys
import random
import math
import numpy as np

# --- INICJALIZACJA DŹWIĘKU I PYGAME ---
pygame.mixer.pre_init(44100, -16, 2, 1024)
pygame.init()
pygame.mixer.init()

# Konfiguracja okna
WIDTH, HEIGHT = 950, 700
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Krzykacz: Polowanie na Mamunę - Mroczna Baśń")
clock = pygame.time.Clock()

# --- PROCEDURALNY GENERATOR MUZYKI ---
def generate_slavic_theme():
    sample_rate = 44100
    notes = {
        'D3': 146.83, 'E3': 164.81, 'F3': 174.61, 'G3': 196.00,
        'A3': 220.00, 'C4': 261.63, 'D4': 293.66, 'E4': 329.63, 'F4': 349.23,
        'rest': 0.0
    }

    melody = [
        ('D4', 0.2), ('D4', 0.2), ('F4', 0.2), ('E4', 0.2), 
        ('D4', 0.2), ('C4', 0.2), ('A3', 0.4),
        ('D4', 0.2), ('D4', 0.2), ('F4', 0.2), ('E4', 0.2), 
        ('G3', 0.2), ('A3', 0.2), ('D3', 0.4),
        ('F4', 0.2), ('E4', 0.2), ('D4', 0.2), ('C4', 0.2), 
        ('D4', 0.1), ('E4', 0.1), ('F4', 0.2), ('A3', 0.4),
        ('C4', 0.2), ('A3', 0.2), ('G3', 0.2), ('F3', 0.2), 
        ('E3', 0.2), ('C4', 0.2), ('D3', 0.4)
    ] * 2

    total_samples = sum(int(sample_rate * dur) for _, dur in melody)
    total_duration = total_samples / sample_rate
    track = np.zeros(total_samples)

    current_sample = 0
    for note_name, duration in melody:
        samples = int(sample_rate * duration)
        if note_name != 'rest':
            freq = notes[note_name]
            t = np.linspace(0, duration, samples, False)
            wave = 0.5 * (2 * ((t * freq) - np.floor((t * freq) + 0.5)))
            wave += 0.3 * np.sign(np.sin(2 * np.pi * freq * t)) 
            
            env = np.ones_like(t)
            attack, decay, release = int(sample_rate * 0.015), int(sample_rate * 0.08), int(sample_rate * 0.05)
            
            if samples > attack + release:
                env[:attack] = np.linspace(0, 1, attack)
                env[-release:] = np.linspace(1, 0, release)
                if samples > attack + decay + release:
                    env[attack:attack+decay] = np.linspace(1, 0.6, decay)
                    env[attack+decay:-release] = 0.6

            track[current_sample:current_sample+samples] += wave * env * 0.45

        current_sample += samples

    t_total = np.linspace(0, total_duration, total_samples, False)
    bass_track = np.zeros(total_samples)
    beat_interval = 0.4
    num_beats = int(total_duration / beat_interval)
    
    for i in range(num_beats):
        beat_start = int(i * beat_interval * sample_rate)
        beat_end = int(beat_start + 0.15 * sample_rate)
        if beat_end < total_samples:
            t_beat = t_total[beat_start:beat_end] - t_total[beat_start]
            kick_freq = np.linspace(150, 40, len(t_beat))
            kick = np.sin(2 * np.pi * kick_freq * t_beat)
            kick_env = np.linspace(1, 0, len(t_beat)) ** 2
            bass_track[beat_start:beat_end] += kick * kick_env * 0.9

    track += bass_track
    track = np.clip(track, -1.0, 1.0)
    track_16bit = np.int16(track * 32767)
    return np.column_stack((track_16bit, track_16bit))

print("Generowanie skocznej, folkowej ścieżki dźwiękowej... (To może potrwać sekundę)")
audio_data = generate_slavic_theme()
slavic_sound = pygame.sndarray.make_sound(audio_data)
slavic_sound.set_volume(0.25)
slavic_sound.play(loops=-1, fade_ms=500)
print("Zaczynamy słowiański rejwach!")

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

def draw_soltys(surface, x, y):
    pygame.draw.rect(surface, (60, 50, 40), (x - 12, y + 15, 24, 25))
    pygame.draw.circle(surface, (230, 190, 170), (x, y + 10), 10)
    pygame.draw.rect(surface, (40, 30, 20), (x - 12, y + 40, 10, 15))
    pygame.draw.rect(surface, (40, 30, 20), (x + 2, y + 40, 10, 15))
    pygame.draw.polygon(surface, (30, 30, 30), [(x - 15, y + 3), (x + 15, y + 3), (x, y - 8)])

def draw_zielarka(surface, x, y):
    pygame.draw.polygon(surface, (50, 70, 50), [(x, y - 5), (x - 18, y + 40), (x + 18, y + 40)])
    pygame.draw.circle(surface, (200, 160, 140), (x, y + 5), 8)
    pygame.draw.line(surface, (90, 60, 30), (x + 15, y + 10), (x + 15, y + 45), 3)

def draw_maciek(surface, x, y):
    pygame.draw.rect(surface, (60, 50, 40), (x - 12, y + 15, 24, 25))
    pygame.draw.circle(surface, (230, 190, 160), (x, y + 10), 9)
    pygame.draw.line(surface, (20, 10, 10), (x - 6, y + 6), (x - 2, y + 8), 2)
    pygame.draw.line(surface, (20, 10, 10), (x + 6, y + 6), (x + 2, y + 8), 2)
    pygame.draw.rect(surface, (40, 30, 20), (x - 5, y + 15, 10, 5))

def draw_maria(surface, x, y):
    pygame.draw.polygon(surface, (100, 40, 40), [(x, y + 5), (x - 12, y + 35), (x + 12, y + 35)])
    pygame.draw.circle(surface, (220, 180, 160), (x, y + 5), 8)
    pygame.draw.arc(surface, (40, 20, 10), (x - 10, y - 5, 20, 20), 0, 3.14, 4)

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

def draw_zuk(surface, x, y, light=True):
    s = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
    if light:
        pygame.draw.polygon(s, (255, 255, 150, 50), [(x+130, y+30), (x+450, y-20), (x+450, y+80)])
    surface.blit(s, (0,0))
    pygame.draw.rect(surface, (80, 100, 110), (x, y, 140, 50), border_radius=8)
    pygame.draw.rect(surface, (70, 90, 100), (x, y, 80, 50)) 
    for i in range(int(x)+5, int(x)+80, 10):
        pygame.draw.line(surface, (60, 80, 90), (i, y+5), (i, y+45), 2)
    pygame.draw.rect(surface, (30, 40, 50), (x + 95, y + 8, 30, 18), border_radius=3)
    pygame.draw.rect(surface, (30, 40, 50), (x + 70, y + 8, 20, 18), border_radius=2)
    pygame.draw.circle(surface, (20, 20, 20), (x + 30, y + 50), 16)
    pygame.draw.circle(surface, (120, 120, 120), (x + 30, y + 50), 6)
    pygame.draw.circle(surface, (20, 20, 20), (x + 110, y + 50), 16)
    pygame.draw.circle(surface, (120, 120, 120), (x + 110, y + 50), 6)
    pygame.draw.circle(surface, (255, 255, 200), (x + 138, y + 30), 6)
    pygame.draw.rect(surface, (40, 40, 40), (x + 130, y + 40, 15, 8), border_radius=2)

def draw_text_wrapped(surface, text, font, color, x, y, max_width):
    paragraphs = text.split('\n')
    y_offset = 0
    font_height = font.size('Tg')[1]
    
    for paragraph in paragraphs:
        words = paragraph.split(' ')
        line = []
        for word in words:
            test_line = ' '.join(line + [word])
            width, _ = font.size(test_line)
            if width <= max_width:
                line.append(word)
            else:
                text_surface = font.render(' '.join(line), True, color)
                surface.blit(text_surface, (x, y + y_offset))
                y_offset += font_height + 2
                line = [word]
        if line:
            text_surface = font.render(' '.join(line), True, color)
            surface.blit(text_surface, (x, y + y_offset))
            y_offset += font_height + 2
            
    return y_offset

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
        self.type = type_id
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

# --- NOWE STATYSTYKI GRACZA ---
player_agility = 3    
player_charisma = 2   

# --- DANE FABULARNE Z NOWĄ ŚCIEŻKĄ ---
clues_found = {
    "znaleziono_totem": False, 
    "zaufanie_soltysa": False, 
    "zaufanie_zielarki": False, 
    "dowod_kosci": False,
    "ma_upowaznienie_maciek": False,
    "wiedza_o_mamunie": False,       
    "mamuna_rozmowa": False,
    "mamuna_zalatwiona": False,
    "ruiny_skarb": False,
    "z_lusia": False,
    "spotkal_dziadka": False,
    "zardzewialy_sztylet": False,
    "ma_amulet_zielarki": False,
    "wspolpraca_z_lusia": False,
    "rozmowa_pien": False,
    "rozmowa_gawron": False,
    "rozmowa_skrzekacz": False,
    "rozmowa_latarnik": False,
    "podslyszano_soltysa": False,
    "klamstwo_zielarka_sukces": False,
    "klamstwo_zielarka_porazka": False,
    "zna_sekretny_schowek": False
}

def get_kapliczka_dialogue():
    if clues_found["zardzewialy_sztylet"]: return ("Stara kapliczka. Zabrałeś stąd już wszystko.", [("Odejdź", "LEAVE")])
    return ("Pod deskami starej kapliczki znajdujesz przedziwny artefakt...\nTo Zardzewiały Sztylet, emanujący chłodem.", 
            [("Zabierz sztylet", "CLUE_DAGGER"), ("Zostaw go", "LEAVE")])

def get_soltys_dialogue():
    if clues_found["zaufanie_soltysa"]: 
        return ("Sołtys: Idź do Zielarki. Powiedz, że ja cię przysłałem.", [("Odejdź", "LEAVE")])
    
    choices = [("Wybacz najście. (Odejdź)", "LEAVE")]
    if clues_found["zardzewialy_sztylet"]:
        choices.insert(0, ("Znalazłem ten zardzewiały sztylet. Co to znaczy?", "SHOW_DAGGER"))
    
    return ("Sołtys: Aha, pan jest tym doktorem z miasta? Będzie pan ludzi leczył? \nDrozd: Jestem doktorem psychologii... \nPhiii? Myślałem, że chociaż lekarza nam przysłali, bo starego Fiodora wilki zjadły...", choices)

def get_zielarka_dialogue():
    if clues_found["zaufanie_zielarki"]: 
        if clues_found["ma_amulet_zielarki"]:
            return ("Zielarka: Szukaj w spalonej chacie, głupcze.", [("Odejdź", "LEAVE")])
        return ("Zielarka: Użyj tego Amuletu przeciw demonom... [ZDOBYTO AMULET]", [("Schowaj amulet i odejdź", "CLUE_AMULET")])
    
    if clues_found["klamstwo_zielarka_porazka"]:
        return ("Zielarka: Wynoś się stąd, kłamco! Przejrzałam cię!", [("Odejdź (Zablokowana opcja)", "LEAVE")])
    
    choices = [("Odejdź", "LEAVE")]
    
    if clues_found["zaufanie_soltysa"]:
        choices.insert(0, ("Zapłać za wskazówkę (5 zł)", "PAY_ZIELARKA"))
        choices.insert(1, ("Skłam: 'Sołtys kazał ci wydać amulet za darmo.' (Test Charyzmy)", "TEST_CHARISMA_ZIELARKA"))
        return ("Zielarka: Bieniasz cię przysłał? Zapłać 5 zł, a wskażę ci ruinę.", choices)
        
    return ("Zielarka: Udowodnij najpierw, że tutejsi chcą z tobą gadać.", [("Wyjdź z namiotu", "LEAVE")])

def get_ruiny_dialogue():
    if clues_found.get("mamuna_zalatwiona", False) and not clues_found.get("ruiny_skarb", False):
        return ("Powracasz do spalonych ruin. W świetle księżyca dostrzegasz coś błyszczącego pod deską...", 
                [("Przeszukaj gruzy", "CLUE_RUINY_SKARB")])
    if clues_found["zaufanie_zielarki"] and not clues_found["dowod_kosci"]:
        return ("Rozgarniasz popiół w piecu. Znajdujesz zwęglone kości odmieńca...", 
                [("Zabezpiecz dowód", "CLUE_KOSCI")])
    elif clues_found["dowod_kosci"]: return ("Masz już dowód. Czas pokazać go Maćkowi pod Plebanią.", [("Odejdź", "LEAVE")])
    return ("Osmalone ściany potęgują odór dawnego pożaru.", [("Odejdź", "LEAVE")])

def get_plebania_dialogue():
    if clues_found["ma_upowaznienie_maciek"]:
        return ("Maciek: Błagam, jedź do Marii. Mój Żuk stoi na wschodnim skraju wsi.", [("Odejdź", "LEAVE")])
    if clues_found["dowod_kosci"]:
        return ("Maciek: Te kości... Więc to prawda! To nie ona spaliła nasze dziecko!\nWeź to upoważnienie i jedź do niej do szpitala w Choroszczy.", [("Weź upoważnienie", "GET_UPOWAZNIENIE")])
    return ("Przed plebanią siedzi Maciek.\nMaciek: Zostaw mnie... Moje dziecko nie żyje, a żonę zabrali do Choroszczy...", [("Wyjdź", "LEAVE")])

def get_zuk_dialogue():
    if clues_found["wiedza_o_mamunie"]:
        return ("Żuk jest gotowy do drogi, ale najpierw musisz zabić Mamunę w Lesie.", [("Odejdź", "LEAVE")])
    if clues_found["ma_upowaznienie_maciek"]:
        return ("Masz dokumenty od Maćka. Wsiadasz do Żuka, żeby odwiedzić Marię.", [("Jedź do Choroszczy", "GO_CHOROSZCZ"), ("Jeszcze nie", "LEAVE")])
    return ("Twój stary, wysłużony Żuk. Bez wyraźnego powodu nie ma sensu marnować paliwa.", [("Odejdź", "LEAVE")])

def get_bed_dialogue():
    if clues_found.get("mamuna_zalatwiona", False):
        return ("Czujesz dziwny, mroczny niepokój unoszący się nad Chołami...", [("Połóż się spać (Rozpocznij kolejny akt)", "TRIGGER_MOB_EVENT")])
    return ("Twoje posłanie w starej chacie po Mikołaju.", [("Prześpij się (Regeneracja HP i Poczytalności)", "SLEEP"), ("Wyjdź", "LEAVE")])

houses = [
    House(250, 60, 160, 110, "Dom Sołtysa Bieniasza", get_soltys_dialogue),
    House(140, 320, 130, 90, "Chata po starym Mikołaju", get_bed_dialogue),
    House(780, 80, 140, 100, "Namiot Starej Zielarki", get_zielarka_dialogue),
    House(720, 320, 150, 110, "Spalona Chata Marii", get_ruiny_dialogue, ruined=True),
    House(60, 480, 150, 130, "Plebania (Maciek)", get_plebania_dialogue, roof_color=(120, 40, 30)),
    House(420, 240, 80, 100, "Stara Kapliczka", get_kapliczka_dialogue, roof_color=(80, 80, 90)),
    House(780, 480, 140, 60, "Wóz (Żuk)", get_zuk_dialogue, roof_color=(80, 100, 110))
]

decorations_trees = [(40, 260), (50, 500), (360, 180), (280, 550), (660, 120), (690, 200), (880, 500), (900, 250)]
forest_trees = [(random.randint(-10, WIDTH-20), random.randint(-10, HEIGHT-20)) for _ in range(80)]

monster_triggers_forest = [
    {"rect": pygame.Rect(WIDTH//2 - 250, HEIGHT//2 - 200, 60, 60), "type": BOSS_LATARNIK, "beaten": False},
    {"rect": pygame.Rect(WIDTH//2 + 190, HEIGHT//2 - 200, 60, 60), "type": BOSS_PIEN, "beaten": False},
    {"rect": pygame.Rect(WIDTH//2 - 250, HEIGHT//2 + 150, 60, 60), "type": BOSS_KRZYKACZ_FOREST, "beaten": False},
    {"rect": pygame.Rect(WIDTH//2 - 30, HEIGHT//2 + 100, 60, 60), "type": BOSS_MAMUNA, "beaten": False}, 
    {"rect": pygame.Rect(WIDTH//2 - 50, HEIGHT//2 - 250, 60, 60), "type": BOSS_GAWRON, "beaten": False},
    {"rect": pygame.Rect(WIDTH//2 + 190, HEIGHT//2 + 150, 60, 60), "type": BOSS_SKRZEKACZ, "beaten": False} 
]

current_state = STATE_INTRO
anim_tick = 0
active_house = None 
player_pos = pygame.Vector2(215, 410) 
player_hp, player_max_hp = 100, 100
player_sanity, player_max_sanity = 100, 100
player_money = 10 
base_attack, mod_attack, mod_stamina = 10, 0, 0

active_boss_type = None
boss_hp, boss_max_hp = 100, 100
boss_mod_attack, boss_mod_stamina = 0, 0

latarnik_fatigue = 0
latarnik_max_fatigue = 40
latarnik_pos = pygame.Vector2(WIDTH//2, 200)

dialogue_title, dialogue_lines, dialogue_choices = "", [], []
current_choice_idx = 0

combat_projectiles, combat_bullets = [], []
combat_timer = 0
player_combat_pos = pygame.Vector2(WIDTH//2, HEIGHT//2 + 100)

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
    {"title": "Wnętrze Żuka. Siedzisz na śmierdzącym papierosami, wypierdzianym fotelu obok kierowcy, który wygląda, jak wyjęty żywcem z lat '50 partyzant Vietcongu.", "text": "Kierowca Władek: W Chołach babka spaliła dzieciaka w piecu, chore, co się dzieje z tym światem. Maciej nadal rozpacza, a Marię zabrali do Choroszczy..."},
    {"title": "Wioska Choły.", "text": "Porozmawiaj z ludźmi. Znajdź poszlaki. Rozwiąż sprawę. Strzeż swojego umysłu..."}
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
                
                if current_state == STATE_EXPLORE:
                    okno_soltysa = pygame.Rect(230, 90, 40, 40)
                    if okno_soltysa.collidepoint(player_pos.x, player_pos.y):
                        current_state = STATE_DIALOGUE
                        dialogue_title = "Ciemne Okno (Dom Sołtysa)"
                        if clues_found["podslyszano_soltysa"]:
                            dialogue_lines = ["Nic więcej nie usłyszysz. Wewnątrz panuje głucha cisza."]
                            dialogue_choices = [("Odejdź", "LEAVE_WINDOW")]
                        else:
                            dialogue_lines = ["Widzisz migoczące światło świecy. Słyszysz ściszone, nerwowe głosy.", "To Sołtys z kimś rozmawia. Ryzykujesz podsłuchiwanie?"]
                            dialogue_choices = [
                                ("Podsłuchuj (Test Zręczności)", "TEST_AGILITY_WINDOW"), 
                                ("Zostaw to, zbyt niebezpieczne", "LEAVE_WINDOW")
                            ]
                        current_choice_idx = 0
            
            elif current_map == "FOREST":
                for m in monster_triggers_forest:
                    if not m["beaten"] and m["rect"].collidepoint(player_pos.x, player_pos.y):
                        active_boss_type = m["type"]
                        
                        if active_boss_type == BOSS_MAMUNA:
                            if not clues_found["wiedza_o_mamunie"]:
                                player_sanity -= 15
                                current_state = STATE_DIALOGUE
                                dialogue_title = "Mgliste Mokradła"
                                dialogue_lines = ["Z mgły wyłania się przerażający byt. Twój umysł odrzuca ten widok! (-15 Poczytalności)", "Przeczuwasz, że bez odpowiedniej wiedzy ta walka to samobójstwo."]
                                dialogue_choices = [("Uciekaj!", "LEAVE")]
                                current_choice_idx = 0
                                player_pos.y += 40
                                break
                            elif not clues_found["mamuna_rozmowa"]:
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
            fire_rate = 40 if active_boss_type != BOSS_TRUE_KRZYKACZ else 25
            if combat_timer % fire_rate == 0:
                dx, dy = player_combat_pos.x - (WIDTH//2), player_combat_pos.y - 220
                dist = math.hypot(dx, dy) if math.hypot(dx, dy) != 0 else 1
                spd = 6 if active_boss_type != BOSS_TRUE_KRZYKACZ else 9
                color = (255, 60, 0) if active_boss_type != BOSS_TRUE_KRZYKACZ else (100, 0, 0)
                combat_projectiles.append(Projectile(WIDTH//2, 220, (dx/dist)*spd, (dy/dist)*spd, color, 10))
            
        if keys[pygame.K_SPACE] and combat_timer % 15 == 0:
            combat_bullets.append(Projectile(player_combat_pos.x, player_combat_pos.y, 0, -10, (255, 255, 255), 4))

        for b in combat_bullets:
            b.update()
            target_pos = latarnik_pos if active_boss_type == BOSS_LATARNIK else pygame.Vector2(WIDTH//2, 220)
            if pygame.Vector2(b.x, b.y).distance_to(target_pos) < 45:
                boss_hp -= max(1, base_attack + mod_attack)
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
                if active_boss_type == BOSS_LATARNIK and latarnik_fatigue < latarnik_max_fatigue:
                    latarnik_fatigue += 1
                combat_projectiles.remove(p)

        if active_boss_type == BOSS_TRUE_KRZYKACZ and player_hp < player_max_hp / 3:
            end_message = "Krzykacz ryczy przeraźliwie, podnosi cię potężnymi łapami...\nJego kościana szczęka jelenia zamyka się na twojej głowie.\nZostałeś pożarty. (GAME OVER)"
            current_state = STATE_END

        elif boss_hp <= 0:
            if active_boss_type == BOSS_TRUE_KRZYKACZ:
                end_message = "Zabiłeś Krzykacza. Prastara obrona lasu padła...\nDrwale z urzędu wkrótce zetną wszystko. Las umrze, ale Choły są bezpieczne."
                current_state = STATE_END
            elif active_boss_type == BOSS_MAMUNA:
                for m in monster_triggers_forest:
                    if m["type"] == active_boss_type: m["beaten"] = True
                current_state = STATE_DIALOGUE
                dialogue_title = "Zwycięstwo nad Mamuną"
                dialogue_lines = ["Mamuna z krzykiem rozpływa się w gąszczu...", "Czujesz ekstremalne zmęczenie. Lepiej wróć do wioski na odpoczynek."]
                dialogue_choices = [("Wróć do Chołów", "RETURN_TO_VILLAGE")]
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
                    player_pos = pygame.Vector2(WIDTH//2, HEIGHT - 30)

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
                    
                    if c_code == "LEAVE":
                        if current_map == "VILLAGE":
                            current_state = STATE_HOUSE
                            player_pos.y += 70 
                        else:
                            current_state = STATE_EXPLORE
                            player_pos.y += 20
                        continue
                        
                    elif c_code == "LEAVE_WINDOW":
                        current_state = STATE_EXPLORE
                        player_pos.x -= 30 
                        continue
                        
                    elif c_code == "TEST_AGILITY_WINDOW":
                        roll = random.randint(1, 6) + random.randint(1, 6) + player_agility
                        if roll >= 9:
                            clues_found["podslyszano_soltysa"] = True
                            clues_found["zna_sekretny_schowek"] = True
                            dialogue_title = "Zręczność: Sukces!"
                            dialogue_lines = [
                                f"Wynik: {roll}. Podkradłeś się bezszelestnie.",
                                "Słyszysz Sołtysa: 'Miastowy nie może znaleźć sztyletu w kapliczce. Las nas wtedy zje!'",
                                "Wiesz już, gdzie szukać!"
                            ]
                            dialogue_choices = [("Zanotuj w dzienniku", "LEAVE_WINDOW")]
                        else:
                            player_hp -= 15
                            dialogue_title = "Zręczność: Porażka!"
                            dialogue_lines = [
                                f"Wynik: {roll}. Nadepnąłeś na głośną gałąź!",
                                "Z domu wypada wściekły pies Sołtysa i boleśnie cię gryzie (-15 HP)."
                            ]
                            dialogue_choices = [("Uciekaj!", "LEAVE_WINDOW")]
                        current_choice_idx = 0
                        continue

                    elif c_code == "TEST_CHARISMA_ZIELARKA":
                        roll = random.randint(1, 6) + random.randint(1, 6) + player_charisma
                        if roll >= 9:
                            clues_found["zaufanie_zielarki"] = True
                            clues_found["klamstwo_zielarka_sukces"] = True
                            dialogue_title = "Charyzma: Sukces!"
                            dialogue_lines = [
                                f"Wynik: {roll}. Brzmiałeś niezwykle przekonująco i groźnie.",
                                "Zielarka kuli się: 'Dobrze, dobrze... Nie mów mu tylko, proszę.",
                                "Przeszukaj piec w spalonej chacie Marii...'"
                            ]
                            dialogue_choices = [("Dobrze (Zaoszczędzono 5 zł)", "LEAVE")]
                        else:
                            clues_found["klamstwo_zielarka_porazka"] = True
                            dialogue_title = "Charyzma: Porażka!"
                            dialogue_lines = [
                                f"Wynik: {roll}. Zawahałeś się.",
                                "Zielarka pluje ci pod nogi: 'Kłamiesz jak pies! Wynocha z mojego namiotu!'"
                            ]
                            dialogue_choices = [("Wycofaj się ze wstydu", "LEAVE")]
                        current_choice_idx = 0
                        continue

                    elif c_code == "CLUE_TOTEM": 
                        clues_found["znaleziono_totem"] = True
                        c_code = "LEAVE"
                        
                    elif c_code == "CLUE_DAGGER": 
                        clues_found["zardzewialy_sztylet"] = True
                        dialogue_title = "Zdobycz!"
                        dialogue_lines = ["Zabrałeś Zardzewiały Sztylet. Aż mrowi od niego w palcach..."]
                        dialogue_choices = [("Schowaj", "LEAVE")]
                        current_choice_idx = 0
                        continue
                        
                    elif c_code == "SHOW_DAGGER":
                        dialogue_title = "Zaufanie Sołtysa"
                        dialogue_lines = ["Sołtys blednie na widok ostrza.", "'Więc to prawda... Las się budzi. Idź do starej Zielarki.'"]
                        dialogue_choices = [("Dziękuję.", "TRUST_SOLTYS")]
                        current_choice_idx = 0
                        continue
                        
                    elif c_code == "TRUST_SOLTYS":
                        clues_found["zaufanie_soltysa"] = True
                        current_state = STATE_HOUSE
                        player_pos.y += 70
                        continue

                    elif c_code == "CLUE_AMULET": 
                        clues_found["ma_amulet_zielarki"] = True
                        current_state = STATE_EXPLORE
                        player_pos.y += 70
                        continue

                    elif c_code == "CLUE_RUINY_SKARB":
                        clues_found["ruiny_skarb"] = True
                        player_money += 20
                        base_attack += 5
                        dialogue_title = "Cenna Zdobycz!"
                        dialogue_lines = ["Znalazłeś porzuconą sakiewkę (+20 zł) oraz stary kamień szlifierski.", "Twoja broń zadaje teraz większe obrażenia (+5 Atak)!"]
                        dialogue_choices = [("Świetnie!", "LEAVE")]
                        current_choice_idx = 0
                        continue
                        
                    elif c_code and c_code.startswith("PAY_"):
                        if player_money >= 5:
                            player_money -= 5
                            if c_code == "PAY_ZIELARKA": 
                                clues_found["zaufanie_zielarki"] = True
                                dialogue_title = "Wiedza kupiona"
                                dialogue_lines = ["Zielarka chowa monety.", "'Przeszukaj piec w spalonej chacie Marii...'"]
                                dialogue_choices = [("Ruszaj", "LEAVE")]
                                current_choice_idx = 0
                                continue
                        else:
                            dialogue_lines = ["Nie masz wystarczająco złota..."]
                            dialogue_choices = [("Odejdź...", "LEAVE")]
                            current_choice_idx = 0
                            continue
                            
                    elif c_code == "CLUE_KOSCI": 
                        clues_found["dowod_kosci"] = True
                        player_sanity -= 20
                        dialogue_title = "Makabryczne Odkrycie"
                        dialogue_lines = ["Zabezpieczasz nadpalone kości odmieńca. Zrobiło ci się słabo... (-20 Poczytalności)", "Pokaż to jako dowód Maćkowi."]
                        dialogue_choices = [("Schowaj do torby", "LEAVE")]
                        current_choice_idx = 0
                        continue

                    elif c_code == "GET_UPOWAZNIENIE":
                        clues_found["ma_upowaznienie_maciek"] = True
                        dialogue_title = "Zdobyto dokument!"
                        dialogue_lines = ["Otrzymałeś upoważnienie. Możesz teraz pojechać swoim Żukiem do Choroszczy."]
                        dialogue_choices = [("Odejdź", "LEAVE")]
                        current_choice_idx = 0
                        continue

                    elif c_code == "GO_CHOROSZCZ":
                        dialogue_title = "Szpital w Choroszczy"
                        dialogue_lines = [
                            "Pokazujesz upoważnienie od Maćka. Pielęgniarz wpuszcza cię na oddział zamknięty.",
                            "Maria: 'To nie była zwykła choroba... To Mamuna! A to dziecko... to był Odmieniec.'",
                            "Maria: 'Błagam, pomścij mnie. Mamuna tworzy iluzje – ignoruj je i celuj w jej prawdziwe ciało!'"
                        ]
                        dialogue_choices = [("Przyjmuję to zadanie. (Wróć do Chołów)", "RETURN_FROM_CHOROSZCZ")]
                        current_choice_idx = 0
                        continue

                    elif c_code == "RETURN_FROM_CHOROSZCZ":
                        clues_found["wiedza_o_mamunie"] = True
                        current_state = STATE_EXPLORE
                        player_pos.y += 30
                        continue

                    elif c_code == "TRIGGER_MOB_EVENT":
                        dialogue_title = "Środek Nocy - Bunt!"
                        dialogue_lines = [
                            "Nagle budzi cię ostre szarpanie! To Lusia.",
                            "Lusia: 'Drozd, wstawaj! Sołtys i inni dowiedzieli się o twoich spacerach",
                            "w lesie... Zebrali chłopów z widłami i pochodniami, idą cię spalić!'",
                            "Słyszysz okrzyki z zewnątrz. 'Znam bezpieczne miejsce, chodź ze mną!'"
                        ]
                        dialogue_choices = [
                            ("Zaakceptuj pomoc Lusi (Teleport do Jądra Lasu)", "MOB_LUSIA_HELP"),
                            ("Odrzuć pomoc i uciekaj do lasu oknem (Test Zręczności)", "MOB_ESCAPE_FOREST"),
                            ("Biegnij z całych sił do Żuka! (Test Zręczności)", "MOB_ESCAPE_CAR")
                        ]
                        current_choice_idx = 0
                        continue

                    elif c_code == "MOB_LUSIA_HELP":
                        clues_found["wspolpraca_z_lusia"] = True
                        dialogue_title = "Teleportacja"
                        dialogue_lines = ["Lusia chwyta cię za ramię. Zanim drzwi wyważają chłopi z pochodniami, świat wiruje!"]
                        dialogue_choices = [("Rozejrzyj się", "GO_TO_STRANGE_PLACE_FROM_MOB")]
                        current_choice_idx = 0
                        continue

                    elif c_code == "MOB_ESCAPE_FOREST":
                        roll = random.randint(1, 6) + random.randint(1, 6) + player_agility
                        if roll >= 7:
                            dialogue_title = "Zręczność: Sukces!"
                            dialogue_lines = ["Wyskoczyłeś oknem na tyłach, zaledwie sekundy przed wdarciem się tłumu.", "Biegniesz prosto w najciemniejszy mrok lasu..."]
                            dialogue_choices = [("Biegnij dalej", "MEET_DZIADEK_DIALOGUE")]
                            current_choice_idx = 0
                        else:
                            end_message = f"Wynik Zręczności: {roll} (Porażka!).\nPotknąłeś się o próg izby. Rozwścieczony tłum z Sołtysem na czele wyciągnął cię z chaty.\nZostałeś zlinczowany. (GAME OVER)"
                            current_state = STATE_END
                        continue

                    elif c_code == "MOB_ESCAPE_CAR":
                        roll = random.randint(1, 6) + random.randint(1, 6) + player_agility
                        if roll >= 8:
                            end_message = f"Wynik Zręczności: {roll} (Ekstremalny Sukces!).\nDopadasz Żuka, błyskawicznie zwierasz kable pod kierownicą i odjeżdżasz z piskiem opon.\nUdało ci się wrócić do Wrocławia i ocalić skórę. (ZAKOŃCZENIE: TCHÓRZLIWA UCIECZKA)"
                            current_state = STATE_END
                        else:
                            end_message = f"Wynik Zręczności: {roll} (Porażka!).\nStary silnik Żuka po prostu odmówił posłuszeństwa. Tłum rozbił szyby i...\nZostałeś zlinczowany we wrakach maszyny. (GAME OVER)"
                            current_state = STATE_END
                        continue

                    elif c_code == "MEET_DZIADEK_DIALOGUE":
                        dialogue_title = "Spotkanie w gąszczu"
                        dialogue_lines = [
                            "Wpadasz w gęstwinę i zderzasz się z potężną, drewnianą istotą.",
                            "Leśny Dziadek obraca się gniewnie: 'Intruz! Kolejny człowiek! Kim jesteś?!'"
                        ]
                        dialogue_choices = [
                            ("Jestem Drozd, człowiek z miasta! (Prawda)", "DZIADEK_TRUTH"),
                            ("Jestem demonem-łowcą! (Kłamstwo - Test Charyzmy)", "DZIADEK_LIE")
                        ]
                        current_choice_idx = 0
                        continue

                    elif c_code == "DZIADEK_TRUTH":
                        end_message = "Leśny Dziadek ryczy obnażając kły.\nOplata cię grubymi pnączami i zgniata jak gałązkę. Umierasz. (GAME OVER)"
                        current_state = STATE_END
                        continue

                    elif c_code == "DZIADEK_LIE":
                        roll = random.randint(1, 6) + random.randint(1, 6) + player_charisma
                        if roll >= 7:
                            dialogue_title = "Charyzma: Sukces!"
                            dialogue_lines = [
                                "Leśny Dziadek łagodzi morderczy uścisk.",
                                "'Wyczuwam w tobie krew Mamuny... Chodź ze mną w najgłębsze rejony puszczy.'"
                            ]
                            dialogue_choices = [("Podążaj za nim", "GO_TO_STRANGE_PLACE_FROM_MOB")]
                            current_choice_idx = 0
                        else:
                            end_message = f"Wynik Charyzmy: {roll} (Porażka!).\nLeśny Dziadek: 'Łżesz jak pies! Pachniesz człowiekiem!'\nPnącza brutalnie łamią ci klatkę piersiową. (GAME OVER)"
                            current_state = STATE_END
                        continue

                    elif c_code == "GO_TO_STRANGE_PLACE_FROM_MOB":
                        current_map = "STRANGE_PLACE"
                        current_state = STATE_EXPLORE
                        player_pos = pygame.Vector2(WIDTH//2, HEIGHT - 50)
                        continue
                        
                    elif c_code == "SLEEP": 
                        player_hp = player_max_hp
                        player_sanity = min(player_max_sanity, player_sanity + 30)
                        dialogue_title = "Odpoczynek"
                        dialogue_lines = ["Przespałeś się na starym łóżku. Twoje rany się zagoiły, a umysł odpoczął."]
                        dialogue_choices = [("Wstań", "LEAVE")]
                        current_choice_idx = 0
                        continue
                        
                    elif c_code == "GO_TO_FOREST":
                        current_state = STATE_TRANSITION
                        continue
                    
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
                        dialogue_choices = [("Wróć do eksploracji", "LEAVE")]
                        if clues_found["rozmowa_pien"]: dialogue_choices.append(("Idź zniszczyć Latarnika", "START_LATARNIK_FIGHT"))
                        if clues_found["rozmowa_gawron"]: dialogue_choices.append(("Idź do leża Krzykacza", "START_KRZYKACZ_FIGHT"))
                        if clues_found["rozmowa_skrzekacz"]: dialogue_choices.append(("Próbuj zwerbować Lusię (Teleport)", "RECRUIT_LUSIA"))
                        current_choice_idx = 0
                        continue

                    elif c_code == "RECRUIT_LUSIA":
                        clues_found["wspolpraca_z_lusia"] = True
                        dialogue_title = "Pomoc Patronki"
                        dialogue_lines = ["Lusia decyduje się pomóc. Teleportuje cię od razu do leża Latarnika!"]
                        dialogue_choices = [("Zawalcz z nim (Masz wsparcie!)", "START_LATARNIK_FIGHT")]
                        current_choice_idx = 0
                        continue

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
                        
                        boss_mod_attack = -2 if clues_found["ma_amulet_zielarki"] else 2
                        mod_attack = 0 if clues_found["wspolpraca_z_lusia"] else -2

                        combat_timer = 0
                        combat_projectiles.clear()
                        continue

                    elif c_code == "FIGHT_MAMUNA":
                        current_state = STATE_COMBAT
                        active_boss_type = BOSS_MAMUNA
                        boss_hp = boss_max_hp = 180
                        boss_mod_attack = 2
                        combat_timer = 0
                        combat_projectiles.clear()
                        continue
                        
                    elif c_code == "SPARE_MAMUNA":
                        dialogue_title = "Pakt z Mamuną"
                        dialogue_lines = ["Mamuna kiwa głową z wdzięcznością.", "'Dziękuję. Las ci tego nie zapomni.'"]
                        dialogue_choices = [("Opuść leże w pokoju", "LEAVE_MAMUNA_PEACE")]
                        current_choice_idx = 0
                        for m in monster_triggers_forest:
                            if m["type"] == BOSS_MAMUNA: m["beaten"] = True
                        continue

                    elif c_code == "LEAVE_MAMUNA_PEACE" or c_code == "RETURN_TO_VILLAGE":
                        clues_found["mamuna_zalatwiona"] = True
                        current_map = "VILLAGE"
                        current_state = STATE_EXPLORE
                        player_pos = pygame.Vector2(WIDTH//2, HEIGHT - 50)
                        continue

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
                        if clues_found.get("wspolpraca_z_lusia", False) or clues_found.get("z_lusia", False):
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
                        roll = random.randint(1,6) + random.randint(1,6) + player_charisma
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
                        roll = random.randint(1,6) + random.randint(1,6) + player_charisma + 2
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

            elif current_state == STATE_END:
                if event.key == pygame.K_ESCAPE: running = False

    # 3. RENDEROWANIE
    if current_state == STATE_INTRO:
        screen.fill((10, 12, 15)) 
        for i in range(12): draw_tree(screen, 30 + i*80, HEIGHT - 300)
        
        pygame.draw.rect(screen, (25, 25, 30), (0, HEIGHT - 200, WIDTH, 200))
        
        zuk_x = -200 + (anim_tick * 2.5)
        if zuk_x > WIDTH // 2 - 100: zuk_x = WIDTH // 2 - 100
        draw_zuk(screen, zuk_x, HEIGHT - 190, light=True)
        
        bg_bar = pygame.Surface((WIDTH, 200), pygame.SRCALPHA)
        bg_bar.fill((0, 0, 0, 200))
        screen.blit(bg_bar, (0, HEIGHT - 200))
        
        title_text = intro_sequence[intro_step]["title"]
        main_text = intro_sequence[intro_step]["text"]
        
        y_pos = HEIGHT - 180
        y_pos += draw_text_wrapped(screen, title_text, font_title, (180, 200, 180), 80, y_pos, WIDTH - 160) + 10
        draw_text_wrapped(screen, main_text, font_main, (240, 240, 220), 80, y_pos, WIDTH - 160)

        screen.blit(font_sub.render("[Spacja / Enter by kontynuować]", True, (120, 120, 120)), (WIDTH - 280, HEIGHT - 40))
            
    elif current_state == STATE_TRANSITION:
        screen.fill((10, 15, 12))
        screen.blit(font_title.render("Wejście w głąb puszczy...", True, (120, 180, 120)), (80, HEIGHT - 180))

    elif current_state in [STATE_EXPLORE, STATE_HOUSE, STATE_DIALOGUE, STATE_DICE_ROLL]:
        if current_map == "VILLAGE":
            if current_state == STATE_HOUSE or (current_state == STATE_DIALOGUE and active_house is not None):
                screen.fill((10, 10, 12))
                pygame.draw.rect(screen, (50, 40, 30), (50, 50, WIDTH - 100, HEIGHT - 100))
                pygame.draw.rect(screen, (30, 20, 15), (50, 50, WIDTH - 100, HEIGHT - 100), 10)
                
                pygame.draw.circle(screen, (80, 40, 30), (WIDTH//2, HEIGHT//2), 65) 
                pygame.draw.circle(screen, (200, 180, 150), (WIDTH//2, HEIGHT//2), 20)
                
                house_name = active_house.name if active_house else "Wnętrze"
                screen.blit(font_title.render("Wnętrze: " + house_name, True, (220, 200, 150)), (70, 70))
                screen.blit(font_sub.render("Podejdź na środek, aby porozmawiać. Przejdź za krawędź ekranu, by wyjść.", True, (150, 150, 150)), (70, 110))
            else:
                screen.blit(terrain_surface, (0, 0))
                for tx, ty in decorations_trees: draw_tree(screen, tx, ty)
                draw_well(screen, 490, 420)
                for h in houses:
                    if h.name == "Wóz (Żuk)":
                        draw_zuk(screen, h.rect.x, h.rect.y, light=False)
                    else:
                        draw_slavic_house(screen, h.rect.x, h.rect.y, h.rect.width, h.rect.height, h.roof_color, h.ruined)
                
                if current_state == STATE_EXPLORE:
                    screen.blit(font_main.render(f"Sakiewka: {player_money} zł", True, (255, 215, 0)), (20, 20))
                    
                    pygame.draw.rect(screen, (50, 0, 0), (20, 50, 150, 15))
                    pygame.draw.rect(screen, (200, 50, 50), (20, 50, 150 * (player_hp / player_max_hp), 15))
                    pygame.draw.rect(screen, (200, 200, 200), (20, 50, 150, 15), 1)
                    screen.blit(font_sub.render("Zdrowie Drozda", True, (255, 255, 255)), (20, 70))
                    
                    pygame.draw.rect(screen, (30, 0, 50), (20, 90, 150, 15))
                    pygame.draw.rect(screen, (150, 50, 200), (20, 90, 150 * (max(0, player_sanity) / player_max_sanity), 15))
                    pygame.draw.rect(screen, (200, 200, 200), (20, 90, 150, 15), 1)
                    screen.blit(font_sub.render("Poczytalność", True, (255, 255, 255)), (20, 110))
        
        elif current_map == "FOREST":
            screen.fill((20, 25, 20))
            for tx, ty in forest_trees: draw_tree(screen, tx, ty)
        
        elif current_map == "STRANGE_PLACE":
            screen.fill((15, 10, 20)) 
            draw_wielkie_drzewo(screen, WIDTH//2 - 60, HEIGHT//2 - 150)
            if clues_found.get("wspolpraca_z_lusia", False) or clues_found.get("z_lusia", False): draw_lusia(screen, WIDTH//2 + 80, HEIGHT//2 + 50)
            draw_lesny_dziadek(screen, WIDTH//2 - 80, HEIGHT//2 + 50)

        if current_state in [STATE_EXPLORE, STATE_HOUSE]:
            draw_drozd(screen, int(player_pos.x), int(player_pos.y))

        if current_state == STATE_DIALOGUE:
            pygame.draw.rect(screen, (20, 20, 25), (40, HEIGHT - 250, WIDTH - 80, 230), border_radius=10)
            pygame.draw.rect(screen, (150, 140, 120), (40, HEIGHT - 250, WIDTH - 80, 230), 2, border_radius=10)
            
            combined_dialogue = " ".join(dialogue_lines)

            avatar_x, avatar_y = 90, HEIGHT - 210
            if "Sołtys" in dialogue_title:
                draw_soltys(screen, avatar_x, avatar_y)
            elif "Zielark" in dialogue_title:
                draw_zielarka(screen, avatar_x, avatar_y)
            elif "Plebania" in dialogue_title or "Maciek" in combined_dialogue:
                draw_maciek(screen, avatar_x, avatar_y)
            elif "Choroszcz" in dialogue_title or "Maria" in combined_dialogue:
                draw_maria(screen, avatar_x, avatar_y)
            
            current_y = HEIGHT - 230
            current_y += draw_text_wrapped(screen, dialogue_title, font_title, (200, 180, 150), 140, current_y, WIDTH - 200) + 10
            
            current_y += draw_text_wrapped(screen, combined_dialogue, font_main, (220, 220, 220), 140, current_y, WIDTH - 200) + 15
            
            for idx, choice in enumerate(dialogue_choices):
                color = (255, 200, 50) if idx == current_choice_idx else (150, 150, 150)
                choice_text = f"> {choice[0]}"
                current_y += draw_text_wrapped(screen, choice_text, font_main, color, 140, current_y, WIDTH - 200) + 5

    elif current_state == STATE_COMBAT:
        screen.fill((15, 10, 10))
        pygame.draw.rect(screen, (50, 0, 0), (WIDTH//2 - 100, 50, 200, 20))
        pygame.draw.rect(screen, (255, 0, 0), (WIDTH//2 - 100, 50, 200 * (boss_hp / boss_max_hp), 20))
        screen.blit(font_title.render(active_boss_type, True, (200, 50, 50)), (WIDTH//2 - 150, 15))
        
        pygame.draw.rect(screen, (0, 0, 50), (20, HEIGHT - 40, 200, 20))
        pygame.draw.rect(screen, (0, 100, 255), (20, HEIGHT - 40, 200 * (player_hp / player_max_hp), 20))
        
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
        elif active_boss_type == BOSS_MAMUNA:
            draw_monster_mamuna(screen, WIDTH//2 - 20, 200, anim_tick)

        draw_drozd(screen, int(player_combat_pos.x), int(player_combat_pos.y))
        for p in combat_projectiles: p.draw(screen)
        for b in combat_bullets: b.draw(screen)

    elif current_state == STATE_RUNNER:
        screen.fill((15, 25, 15))
        pygame.draw.line(screen, (80, 60, 40), (0, runner_ground_y + 40), (WIDTH, runner_ground_y + 40), 10)
        
        pygame.draw.rect(screen, (0, 0, 50), (20, 20, 200, 20))
        pygame.draw.rect(screen, (0, 100, 255), (20, 20, 200 * (player_hp / player_max_hp), 20))
        screen.blit(font_sub.render("HP Drozda", True, (255,255,255)), (25, 22))

        pygame.draw.rect(screen, (50, 0, 0), (WIDTH - 220, 20, 200, 20))
        pygame.draw.rect(screen, (255, 0, 0), (WIDTH - 220, 20, 200 * (runner_dziadek_hp / runner_dziadek_max_hp), 20))
        screen.blit(font_sub.render("HP Leśnego Dziadka", True, (255,255,255)), (WIDTH - 215, 22))

        screen.blit(font_main.render("[SPACE] - Skok  |  [E] - Strzał do tyłu", True, (150, 150, 150)), (WIDTH//2 - 150, 60))

        draw_drozd(screen, 400, int(runner_player_y))
        draw_lesny_dziadek(screen, 100, runner_ground_y + int(math.sin(runner_timer*0.2)*5))
        
        for o in runner_obstacles: o.draw(screen)
        for b in runner_bolts: pygame.draw.rect(screen, (200, 200, 200), b)

    elif current_state == STATE_DICE_ROLL:
        screen.fill((20, 20, 25))
        screen.blit(font_main.render("[Wciśnij ENTER]", True, (100, 100, 100)), (WIDTH//2 - 100, HEIGHT//2))

    elif current_state == STATE_END:
        screen.fill((0, 0, 0))
        draw_text_wrapped(screen, end_message, font_title, (200, 50, 50), WIDTH//2 - 350, HEIGHT//2 - 100, 700)
        screen.blit(font_sub.render("[ESC] - Wyjście", True, (100,100,100)), (WIDTH//2 - 50, HEIGHT - 50))

    # --- EFEKTY HALUCYNACJI ---
    if player_sanity <= 40 and current_state not in [STATE_END, STATE_INTRO]:
        pulsing = math.sin(anim_tick * 0.1) * 30
        overlay = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
        overlay.fill((int(50 + pulsing), 0, 0, 40)) 
        
        jitter_x = random.randint(-3, 3)
        jitter_y = random.randint(-3, 3)
        screen.blit(overlay, (jitter_x, jitter_y))
        
        if random.randint(1, 20) == 1:
            phantom_x, phantom_y = random.randint(0, WIDTH), random.randint(0, HEIGHT)
            pygame.draw.circle(screen, (255, 0, 0), (phantom_x, phantom_y), 4)

    # --- OBŁĘD (GAME OVER) ---
    if player_sanity <= 0 and current_state != STATE_END:
        end_message = "Twój umysł nie zniósł koszmaru Chołów.\nPopadłeś w głęboki obłęd. Trafiłeś do zakładu w Choroszczy, dołączając do Marii... (GAME OVER)"
        current_state = STATE_END

    pygame.display.flip()

pygame.quit()
sys.exit()
