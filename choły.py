import pygame
import sys
import random
import math
import numpy as np
from collections import defaultdict

# --- INICJALIZACJA DŹWIĘKU I PYGAME ---
pygame.mixer.pre_init(44100, -16, 2, 2048)
pygame.init()
pygame.mixer.init()

WIDTH, HEIGHT = 950, 700
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Krzykacz: Polowanie na Mamunę - Retro Horror Edition")
clock = pygame.time.Clock()

# --- NOWY KIERUNEK ARTYSTYCZNY (HIGH-RES PIXEL ART & PALETA) ---
SCALE_F = 1.5
LOW_W, LOW_H = int(WIDTH / SCALE_F), int(HEIGHT / SCALE_F)
game_surface = pygame.Surface((LOW_W, LOW_H))
fx_surface = pygame.Surface((LOW_W, LOW_H), pygame.SRCALPHA)

def S(val):
    return int(val / SCALE_F)

# Paleta kolorów
C_BLACK = (2, 2, 5)
C_VOID = (10, 10, 15)
C_DARK = (35, 30, 35)
C_BROWN = (70, 50, 40)
C_GRAY = (100, 100, 110)
C_LIGHT = (210, 210, 200)
C_RED = (190, 10, 10)
C_BLOOD = (100, 0, 0)
C_GOLD = (200, 150, 50) 
C_SKIN = (220, 180, 150)

# --- ZAAWANSOWANY PROCEDURALNY GENERATOR MUZYKI ---
def generate_slavic_theme():
    sample_rate = 44100
    notes = {
        'D3': 146.83, 'F3': 174.61, 'G3': 196.00, 'A3': 220.00, 
        'A#3': 233.08, 'C4': 261.63, 'D4': 293.66, 'E4': 329.63, 
        'F4': 349.23, 'G4': 392.00, 'A4': 440.00, 'rest': 0.0
    }

    melody = [
        ('D4', 0.4), ('F4', 0.2), ('E4', 0.2), ('D4', 0.4), ('A3', 0.4),
        ('D4', 0.4), ('F4', 0.2), ('G4', 0.2), ('A4', 0.8),
        ('A4', 0.4), ('G4', 0.2), ('F4', 0.2), ('E4', 0.4), ('C4', 0.4),
        ('D4', 0.2), ('E4', 0.2), ('F4', 0.2), ('E4', 0.2), ('D4', 0.8)
    ] * 2

    harmony = [
        ('D3', 1.6), ('F3', 1.6), 
        ('C4', 1.6), ('D3', 1.6)
    ] * 2
    
    total_duration = sum(dur for _, dur in melody)
    total_samples = int(sample_rate * total_duration)
    
    flute_track = np.zeros(total_samples)
    violin_track = np.zeros(total_samples)
    percussion_track = np.zeros(total_samples)
    
    current_sample = 0
    for note, duration in melody:
        samples = int(sample_rate * duration)
        if note != 'rest':
            freq = notes[note]
            t = np.linspace(0, duration, samples, False)
            wave = 0.8 * np.sin(2 * np.pi * freq * t) + 0.2 * np.sin(2 * np.pi * (freq * 2) * t)
            tremolo = 1.0 + 0.15 * np.sin(2 * np.pi * 6 * t)
            wave *= tremolo
            env = np.ones_like(t)
            attack, release = int(sample_rate * 0.05), int(sample_rate * 0.1)
            if samples > attack + release:
                env[:attack] = np.linspace(0, 1, attack)
                env[-release:] = np.linspace(1, 0, release)
            flute_track[current_sample:current_sample+samples] += wave * env * 0.5
        current_sample += samples

    current_sample = 0
    for note, duration in harmony:
        samples = int(sample_rate * duration)
        if note != 'rest':
            freq = notes[note]
            t = np.linspace(0, duration, samples, False)
            vibrato = np.sin(2 * np.pi * 5 * t) * 0.015
            mod_freq = freq * (1 + vibrato)
            phase = np.cumsum(mod_freq) / sample_rate
            wave = 2 * (phase - np.floor(phase + 0.5))
            wave = 0.5 * wave + 0.5 * np.sin(2 * np.pi * mod_freq * t)
            env = np.ones_like(t)
            attack, release = int(sample_rate * 0.4), int(sample_rate * 0.6) 
            if samples > attack + release:
                env[:attack] = np.linspace(0, 1, attack)
                env[-release:] = np.linspace(1, 0, release)
            violin_track[current_sample:current_sample+samples] += wave * env * 0.4
        current_sample += samples

    beat_interval = 0.4
    num_beats = int(total_duration / beat_interval)
    t_total = np.linspace(0, total_duration, total_samples, False)
    
    for i in range(num_beats):
        beat_start = int(i * beat_interval * sample_rate)
        if i % 2 == 0:
            beat_end = min(beat_start + int(0.2 * sample_rate), total_samples)
            t_beat = t_total[:beat_end-beat_start]
            kick_freq = np.linspace(120, 30, len(t_beat)) 
            kick = np.sin(2 * np.pi * kick_freq * t_beat)
            kick_env = np.exp(-12 * t_beat) 
            percussion_track[beat_start:beat_end] += kick * kick_env * 0.9
        
        if i % 2 != 0 or i % 4 == 3:
            shaker_end = min(beat_start + int(0.08 * sample_rate), total_samples)
            t_shaker = t_total[:shaker_end-beat_start]
            noise = np.random.uniform(-1, 1, len(t_shaker)) 
            shaker_env = np.exp(-25 * t_shaker)
            percussion_track[beat_start:shaker_end] += noise * shaker_env * 0.25

    final_track = flute_track + violin_track + percussion_track
    final_track = np.clip(final_track, -1.0, 1.0)
    track_16bit = np.int16(final_track * 32767)
    return np.ascontiguousarray(np.column_stack((track_16bit, track_16bit)))

def generate_barka_theme():
    sample_rate = 44100
    notes = {
        'G3': 196.00, 'A3': 220.00, 'B3': 246.94, 'C4': 261.63, 'D4': 293.66, 'E4': 329.63, 'F4': 349.23, 'G4': 392.00, 'A4': 440.00, 'rest': 0.0
    }
    melody = [
        ('G4', 0.3), ('C4', 0.3), ('D4', 0.3), ('E4', 0.5), ('D4', 0.3), ('C4', 0.3), ('A4', 0.6), ('rest', 0.1),
        ('A4', 0.3), ('F4', 0.3), ('G4', 0.3), ('A4', 0.5), ('G4', 0.3), ('F4', 0.3), ('E4', 0.6), ('rest', 0.1),
        ('E4', 0.3), ('C4', 0.3), ('D4', 0.3), ('E4', 0.5), ('D4', 0.3), ('C4', 0.3), ('G3', 0.6), ('rest', 0.1),
        ('A3', 0.3), ('B3', 0.3), ('C4', 0.3), ('D4', 0.5), ('B3', 0.3), ('G3', 0.3), ('C4', 0.8)
    ]
    total_samples = sum(int(sample_rate * dur) for _, dur in melody)
    track = np.zeros(total_samples)
    current_sample = 0
    for note_name, duration in melody:
        samples = int(sample_rate * duration)
        if note_name != 'rest':
            freq = notes[note_name]
            t = np.linspace(0, duration, samples, False)
            wave = 0.6 * np.sin(2 * np.pi * freq * t) + 0.2 * (2 * np.abs(2 * (t * freq - np.floor(t * freq + 0.5))) - 1)
            env = np.ones_like(t)
            attack, release = int(sample_rate * 0.05), int(sample_rate * 0.05)
            if samples > attack + release:
                env[:attack] = np.linspace(0, 1, attack)
                env[-release:] = np.linspace(1, 0, release)
            track[current_sample:current_sample+samples] += wave * env * 0.4
        current_sample += samples
    track = np.clip(track, -1.0, 1.0)
    track_16bit = np.int16(track * 32767)
    return np.ascontiguousarray(np.column_stack((track_16bit, track_16bit)))

print("Generowanie złożonej, mrocznej ścieżki dźwiękowej...")
audio_data = generate_slavic_theme()
slavic_sound = pygame.sndarray.make_sound(audio_data)
slavic_sound.set_volume(0.3)
slavic_sound.play(loops=-1, fade_ms=1000)

barka_data = generate_barka_theme()
barka_sound = pygame.sndarray.make_sound(barka_data)
barka_sound.set_volume(0.3)

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

def draw_pixel_line(surface, color, start, end, thickness=1):
    pygame.draw.line(surface, color, start, end, int(thickness * SCALE_F))

# ==============================================================================
# --- POSTACIE (Z AKTUALIZACJĄ WYGLĄDU) ---
# ==============================================================================
def draw_drozd(surface, x, y):
    pygame.draw.rect(surface, (40, 40, 45), (x - S(4), y + S(5), S(3), S(10)))
    pygame.draw.rect(surface, (40, 40, 45), (x + S(1), y + S(5), S(3), S(10)))
    pygame.draw.rect(surface, (20, 15, 10), (x - S(5), y + S(13), S(4), S(3)))
    pygame.draw.rect(surface, (20, 15, 10), (x + S(1), y + S(13), S(4), S(3)))
    pygame.draw.rect(surface, (110, 85, 60), (x - S(6), y - S(5), S(12), S(14)))
    pygame.draw.rect(surface, (70, 50, 35), (x - S(6), y - S(5), S(12), S(14)), 1) 
    pygame.draw.line(surface, (50, 30, 20), (x - S(6), y + S(2)), (x + S(5), y + S(2)), S(2))
    pygame.draw.rect(surface, C_SKIN, (x - S(4), y - S(12), S(8), S(8)))
    pygame.draw.rect(surface, (30, 25, 20), (x - S(5), y - S(14), S(10), S(4)))
    pygame.draw.rect(surface, (30, 25, 20), (x - S(5), y - S(12), S(3), S(4)))
    pygame.draw.line(surface, (200, 240, 255), (x - S(3), y - S(9)), (x + S(3), y - S(9)), S(2))
    pygame.draw.line(surface, (50, 50, 50), (x, y - S(10)), (x, y - S(8)), S(1)) 

def draw_lusia(surface, x, y):
    C_BLUE = (50, 100, 180)
    C_BLONDE = (220, 200, 50)
    pygame.draw.polygon(surface, C_BLUE, [(x - S(6), y), (x + S(6), y), (x + S(4), y + S(16)), (x - S(4), y + S(16))])
    pygame.draw.line(surface, C_DARK, (x - S(4), y + S(2)), (x - S(10), y + S(8)), 2)
    pygame.draw.line(surface, C_DARK, (x - S(10), y + S(8)), (x - S(8), y + S(18)), 1)
    pygame.draw.rect(surface, C_SKIN, (x - S(4), y - S(9), S(8), S(9)))
    pygame.draw.polygon(surface, C_BLONDE, [(x - S(7), y - S(11)), (x + S(8), y - S(9)), (x + S(4), y - S(2)), (x - S(6), y - S(3))])
    pygame.draw.circle(surface, C_BLACK, (x - S(2), y - S(5)), 1)
    pygame.draw.circle(surface, C_BLACK, (x + S(2), y - S(6)), 1)

# ==============================================================================
# --- MINI-SPRITE NPC ---
# ==============================================================================
def draw_npc_soltys(surface, x, y):
    pygame.draw.rect(surface, (40, 50, 40), (x-S(8), y-S(5), S(16), S(15))) 
    pygame.draw.rect(surface, C_SKIN, (x-S(5), y-S(12), S(10), S(8))) 
    pygame.draw.polygon(surface, C_BLACK, [(x-S(7), y-S(14)), (x+S(7), y-S(12)), (x+S(2), y-S(10)), (x-S(6), y-S(11))])

def draw_npc_zielarka(surface, x, y):
    pygame.draw.polygon(surface, (60, 40, 50), [(x, y-S(10)), (x-S(12), y+S(10)), (x+S(10), y+S(10))])
    pygame.draw.rect(surface, C_SKIN, (x-S(4), y-S(14), S(8), S(6)))
    pygame.draw.polygon(surface, C_GRAY, [(x-S(5), y-S(16)), (x+S(5), y-S(14)), (x, y-S(8))]) 

def draw_npc_maciek(surface, x, y):
    pygame.draw.rect(surface, (50, 50, 60), (x-S(6), y-S(5), S(12), S(15)))
    pygame.draw.rect(surface, C_SKIN, (x-S(4), y-S(12), S(8), S(8)))
    pygame.draw.line(surface, C_SKIN, (x-S(6), y), (x-S(5), y-S(10)), S(2))
    pygame.draw.line(surface, C_SKIN, (x+S(6), y), (x+S(5), y-S(10)), S(2))

def draw_npc_sprzedawca(surface, x, y):
    pygame.draw.rect(surface, C_VOID, (x-S(4), y-S(5), S(8), S(20)))
    pygame.draw.rect(surface, C_LIGHT, (x-S(3), y-S(12), S(6), S(8))) 
    pygame.draw.line(surface, C_BLACK, (x-S(2), y-S(8)), (x+S(2), y-S(8)), S(1)) 

# --- ARCHITEKTURA I ŚRODOWISKO (MARTWA WIOSKA) ---
def draw_uncanny_house(surface, x, y, width=160, height=110, ruined=False):
    if ruined:
        C_WALL = (30, 25, 25)
        main_rect = pygame.Rect(x, y + height//3, width, height - height//3)
        pygame.draw.rect(surface, C_WALL, main_rect)
        pygame.draw.rect(surface, C_BLACK, main_rect, 2)
        pygame.draw.polygon(surface, C_VOID, [(x - S(5), y + height//3), (x + width // 3, y + S(5)), (x + width//2, y + height//3 + S(5))])
        pygame.draw.line(surface, C_DARK, (x + S(10), y + height//3), (x + width - S(10), y - S(20)), 4) 
    else:
        C_WALL = (85, 80, 75)   
        C_ROOF = (50, 45, 45)   
        C_WINDOW = (5, 5, 5)    
        
        pygame.draw.rect(surface, C_WALL, (x, y, width, height))
        pygame.draw.rect(surface, C_BLACK, (x, y, width, height), 2)
        
        for i in range(S(15), height, S(15)):
            pygame.draw.line(surface, (70, 65, 60), (x, y + i), (x + width, y + i), 1)
            
        roof_poly = [(x - S(15), y), (x + width // 2, y - S(70)), (x + width + S(15), y)]
        pygame.draw.polygon(surface, C_ROOF, roof_poly)
        pygame.draw.polygon(surface, C_BLACK, roof_poly, 2)
        
        dw, dh = S(36), S(45)
        pygame.draw.rect(surface, (40, 35, 30), (x + width//2 - dw//2, y + height - dh, dw, dh))
        pygame.draw.rect(surface, C_BLACK, (x + width//2 - dw//2, y + height - dh, dw, dh), 2)
        
        ww, wh = S(30), S(35)
        pygame.draw.rect(surface, C_WINDOW, (x + S(20), y + S(40), ww, wh))
        pygame.draw.rect(surface, C_WINDOW, (x + width - S(50), y + S(40), ww, wh))
        pygame.draw.rect(surface, (60, 55, 50), (x + S(20), y + S(40), ww, wh), 2)
        pygame.draw.rect(surface, (60, 55, 50), (x + width - S(50), y + S(40), ww, wh), 2)

def draw_dead_grass(surface, x_start, x_end, y_start, y_end, count=150):
    C_GRASS = (70, 85, 70) 
    for _ in range(count):
        gx = random.randint(x_start, x_end)
        gy = random.randint(y_start, y_end)
        pygame.draw.line(surface, C_GRASS, (gx, gy), (gx, gy - S(random.randint(6, 12))), 1)

def draw_oily_mud(surface, x, y, width, height):
    C_MUD_DARK = (30, 28, 25)
    C_MUD_REFLECTION = (55, 55, 60)
    pygame.draw.ellipse(surface, C_MUD_DARK, (x, y, width, height))
    pygame.draw.ellipse(surface, C_MUD_REFLECTION, (x + S(4), y + S(2), width - S(12), height - S(6)))

def draw_tree(surface, x, y):
    pien_poly = [(x - S(6), y + S(10)), (x + S(8), y + S(8)), (x + S(10), y - S(40)), (x, y - S(80)), (x - S(8), y - S(30))]
    pygame.draw.polygon(surface, C_BLACK, pien_poly)
    pygame.draw.polygon(surface, C_VOID, [(x - S(5), y - S(70)), (x - S(30), y - S(90)), (x - S(10), y - S(110)), (x + S(5), y - S(90))])
    pygame.draw.polygon(surface, C_VOID, [(x + S(5), y - S(65)), (x + S(35), y - S(75)), (x + S(20), y - S(100)), (x - S(2), y - S(85))])
    draw_pixel_line(surface, C_DARK, (x - S(25), y - S(95)), (x - S(45), y - S(120)), 2)
    draw_pixel_line(surface, C_DARK, (x + S(30), y - S(75)), (x + S(50), y - S(90)), 2)

def draw_well(surface, x, y):
    w, h = S(40), S(30)
    pygame.draw.rect(surface, C_GRAY, (x - w//2, y - h//2, w, h))
    pygame.draw.rect(surface, C_BLACK, (x - w//2, y - h//2, w, h), 2)
    for i in range(3):
        pygame.draw.circle(surface, C_DARK, (x - w//2 + S(10) + i*S(10), y + random.randint(-4,4)), S(3))
    pygame.draw.line(surface, C_BROWN, (x - w//2 + 4, y - h//2), (x - w//2 + 4, y - S(35)), 3)
    pygame.draw.line(surface, C_BROWN, (x + w//2 - 4, y - h//2), (x + w//2 - 4, y - S(35)), 3)
    pygame.draw.polygon(surface, C_DARK, [(x - w//2 - 4, y - S(35)), (x, y - S(45)), (x + w//2 + 4, y - S(35))])
    pygame.draw.polygon(surface, C_BLACK, [(x - w//2 - 4, y - S(35)), (x, y - S(45)), (x + w//2 + 4, y - S(35))], 1)

def draw_zuk(surface, x, y, light=False):
    C_KAROSERIA = (90, 105, 115) 
    C_PLANDEKA = (130, 130, 125) 
    C_OPONY = (20, 20, 20)
    C_SZYBY = (15, 20, 25) 
    
    pygame.draw.rect(surface, C_PLANDEKA, (x - S(70), y - S(65), S(85), S(35)))
    pygame.draw.rect(surface, C_KAROSERIA, (x - S(70), y - S(30), S(85), S(20)))
    
    pygame.draw.rect(surface, C_KAROSERIA, (x + S(15), y - S(55), S(35), S(45)))
    pygame.draw.polygon(surface, C_SZYBY, [(x + S(20), y - S(50)), (x + S(45), y - S(50)), (x + S(45), y - S(35)), (x + S(20), y - S(35))])
    
    pygame.draw.polygon(surface, C_KAROSERIA, [(x + S(50), y - S(35)), (x + S(70), y - S(25)), (x + S(70), y - S(10)), (x + S(50), y - S(10))])
    pygame.draw.rect(surface, (50, 50, 50), (x + S(65), y - S(12), S(10), S(6)))

    pygame.draw.circle(surface, C_OPONY, (x - S(40), y - S(5)), S(14))
    pygame.draw.circle(surface, C_OPONY, (x + S(35), y - S(5)), S(14))
    pygame.draw.circle(surface, (100, 100, 100), (x - S(40), y - S(5)), S(6)) 
    pygame.draw.circle(surface, (100, 100, 100), (x + S(35), y - S(5)), S(6))

    pygame.draw.ellipse(surface, (200, 200, 200) if not light else (255, 255, 180), (x + S(66), y - S(24), S(6), S(10)))
    
    if light:
        light_surf = pygame.Surface((S(250), S(100)), pygame.SRCALPHA)
        pygame.draw.polygon(light_surf, (255, 255, 150, 40), [(0, S(30)), (S(250), 0), (S(250), S(100))])
        surface.blit(light_surf, (x + S(70), y - S(54)))

# --- POTWORY ---
def draw_monster_latarnik(surface, x, y, anim_tick):
    offset_y = int(math.sin(anim_tick * 0.1) * S(10))
    y += offset_y
    shadow_poly = [(x, y - S(50)), (x - S(25), y + S(20)), (x - S(10), y + S(35)), (x + S(15), y + S(30)), (x + S(30), y - S(10))]
    pygame.draw.polygon(surface, C_VOID, shadow_poly)
    pygame.draw.polygon(surface, C_BLACK, shadow_poly, 1) 
    for i in range(8):
        ky = y - S(40) + i*S(8)
        pygame.draw.ellipse(surface, C_LIGHT, (x - S(6), ky, S(12), S(5)))
        pygame.draw.ellipse(surface, C_DARK, (x - S(5), ky + S(1), S(10), S(4)), 1)
    arm_start, arm_elbow, arm_hand = (x + S(10), y - S(20)), (x + S(35), y), (x + S(25), y + S(30))
    draw_pixel_line(surface, C_BLACK, arm_start, arm_elbow, 4)
    draw_pixel_line(surface, C_VOID, arm_elbow, arm_hand, 3)
    pygame.draw.circle(surface, C_LIGHT, arm_elbow, 3)
    lat_r = pygame.Rect(arm_hand[0] - S(8), arm_hand[1], S(16), S(20))
    pygame.draw.rect(surface, C_BROWN, lat_r)
    pygame.draw.rect(surface, C_BLACK, lat_r, 2)
    light_val = int(abs(math.sin(anim_tick * 0.2)) * 100) + 155
    pygame.draw.rect(surface, (light_val, int(light_val*0.7), 0), (lat_r.x + 3, lat_r.y + 3, lat_r.w - 6, lat_r.h - 6))
    fx_radius = S(70) + int(abs(math.sin(anim_tick * 0.2)) * S(20))
    pygame.draw.circle(fx_surface, (C_GOLD[0], C_GOLD[1], C_GOLD[2], 80), (S(lat_r.centerx * SCALE_F), S(lat_r.centery * SCALE_F)), fx_radius)

def draw_monster_pien(surface, x, y):
    body_poly = [(x - S(40), y + S(20)), (x + S(45), y + S(25)), (x + S(30), y - S(50)), (x - S(35), y - S(45))]
    pygame.draw.polygon(surface, C_BROWN, body_poly)
    pygame.draw.polygon(surface, C_VOID, body_poly, 3)
    for i in range(5):
        dist = S(8) + i*S(6)
        pygame.draw.ellipse(surface, C_DARK, (x - dist*1.2, y - dist - S(10), dist*2.4, dist*2), 2)
    korzenie = [
        [(x - S(30), y + S(15)), (x - S(50), y + S(40)), (x - S(45), y + S(45))],
        [(x - S(10), y + S(20)), (x - S(15), y + S(55)), (x - S(5), y + S(60))],
        [(x + S(25), y + S(20)), (x + S(40), y + S(50)), (x + S(35), y + S(55))],
    ]
    for korz in korzenie:
        pygame.draw.polygon(surface, C_VOID, korz)
        pygame.draw.polygon(surface, C_BLACK, korz, 1)
    skull_poly = [(x - S(20), y - S(25)), (x + S(18), y - S(28)), (x + S(15), y - S(5)), (x, y + S(15)), (x - S(17), y - S(8))]
    pygame.draw.polygon(surface, C_LIGHT, skull_poly)
    pygame.draw.polygon(surface, C_GRAY, skull_poly, 1)
    pygame.draw.circle(surface, C_BLACK, (x - S(7), y - S(15)), S(3))
    pygame.draw.circle(surface, C_RED, (x - S(7), y - S(15)), S(1)) 
    pygame.draw.circle(surface, C_BLACK, (x + S(6), y - S(17)), S(3))
    pygame.draw.circle(surface, C_RED, (x + S(6), y - S(17)), S(1))
    draw_pixel_line(surface, C_LIGHT, (x - S(15), y - S(20)), (x - S(35), y - S(40)), 2)
    draw_pixel_line(surface, C_GRAY, (x + S(12), y - S(22)), (x + S(25), y - S(35)), 2)

def draw_monster_gawron(surface, x, y):
    wing_poly_l = [(x, y - S(30)), (x - S(60), y - S(50)), (x - S(40), y + S(10)), (x, y + S(10))]
    wing_poly_r = [(x, y - S(30)), (x + S(60), y - S(50)), (x + S(40), y + S(10)), (x, y + S(10))]
    pygame.draw.polygon(surface, C_VOID, wing_poly_l)
    pygame.draw.polygon(surface, C_VOID, wing_poly_r)
    for i in range(4):
        pygame.draw.line(surface, C_BLACK, (x - S(10), y - S(20) + i*S(6)), (x - S(55) + i*S(5), y - S(40) + i*S(8)), 2)
        pygame.draw.line(surface, C_BLACK, (x + S(10), y - S(20) + i*S(6)), (x + S(55) - i*S(5), y - S(40) + i*S(8)), 2)
    skull_poly = [(x - S(8), y - S(45)), (x + S(8), y - S(45)), (x + S(4), y - S(20)), (x - S(4), y - S(20))]
    pygame.draw.polygon(surface, C_LIGHT, skull_poly)
    pygame.draw.polygon(surface, C_GRAY, skull_poly, 1)
    beak_poly = [(x - S(2), y - S(25)), (x + S(2), y - S(25)), (x + S(1), y - S(5)), (x - S(10), y - S(15))]
    pygame.draw.polygon(surface, C_GRAY, beak_poly)
    pygame.draw.polygon(surface, C_BLACK, beak_poly, 1)
    pygame.draw.circle(surface, C_BLACK, (x - S(3), y - S(35)), S(2))
    pygame.draw.circle(surface, C_RED, (x - S(3), y - S(35)), S(1))
    pygame.draw.circle(surface, C_BLACK, (x + S(3), y - S(35)), S(2))
    pygame.draw.circle(surface, C_RED, (x + S(3), y - S(35)), S(1))

def draw_monster_skrzekacz(surface, x, y):
    pygame.draw.ellipse(surface, C_VOID, (x - S(35), y - S(20), S(70), S(45)))
    pygame.draw.ellipse(surface, C_BLACK, (x - S(25), y - S(15), S(50), S(35)), 2)
    for i in range(4):
        pygame.draw.circle(surface, C_DARK, (x + random.randint(-20,20), y + random.randint(-15,15)), S(4))
    legs = [
        [(x - S(30), y - S(10)), (x - S(55), y - S(30)), (x - S(50), y - S(35))],
        [(x - S(30), y + S(10)), (x - S(60), y + S(30)), (x - S(55), y + S(35))], 
        [(x + S(30), y - S(10)), (x + S(55), y - S(30)), (x + S(50), y - S(35))], 
        [(x + S(30), y + S(10)), (x + S(60), y + S(30)), (x + S(55), y + S(35))],
    ]
    for leg in legs:
        pygame.draw.polygon(surface, C_VOID, leg)
        pygame.draw.polygon(surface, C_BLACK, leg, 2)
    eyes = [(-S(15), -S(8)), (S(18), -S(12)), (-S(5), S(10)), (S(12), S(8)), (0, -S(15))]
    for ex, ey in eyes:
        pygame.draw.circle(surface, (255, 50, 50), (x + ex, y + ey), S(2))
        pygame.draw.circle(surface, C_BLOOD, (x + ex, y + ey), S(3), 1)

def draw_monster_mamuna(surface, x, y, anim_tick):
    offset_x = int(math.sin(anim_tick * 0.08) * S(5))
    x += offset_x
    main_poly = [(x - S(10), y - S(70)), (x + S(12), y - S(70)), (x + S(8), y + S(40)), (x - S(8), y + S(40))]
    pygame.draw.polygon(surface, C_VOID, main_poly)
    pygame.draw.polygon(surface, C_BLACK, main_poly, 2)
    for i in range(x - S(8), x + S(9), S(4)):
        pygame.draw.line(surface, C_BLACK, (i, y - S(65)), (i + random.randint(-2,2), y + S(35)), 2)
    pygame.draw.rect(surface, C_LIGHT, (x - S(4), y - S(60), S(8), S(12)))
    pygame.draw.circle(surface, C_RED, (x + S(1), y - S(55)), S(1))
    pygame.draw.line(surface, C_BLACK, (x - S(2), y - S(60)), (x - S(5), y - S(45)), 1)
    hand_l = [(x - S(10), y - S(25)), (x - S(30), y - S(15)), (x - S(15), y - S(5))]
    pygame.draw.polygon(surface, C_LIGHT, hand_l)
    pygame.draw.polygon(surface, C_GRAY, hand_l, 1)
    baby_poly = [(x - S(18), y - S(10)), (x - S(30), y - S(5)), (x - S(25), y + S(8)), (x - S(12), y + S(5))]
    pygame.draw.polygon(surface, C_BROWN, baby_poly)
    pygame.draw.circle(surface, C_BLACK, (x - S(20), y - S(2)), S(3))
    pygame.draw.circle(surface, C_RED, (x - S(20), y - S(2)), S(1))

def draw_true_krzykacz(surface, x, y, anim_tick):
    w, h = S(180), S(260) 
    breathe = int(math.sin(anim_tick * 0.05) * S(8))
    legs = [
        [(x - w//3, y - h//3), (x - w, y + h//4), (x - w*0.9, y + h//3)], 
        [(x - w//3, y), (x - w*1.1, y + h//2), (x - w*0.8, y + h//1.8)],
        [(x + w//3, y - h//3), (x + w, y + h//4), (x + w*0.9, y + h//3)], 
        [(x + w//3, y), (x + w*1.1, y + h//2), (x + w*0.8, y + h//1.8)], 
    ]
    for leg in legs:
        pygame.draw.polygon(surface, C_VOID, leg)
        pygame.draw.polygon(surface, C_BLACK, leg, 3) 
    torso_poly = [(x, y - h//2 + S(30)), (x - w//2.5, y + h//2), (x + w//2.5, y + h//2)]
    pygame.draw.polygon(surface, C_VOID, torso_poly)
    pygame.draw.polygon(surface, C_BLACK, torso_poly, 2)
    for i in range(6):
        pygame.draw.circle(surface, C_DARK, (x + random.randint(-40,40), y + random.randint(-50,50)), S(8))
    for i in range(5):
        rib_y = y - h//2 + S(60) + (i * S(18)) + breathe
        rib_w = S(25) + i*S(4)
        pygame.draw.ellipse(surface, C_LIGHT, (x - rib_w//2, rib_y, rib_w, S(6)))
        pygame.draw.ellipse(surface, C_GRAY, (x - rib_w//2, rib_y, rib_w, S(6)), 1) 
    skull_y = y - h//2 - S(20) + breathe
    skull_poly = [(x - S(30), skull_y), (x + S(30), skull_y), (x + S(5), skull_y + S(50)), (x - S(5), skull_y + S(50))]
    pygame.draw.polygon(surface, C_LIGHT, skull_poly)
    pygame.draw.polygon(surface, C_GRAY, skull_poly, 1)
    pygame.draw.circle(surface, C_BLACK, (x - S(12), skull_y + S(20)), S(5))
    pygame.draw.circle(surface, C_BLOOD, (x - S(12), skull_y + S(20)), S(2)) 
    pygame.draw.circle(surface, C_BLACK, (x + S(12), skull_y + S(20)), S(5))
    pygame.draw.circle(surface, C_BLOOD, (x + S(12), skull_y + S(20)), S(2))
    draw_pixel_line(surface, C_LIGHT, (x - S(20), skull_y), (x - S(70), skull_y - S(60)), 3)
    draw_pixel_line(surface, C_LIGHT, (x - S(40), skull_y - S(30)), (x - S(80), skull_y - S(20)), 2)
    draw_pixel_line(surface, C_LIGHT, (x + S(20), skull_y), (x + S(70), skull_y - S(60)), 3)
    draw_pixel_line(surface, C_LIGHT, (x + S(40), skull_y - S(30)), (x + S(80), skull_y - S(20)), 2)

def draw_lesny_dziadek(surface, x, y):
    pygame.draw.polygon(surface, C_GRAY, [(x - 8, y), (x + 8, y), (x + 5, y + 22), (x - 5, y + 22)])
    pygame.draw.polygon(surface, C_DARK, [(x - 8, y), (x + 8, y), (x + 5, y + 22), (x - 5, y + 22)], 1)
    broda_poly = [(x - 7, y - 5), (x + 7, y - 6), (x + 4, y + 15), (x, y + 18), (x - 4, y + 15)]
    pygame.draw.polygon(surface, C_LIGHT, broda_poly)
    pygame.draw.polygon(surface, C_GRAY, broda_poly, 1) 
    pygame.draw.circle(surface, C_VOID, (x, y - 10), S(6))
    pygame.draw.circle(surface, C_BLACK, (x, y - 10), S(7), 1)
    pygame.draw.circle(surface, C_RED, (x - 1, y - 11), S(1))
    pygame.draw.line(surface, C_BROWN, (x + 12, y - 25), (x + 12, y + 25), S(3))
    pygame.draw.rect(surface, C_BLACK, (x + 10, y - 25, S(4), S(50)), 1) 

def draw_wielkie_drzewo(surface, x, y):
    pygame.draw.polygon(surface, C_VOID, [(x-S(40), y+S(50)), (x+S(50), y+S(40)), (x+S(30), y-S(100)), (x-S(45), y-S(90))])
    pygame.draw.polygon(surface, C_BLACK, [(x-S(40), y+S(50)), (x+S(50), y+S(40)), (x+S(30), y-S(100)), (x-S(45), y-S(90))], S(3))
    for i in range(6):
        dist = S(15) + i*S(8)
        pygame.draw.ellipse(surface, C_DARK, (x - dist*1.3, y - dist*2 - S(20), dist*2.6, dist*4), 2)
    face_r = pygame.Rect(x - S(10), y - S(60), S(20), S(30))
    pygame.draw.ellipse(surface, C_VOID, face_r)
    pygame.draw.ellipse(surface, C_BLACK, face_r, 2)
    pygame.draw.circle(surface, C_RED, (x - S(4), y - S(50)), S(2))
    pygame.draw.circle(surface, C_RED, (x + S(4), y - S(48)), S(2))
    pygame.draw.ellipse(surface, C_BLACK, (x - S(3), y - S(40), S(6), S(10)))
    pygame.draw.polygon(surface, C_VOID, [(x-S(15), y-S(90)), (x-S(100), y-S(130)), (x-S(60), y-S(160)), (x+S(5), y-S(110))])
    pygame.draw.polygon(surface, C_BLACK, [(x-S(15), y-S(90)), (x-S(100), y-S(130)), (x-S(60), y-S(160)), (x+S(5), y-S(110))], 1)
    pygame.draw.polygon(surface, C_VOID, [(x+S(15), y-S(90)), (x+S(100), y-S(130)), (x+S(60), y-S(160)), (x-S(5), y-S(110))])
    pygame.draw.polygon(surface, C_BLACK, [(x+S(15), y-S(90)), (x+S(100), y-S(130)), (x+S(60), y-S(160)), (x-S(5), y-S(110))], 1)

# --- PORTRETY UI ---
def draw_portrait_base(surface, x, y, size=70):
    pygame.draw.rect(surface, (5, 5, 10), (x - size//2, y - size//2, size, size))
    pygame.draw.rect(surface, C_GRAY, (x - size//2, y - size//2, size, size), 2)

def draw_soltys(surface, x, y):
    draw_portrait_base(surface, x, y)
    pygame.draw.polygon(surface, C_VOID, [(x - 22, y + 20), (x + 18, y + 15), (x + 22, y + 35), (x - 25, y + 35)])
    pygame.draw.polygon(surface, C_BLACK, [(x - 22, y + 20), (x + 18, y + 15), (x + 22, y + 35), (x - 25, y + 35)], 2)
    pygame.draw.rect(surface, C_SKIN, (x - 14, y - 10, 26, 26))
    pygame.draw.polygon(surface, C_BLACK, [(x - 14, y - 10), (x + 12, y - 10), (x + 12, y + 16), (x - 14, y + 16)], 2)
    pygame.draw.polygon(surface, C_GRAY, [(x - 14, y + 8), (x - 16, y + 25), (x + 4, y + 18)]) 
    pygame.draw.circle(surface, C_RED, (x - 6, y - 2), 3)
    pygame.draw.line(surface, C_BLACK, (x + 6, y - 3), (x + 10, y - 1), 3)

def draw_zielarka(surface, x, y):
    draw_portrait_base(surface, x, y)
    pygame.draw.polygon(surface, C_VOID, [(x, y - 15), (x - 30, y + 35), (x + 20, y + 35)])
    pygame.draw.polygon(surface, C_BLACK, [(x, y - 15), (x - 30, y + 35), (x + 20, y + 35)], 2)
    pygame.draw.polygon(surface, C_SKIN, [(x - 10, y - 12), (x + 8, y - 15), (x, y + 10)])
    pygame.draw.polygon(surface, C_BLACK, [(x - 10, y - 12), (x + 8, y - 15), (x, y + 10)], 2)
    pygame.draw.circle(surface, C_VOID, (x - 4, y - 5), 4)
    pygame.draw.circle(surface, C_LIGHT, (x - 4, y - 5), 1)

def draw_maciek(surface, x, y):
    draw_portrait_base(surface, x, y)
    pygame.draw.rect(surface, C_VOID, (x - 20, y + 10, 35, 25))
    pygame.draw.rect(surface, C_BLACK, (x - 20, y + 10, 35, 25), 2)
    pygame.draw.polygon(surface, C_SKIN, [(x - 15, y - 10), (x, y - 18), (x + 8, y + 3), (x - 10, y + 5)])
    pygame.draw.polygon(surface, C_BLACK, [(x - 15, y - 10), (x, y - 18), (x + 8, y + 3), (x - 10, y + 5)], 2)
    pygame.draw.rect(surface, C_VOID, (x - 8, y - 8, 5, 4))
    pygame.draw.rect(surface, C_VOID, (x + 2, y - 10, 4, 3))

def draw_maria(surface, x, y):
    draw_portrait_base(surface, x, y)
    pygame.draw.polygon(surface, C_GRAY, [(x - 6, y), (x - 25, y + 35), (x + 20, y + 35)])
    pygame.draw.polygon(surface, C_BLACK, [(x - 6, y), (x - 25, y + 35), (x + 20, y + 35)], 2)
    pygame.draw.polygon(surface, C_LIGHT, [(x - 8, y - 20), (x + 10, y - 18), (x + 6, y + 3), (x - 6, y + 5)])
    pygame.draw.polygon(surface, C_BLACK, [(x - 8, y - 20), (x + 10, y - 18), (x + 6, y + 3), (x - 6, y + 5)], 2)
    pygame.draw.circle(surface, C_RED, (x - 3, y - 10), 3)
    pygame.draw.circle(surface, C_VOID, (x + 6, y - 12), 4)

def draw_szef_drwali(surface, x, y):
    draw_portrait_base(surface, x, y)
    # Ubranie
    pygame.draw.polygon(surface, C_VOID, [(x-25, y+35), (x+25, y+35), (x+20, y-10), (x-20, y-10)])
    pygame.draw.polygon(surface, C_BLACK, [(x-25, y+35), (x+25, y+35), (x+20, y-10), (x-20, y-10)], 2)
    # Twarz
    pygame.draw.rect(surface, C_SKIN, (x-12, y-20, 24, 28))
    # Duży nos
    pygame.draw.ellipse(surface, (210, 150, 120), (x-6, y-6, 12, 12))
    # Brązowa broda
    pygame.draw.polygon(surface, (80, 50, 30), [(x-15, y), (x+15, y), (x+10, y+22), (x-10, y+22)])
    # Kowbojski kapelusz
    pygame.draw.ellipse(surface, (110, 75, 45), (x-22, y-25, 44, 14))
    pygame.draw.rect(surface, (110, 75, 45), (x-14, y-38, 28, 18))
    pygame.draw.line(surface, C_BLACK, (x-14, y-25), (x+14, y-25), 2)
    # Oczy
    pygame.draw.circle(surface, C_BLACK, (x-5, y-12), 2)
    pygame.draw.circle(surface, C_BLACK, (x+5, y-12), 2)

def draw_sprzedawca(surface, x, y):
    draw_portrait_base(surface, x, y)
    pygame.draw.polygon(surface, C_LIGHT, [(x-10, y-15), (x+8, y-20), (x+6, y+8), (x-8, y+4)])
    pygame.draw.polygon(surface, C_BLACK, [(x-10, y-15), (x+8, y-20), (x+6, y+8), (x-8, y+4)], 2)
    pygame.draw.circle(surface, C_VOID, (x-4, y-9), 4)
    pygame.draw.circle(surface, C_VOID, (x+5, y-11), 3)
    pygame.draw.line(surface, C_BLACK, (x-6, y), (x+6, y-5), 3)

def draw_menel(surface, x, y):
    draw_portrait_base(surface, x, y)
    pygame.draw.polygon(surface, C_GRAY, [(x-22, y+35), (x+18, y+35), (x+8, y+10), (x-15, y+15)])
    pygame.draw.polygon(surface, C_BLACK, [(x-22, y+35), (x+18, y+35), (x+8, y+10), (x-15, y+15)], 2)
    pygame.draw.rect(surface, C_SKIN, (x-10, y-8, 16, 18))
    pygame.draw.rect(surface, C_BLACK, (x-10, y-8, 16, 18), 2)
    pygame.draw.circle(surface, C_RED, (x-5, y-2), 2)
    pygame.draw.circle(surface, C_RED, (x+3, y-3), 2)

# --- FUNKCJE POMOCNICZE ---
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

def apply_atmosphere(surface):
    vignette = pygame.Surface((LOW_W, LOW_H), pygame.SRCALPHA)
    pygame.draw.rect(vignette, (C_BLACK[0], C_BLACK[1], C_BLACK[2], 240), (0, 0, LOW_W, LOW_H), S(30))
    pygame.draw.rect(vignette, (C_BLACK[0], C_BLACK[1], C_BLACK[2], 160), (S(30), S(30), LOW_W-S(60), LOW_H-S(60)), S(25))
    surface.blit(vignette, (0, 0))
    
    fog = pygame.Surface((LOW_W, LOW_H), pygame.SRCALPHA)
    pygame.draw.rect(fog, (C_GRAY[0], C_GRAY[1], C_GRAY[2], 50), (0, LOW_H - S(80), LOW_W, S(80)))
    for i in range(10):
        fx, fy = random.randint(0, LOW_W), random.randint(LOW_H - S(100), LOW_H)
        pygame.draw.circle(fog, (C_DARK[0], C_DARK[1], C_DARK[2], 30), (fx, fy), S(40))
    surface.blit(fog, (0, 0))

    noise_surf = pygame.Surface((LOW_W, LOW_H), pygame.SRCALPHA)
    for i in range(5000): 
        nx, ny = random.randint(0, LOW_W-1), random.randint(0, LOW_H-1)
        gray = random.randint(5, 50)
        alpha = random.randint(10, 80)
        noise_surf.set_at((nx, ny), (gray, gray, gray + 5, alpha))
    surface.blit(noise_surf, (0, 0))

class Projectile:
    def __init__(self, x, y, vx, vy, color, radius=5):
        self.x, self.y, self.vx, self.vy, self.color, self.radius = x, y, vx, vy, color, radius
        self.trail = [] 
    def update(self):
        self.trail.append((self.x, self.y))
        if len(self.trail) > 4: self.trail.pop(0)
        self.x += self.vx
        self.y += self.vy
    def draw(self, surface):
        if len(self.trail) > 1:
            points = [(S(tx), S(ty)) for tx, ty in self.trail]
            pygame.draw.lines(surface, C_BLOOD, False, points, S(3))
        r = S(self.radius) if S(self.radius) > 1 else 2
        pygame.draw.rect(surface, self.color, (S(self.x) - r//2, S(self.y) - r//2, r, r))

class RunnerObstacle:
    def __init__(self, x, y, width, height, type_id, speed):
        self.rect = pygame.Rect(x, y, width, height)
        self.type = type_id
        self.speed = speed
    def update(self):
        self.rect.x -= self.speed
    def draw(self, surface):
        color = C_BROWN if self.type == "LOG" else C_VOID
        r = self.rect
        pygame.draw.rect(surface, color, (S(r.x), S(r.y), S(r.width), S(r.height)))
        pygame.draw.rect(surface, C_BLACK, (S(r.x), S(r.y), S(r.width), S(r.height)), 2)

low_terrain_surface = pygame.Surface((LOW_W, LOW_H))
low_terrain_surface.fill((40, 45, 40)) 
draw_oily_mud(low_terrain_surface, S(200), S(350), S(80), S(20))
draw_oily_mud(low_terrain_surface, S(500), S(400), S(120), S(25))
draw_oily_mud(low_terrain_surface, S(150), S(200), S(90), S(15))
draw_dead_grass(low_terrain_surface, 0, LOW_W, LOW_H // 2, LOW_H, count=400)

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

font_main = pygame.font.SysFont("courier", 16)
font_sub = pygame.font.SysFont("courier", 12)
font_title = pygame.font.SysFont("courier", 20, bold=True)

intro_sequence = [
    {"title": "Wnętrze Żuka. Cuchnie tanim tytoniem.", "text": "Kierowca Władek: W Chołach babka spaliła dzieciaka w piecu. Chore... Maciej rozpacza, a Marię zabrali do Choroszczy..."},
    {"title": "Wioska Choły. Ciemność.", "text": "Drozd, psycholog śledczy: 'Zobaczymy ile w tym prawdy...' (Porozmawiaj z ludźmi. Znajdź poszlaki. Rozwiąż sprawę. Strzeż umysłu...)"}
]
intro_step = 0

decorations_trees = [(random.randint(0, WIDTH), random.randint(0, HEIGHT)) for _ in range(15)]
forest_trees = [(random.randint(0, WIDTH), random.randint(0, HEIGHT)) for _ in range(35)]

player_agility = 5
player_charisma = 5
clues_found = defaultdict(bool)

# ==============================================================================
# --- SYSTEM LOKACJI I DIALOGÓW ---
# ==============================================================================
class BasicHouse:
    def __init__(self, x, y, name, w=160, h=110, ruined=False, dialog_override=None):
        self.rect = pygame.Rect(x, y, w, h)
        self.door_rect = pygame.Rect(x + 20, y + h - 40, 40, 40)
        self.name = name
        self.ruined = ruined
        self.dialog_override = dialog_override
        
    def dialog_func(self):
        if self.dialog_override: return self.dialog_override()
        return "Zamknięte na głucho.", [("Odejdź", "LEAVE")]

def get_soltys_dialog():
    ch = [("Daj w łapę (5zł)", "PAY_SOLTYS")]
    if clues_found.get("zardzewialy_sztylet"): ch.append(("Pokaż zardzewiały sztylet", "SHOW_DAGGER"))
    ch.append(("Odejdź", "LEAVE"))
    return "Sołtys: Czego tu? Nie wtykaj nosa w nieswoje sprawy.", ch

def get_sklep_dialogue():
    return "Sklep. Czego szukasz, miastowy?", [("Kup Cukierki (5zł)", "BUY_CANDY"), ("Kup Wino (10zł)", "BUY_WINE"), ("Wyjdź", "LEAVE")]

def get_zielarka_dialog():
    ch = [("Zapłać za rady (5zł)", "PAY_ZIELARKA"), ("Spróbuj zastraszyć (Charyzma)", "TEST_CHARISMA_ZIELARKA")]
    if clues_found.get("ma_ksiege_zielarki"): ch.append(("Oddaj księgę", "ODDAJ_KSIEGE_ZIELARCE"))
    if clues_found.get("quest_zielarka_zaczety"): ch.append(("Zdobądź Miksturę Smrodu", "START_SMROD_QUEST"))
    if clues_found.get("rozmowa_zielarka_smrod"): ch.append(("Skradnij Zgniły Grzyb (Zręczność)", "TEST_AGILITY_GRZYB"))
    if clues_found.get("ma_zgnily_grzyb") and not clues_found.get("ma_miksture_smrodu"): ch.append(("Wymień Grzyb na Miksturę", "TAKE_MIKSTURA"))
    ch.append(("Odejdź", "LEAVE"))
    return "Zielarka: Ciemność gęstnieje wokół ciebie, obcy...", ch

def get_plebania_dialog():
    ch = [("Zapytaj o księgę Zielarki", "ZAPYTAC_MACKA_O_KSIEGE"), ("Poproś o upoważnienie do Choroszczy", "GET_UPOWAZNIENIE")]
    if clues_found.get("zna_sekretny_schowek"): ch.append(("Przeszukaj schowek po cichu", "CLUE_RUINY_SKARB"))
    ch.append(("Odejdź", "LEAVE"))
    return "Plebania. Maciek modli się cicho w kącie.", ch

def get_mikolaj_dialog():
    ch = [("Zagadaj do Lusi", "LUSIA_TALK")]
    if clues_found.get("ma_cukierki"): ch.append(("Daj cukierki", "LUSIA_GIVE_CANDY"))
    if clues_found.get("wspolpraca_z_lusia"): ch.append(("Porozmawiaj o Lesie", "LUSIA_TALK_TRUST"))
    ch.append(("Odejdź", "LEAVE"))
    return "Dom Mikołaja. Mała Lusia wpatruje się w las.", ch

def get_spalona_dialog():
    ch = [("Szukaj w zgliszczach", "CLUE_DAGGER"), ("Zbadaj piec", "CLUE_KOSCI")]
    if clues_found.get("klamstwo_zielarka_sukces") or clues_found.get("zaufanie_zielarki"):
        ch.append(("Otwórz ukrytą skrytkę pod piecem", "CLUE_AMULET"))
    ch.append(("Odejdź", "LEAVE"))
    return "Spalona chata. Śmierdzi dymem i spalenizną...", ch

def get_woz_dialog():
    ch = [("Idź spać (Leczenie i Poczytalność)", "SLEEP"), ("Weź zapasy (Bimber)", "TAKE_BIMBER")]
    if clues_found.get("ma_upowaznienie_maciek"): ch.append(("Jedź do Choroszczy porozmawiać z Marią", "GO_CHOROSZCZ"))
    if clues_found.get("dowod_kosci") and player_sanity < 50: ch.append(("Czekaj na noc... (Bunt)", "TRIGGER_MOB_EVENT"))
    ch.append(("Wejdź do Lasu", "GO_TO_FOREST"))
    ch.append(("Wyjdź", "LEAVE"))
    return "Wnętrze Żuka. Cuchnie tanim tytoniem.", ch

houses = [
    BasicHouse(150, 150, "Dom Sołtysa", dialog_override=get_soltys_dialog),
    BasicHouse(450, 250, "Wóz (Żuk)", dialog_override=get_woz_dialog),
    BasicHouse(600, 100, "Spalona Chata", ruined=True, dialog_override=get_spalona_dialog),
    BasicHouse(150, 400, "Sklep", dialog_override=get_sklep_dialogue),
    BasicHouse(400, 450, "Plebania", dialog_override=get_plebania_dialog),
    BasicHouse(650, 450, "Dom Mikołaja", dialog_override=get_mikolaj_dialog),
    BasicHouse(800, 150, "Chata Zielarki", dialog_override=get_zielarka_dialog)
]

monster_triggers_forest = [
    {"rect": pygame.Rect(200, 200, 80, 80), "type": BOSS_LATARNIK, "beaten": False},
    {"rect": pygame.Rect(400, 400, 80, 80), "type": BOSS_MAMUNA, "beaten": False},
    {"rect": pygame.Rect(600, 150, 80, 80), "type": BOSS_PIEN, "beaten": False},
    {"rect": pygame.Rect(750, 350, 80, 80), "type": BOSS_GAWRON, "beaten": False},
    {"rect": pygame.Rect(250, 550, 80, 80), "type": BOSS_SKRZEKACZ, "beaten": False}
]

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
                # Strefa Drwali pojawiająca się dopiero po ucieczce przed drzewem
                if clues_found.get("powrot_do_cholow") and not clues_found.get("drwale_przekonani"):
                    oboz_rect = pygame.Rect(WIDTH//2 - 50, 30, 100, 80)
                    if oboz_rect.collidepoint(player_pos.x, player_pos.y):
                        current_state = STATE_DIALOGUE
                        dialogue_title = "Obóz Drwali"
                        dialogue_lines = ["Szef drwali: Czego tu szukasz? Tniemy ten las, jutro wjeżdża ciężki sprzęt!"]
                        ch = [("Zastrasz ich opowieścią (Charyzma)", "DRWALE_CHARISMA")]
                        if clues_found.get("ma_bimber"): ch.append(("Poczęstuj Bimbrem", "DRWALE_BIMBER"))
                        if clues_found.get("ma_miksture_smrodu"): ch.append(("Rzuć Miksturę Smrodu", "DRWALE_SMROD"))
                        if clues_found.get("ma_tanie_wino"): ch.append(("Daj Wino Menelom na odsiecz", "DRWALE_MENELE"))
                        ch.append(("Odejdź", "LEAVE_WINDOW"))
                        dialogue_choices = ch
                        current_choice_idx = 0

                for h in houses:
                    if h.door_rect.collidepoint(player_pos.x, player_pos.y) and "Wóz (Żuk)" not in h.name:
                        current_state = STATE_HOUSE
                        active_house = h
                        player_pos = pygame.Vector2(WIDTH // 2, HEIGHT - 130)
                        break
                    elif h.door_rect.collidepoint(player_pos.x, player_pos.y) and "Wóz (Żuk)" in h.name:
                        current_state = STATE_DIALOGUE
                        active_house = h   # <--- NAPRAWA: przypisanie wozu jako aktywnej lokacji
                        dialogue_title = h.name
                        t, c = h.dialog_func()
                        dialogue_lines, dialogue_choices = [t], c
                        current_choice_idx = 0
                        break
                
                if current_state == STATE_EXPLORE:
                    okno_soltysa = pygame.Rect(230, 90, 40, 40)
                    if okno_soltysa.collidepoint(player_pos.x, player_pos.y):
                        current_state = STATE_DIALOGUE
                        dialogue_title = "Ciemne Okno"
                        if clues_found["podslyszano_soltysa"]:
                            dialogue_lines = ["Nic więcej nie usłyszysz. Głucha cisza."]
                            dialogue_choices = [("Odejdź", "LEAVE_WINDOW")]
                        else:
                            dialogue_lines = ["Widzisz migoczące światło. Sołtys z kimś rozmawia. Podsłuchujesz?"]
                            dialogue_choices = [("Podsłuchuj (Zręczność)", "TEST_AGILITY_WINDOW"), ("Zostaw to", "LEAVE_WINDOW")]
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
                                dialogue_lines = ["Z mgły wyłania się koszmar. Twój umysł tego odrzuca! (-15 Poczytalności)", "Bez wiedzy to samobójstwo."]
                                dialogue_choices = [("Uciekaj!", "LEAVE")]
                                current_choice_idx = 0
                                player_pos.y += 40
                                break
                            elif not clues_found["mamuna_rozmowa"]:
                                current_state = STATE_DIALOGUE
                                dialogue_title = "Leże Mamuny - Konfrontacja"
                                dialogue_lines = ["Mamuna gładzi ludzkie niemowlę...", "'Zostaw nas w spokoju.'"]
                                dialogue_choices = [("Oddaj dziecko i giń!", "FIGHT_MAMUNA"), ("Opuść broń.", "SPARE_MAMUNA")]
                                current_choice_idx = 0
                                clues_found["mamuna_rozmowa"] = True
                                player_pos.y += 20 
                                break

                        elif active_boss_type == BOSS_LATARNIK and not clues_found["rozmowa_latarnik"]:
                            current_state = STATE_DIALOGUE
                            dialogue_title = "Spotkanie z Latarnikiem"
                            dialogue_lines = ["Latarnik drży w powietrzu trzymając żarzącą się latarnię."]
                            dialogue_choices = [("Zaatakuj go", "START_LATARNIK_FIGHT")]
                            if clues_found["ma_amulet_zielarki"]: dialogue_choices.insert(0, ("Podaj mu amulet Zielarki", "GIVE_AMULET"))
                            current_choice_idx = 0
                            clues_found["rozmowa_latarnik"] = True
                            player_pos.y += 20
                            break
                        elif active_boss_type == BOSS_PIEN and not clues_found["rozmowa_pien"]:
                            current_state = STATE_DIALOGUE
                            dialogue_title = "Spotkanie z Pniem"
                            dialogue_lines = ["Demon Pień chrumka groźnie."]
                            dialogue_choices = [("Pytaj o Latarnika", "INFO_LATARNIK"), ("Walka", "START_GENERIC_FIGHT")]
                            current_choice_idx = 0
                            player_pos.y += 20
                            break
                        elif active_boss_type == BOSS_GAWRON and not clues_found["rozmowa_gawron"]:
                            current_state = STATE_DIALOGUE
                            dialogue_title = "Spotkanie z Gawronem"
                            dialogue_lines = ["Gawron - anioł z głową ptaka."]
                            dialogue_choices = [("Gdzie leży legowisko Krzykacza?", "INFO_KRZYKACZ_LAIR"), ("Walka", "START_GENERIC_FIGHT")]
                            current_choice_idx = 0
                            player_pos.y += 20
                            break
                        elif active_boss_type == BOSS_SKRZEKACZ and not clues_found["rozmowa_skrzekacz"]:
                            current_state = STATE_DIALOGUE
                            dialogue_title = "Spotkanie ze Skrzekaczem"
                            dialogue_lines = ["Zza liści wyłania się Skrzekacz."]
                            dialogue_choices = [("Pytaj o Lusię", "INFO_LUSIA"), ("Walka", "START_GENERIC_FIGHT")]
                            current_choice_idx = 0
                            player_pos.y += 20
                            break
                        elif m["beaten"] == False and active_boss_type not in [BOSS_LATARNIK, BOSS_PIEN, BOSS_GAWRON, BOSS_SKRZEKACZ, BOSS_MAMUNA]:
                            current_state = STATE_DICE_ROLL
                            p_d1, p_d2 = random.randint(1,6), random.randint(1,6)
                            m_d1, m_d2 = random.randint(1,6), random.randint(1,6)
                            mod_attack, mod_stamina = (p_d1 + p_d2) - 6, (p_d1 + p_d2) // 2
                            boss_mod_attack, boss_mod_stamina = (m_d1 + m_d2) - 6, (m_d1 + m_d2) // 2
                            boss_hp = boss_max_hp = 100 + (boss_mod_stamina * 5)
                            break
            
            elif current_map == "STRANGE_PLACE":
                if pygame.Vector2(player_pos.x, player_pos.y).distance_to(pygame.Vector2(WIDTH//2, HEIGHT//2 - 50)) < 70:
                    current_state = STATE_DIALOGUE
                    pygame.event.post(pygame.event.Event(pygame.KEYDOWN, key=pygame.K_RETURN, c_code="TALK_TO_TREE"))

        elif current_state == STATE_HOUSE:
            if active_house is None:  # <--- NAPRAWA: Zabezpieczenie przed błędem, gdy wejdziemy w dom bez przypisania
                current_state = STATE_EXPLORE
                continue
                
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
                combat_projectiles.append(Projectile(latarnik_pos.x, latarnik_pos.y, (dx/dist)*8, (dy/dist)*8, C_RED, 8))
        else:
            fire_rate = 40 if active_boss_type != BOSS_TRUE_KRZYKACZ else 25
            if combat_timer % fire_rate == 0:
                dx, dy = player_combat_pos.x - (WIDTH//2), player_combat_pos.y - 220
                dist = math.hypot(dx, dy) if math.hypot(dx, dy) != 0 else 1
                spd = 6 if active_boss_type != BOSS_TRUE_KRZYKACZ else 9
                combat_projectiles.append(Projectile(WIDTH//2, 220, (dx/dist)*spd, (dy/dist)*spd, C_RED, 10))
            
        if keys[pygame.K_SPACE] and combat_timer % 15 == 0:
            combat_bullets.append(Projectile(player_combat_pos.x, player_combat_pos.y, 0, -10, C_LIGHT, 6))

        for b in combat_bullets[:]:
            b.update()
            target_pos = latarnik_pos if active_boss_type == BOSS_LATARNIK else pygame.Vector2(WIDTH//2, 220)
            if pygame.Vector2(b.x, b.y).distance_to(target_pos) < 45:
                boss_hp -= max(1, base_attack + mod_attack)
                if b in combat_bullets: combat_bullets.remove(b)
            elif b.y < 100: 
                if b in combat_bullets: combat_bullets.remove(b)

        for p in combat_projectiles[:]:
            p.update()
            if pygame.Vector2(p.x, p.y).distance_to(player_combat_pos) < 20:
                dmg = max(1, 10 + boss_mod_attack)
                if active_boss_type == BOSS_TRUE_KRZYKACZ: dmg = 15
                player_hp -= dmg
                if p in combat_projectiles: combat_projectiles.remove(p)
            elif p.x < 0 or p.x > WIDTH or p.y < 0 or p.y > HEIGHT:
                if active_boss_type == BOSS_LATARNIK and latarnik_fatigue < latarnik_max_fatigue:
                    latarnik_fatigue += 1
                if p in combat_projectiles: combat_projectiles.remove(p)

        if active_boss_type == BOSS_TRUE_KRZYKACZ and player_hp < player_max_hp / 3:
            end_message = "Krzykacz cię pożarł. (GAME OVER)"
            current_state = STATE_END
        elif boss_hp <= 0:
            if active_boss_type == BOSS_LATARNIK:
                barka_sound.stop()
                clues_found["latarnia_odebrana"] = True
                current_state = STATE_DIALOGUE
                dialogue_title = "Kanonada Światła - Wygrana z Latarnikiem [CUTSCENKA]"
                dialogue_lines = [
                    "Latarnik wyje i zapada się.",
                    "Drozd podnosi latarnię gasząc chochlika.",
                    "Z głębi lasu dobiega ryk. OBUDZIŁEŚ Krzykacza!",
                    "Jednak demon jest teraz znacznie SŁABSZY."
                ]
                dialogue_choices = [("Zabezpiecz latarnię", "LEAVE")]
                current_choice_idx = 0
                for m in monster_triggers_forest:
                    if m["type"] == active_boss_type: m["beaten"] = True
                slavic_sound.play(loops=-1, fade_ms=500)
                combat_projectiles.clear()
                combat_bullets.clear()
                continue
            elif active_boss_type == BOSS_TRUE_KRZYKACZ:
                end_message = "Zabiłeś Krzykacza! Prastara obrona lasu padła...\nDrwale z urzędu wkrótce zetną wszystko. Las umrze, ale Choły są bezpieczne."
                current_state = STATE_END
            elif active_boss_type == BOSS_MAMUNA:
                for m in monster_triggers_forest:
                    if m["type"] == active_boss_type: m["beaten"] = True
                current_state = STATE_DIALOGUE
                dialogue_title = "Zwycięstwo nad Mamuną"
                dialogue_lines = ["Mamuna z krzykiem rozpływa się..."]
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
            if active_boss_type == BOSS_LATARNIK: barka_sound.stop()
            end_message = "Ciało Drozda dołączyło do rosnącej listy ofiar Przeklętego Lasu..."
            current_state = STATE_END

    # WALKA - RUNNER
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
            end_message = "Potknąłeś się, a pnącza wciągnęły cię pod ziemię. (GAME OVER)"
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
                    if len(dialogue_choices) > 0: current_choice_idx = (current_choice_idx - 1) % len(dialogue_choices)
                elif event.key in [pygame.K_s, pygame.K_DOWN] and not c_code: 
                    if len(dialogue_choices) > 0: current_choice_idx = (current_choice_idx + 1) % len(dialogue_choices)
                elif event.key in [pygame.K_RETURN, pygame.K_e, pygame.K_SPACE] or c_code:
                    if not c_code and len(dialogue_choices) > 0: c_code = dialogue_choices[current_choice_idx][1]
                    
                    if c_code == "LEAVE":
                        if current_map == "VILLAGE":
                            if active_house and "Wóz" in active_house.name:
                                current_state = STATE_EXPLORE
                                player_pos.y += 30
                                active_house = None # <--- NAPRAWA: Zrzucenie zaznaczenia po wyjściu z Wozu
                            else:
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

                    # --- ZADANIA I TESTY ---
                    elif c_code == "RETURN_TO_VILLAGE_ACT2":
                        clues_found["powrot_do_cholow"] = True
                        current_map = "VILLAGE"
                        current_state = STATE_EXPLORE
                        player_pos = pygame.Vector2(WIDTH//2, HEIGHT//2)
                        continue

                    elif c_code == "TAKE_BIMBER":
                        clues_found["ma_bimber"] = True
                        dialogue_title = "Przedmiot"
                        dialogue_lines = ["Zabrałeś butlę mocarnego bimbru."]
                        dialogue_choices = [("Schowaj", "LEAVE")]
                        current_choice_idx = 0
                        continue
                        
                    elif c_code == "START_SMROD_QUEST":
                        clues_found["rozmowa_zielarka_smrod"] = True
                        dialogue_title = "Nowe Zadanie"
                        dialogue_lines = ["Przynieś Zgniły Grzyb z cienia kapliczki."]
                        dialogue_choices = [("Ruszaj", "LEAVE")]
                        current_choice_idx = 0
                        continue
                        
                    elif c_code == "TEST_AGILITY_GRZYB":
                        roll = random.randint(1, 6) + random.randint(1, 6) + player_agility
                        if roll >= 8:
                            clues_found["ma_zgnily_grzyb"] = True
                            dialogue_title = "Zręczność: Sukces!"
                            dialogue_lines = [f"Wynik: {roll}. Chwytasz grzyb unikając żmii!"]
                            dialogue_choices = [("Wróć", "LEAVE")]
                        else:
                            player_hp -= 20
                            clues_found["ma_zgnily_grzyb"] = True
                            dialogue_title = "Zręczność: Porażka!"
                            dialogue_lines = [f"Wynik: {roll}. Żmija cię ugryzła (-20 HP), ale masz grzyb."]
                            dialogue_choices = [("Opatrz", "LEAVE")]
                        current_choice_idx = 0
                        continue
                        
                    elif c_code == "TAKE_MIKSTURA":
                        clues_found["ma_miksture_smrodu"] = True
                        dialogue_title = "Gotowe"
                        dialogue_lines = ["Masz śmierdzącą breję."]
                        dialogue_choices = [("Idź", "LEAVE")]
                        current_choice_idx = 0
                        continue
                        
                    elif c_code == "DRWALE_CHARISMA":
                        roll = random.randint(1, 6) + random.randint(1, 6) + player_charisma
                        if roll >= 10:
                            end_message = f"Zastraszyłeś drwali opowieściami!\nUratowałeś wieś. (PRAWDZIWE ZAKOŃCZENIE)"
                            current_state = STATE_END
                        else:
                            player_hp -= 15
                            dialogue_title = "Charyzma: Porażka!"
                            dialogue_lines = [f"Wynik: {roll}. Szef rzucił w ciebie polanem (-15 HP)."]
                            dialogue_choices = [("Wycofaj się", "LEAVE_WINDOW")]
                            current_choice_idx = 0
                        continue
                        
                    elif c_code == "DRWALE_BIMBER":
                        clues_found["drwale_przekonani"] = True
                        end_message = "Drwale obalili bimber i uciekli po twoich strasznych opowieściach.\n(DOBRE ZAKOŃCZENIE)"
                        current_state = STATE_END
                        continue
                        
                    elif c_code == "DRWALE_SMROD":
                        clues_found["drwale_przekonani"] = True
                        end_message = "Drwale uciekli od smrodu! Uratowałeś Choły.\n(SPRYTNE ZAKOŃCZENIE)"
                        current_state = STATE_END
                        continue

                    elif c_code == "LUSIA_TALK":
                        dialogue_title = "Rozmowa z Lusią"
                        dialogue_lines = ["'Nie ufam ci. Gdybyś przyniósł mi coś słodkiego, to może...'"]
                        dialogue_choices = [("Zostaw ją", "LEAVE")]
                        current_choice_idx = 0
                        continue
                        
                    elif c_code == "LUSIA_GIVE_CANDY":
                        clues_found["wspolpraca_z_lusia"] = True
                        player_sanity = min(player_max_sanity, player_sanity + 30)
                        dialogue_title = "Zaufanie Patronki Lasu"
                        dialogue_lines = ["'Jesteś fajny, Drozd! Jak las będzie chciał ci zrobić krzywdę, pomogę.' (+30 Poczytalności)"]
                        dialogue_choices = [("Dzięki.", "LEAVE")]
                        current_choice_idx = 0
                        continue
                        
                    elif c_code == "LUSIA_TALK_TRUST":
                        dialogue_title = "Lusia"
                        dialogue_lines = ["'Pamiętaj, las cały czas nas słucha...'"]
                        dialogue_choices = [("Do zobaczenia", "LEAVE")]
                        current_choice_idx = 0
                        continue
                    
                    elif c_code == "BUY_CANDY":
                        if player_money >= 5:
                            player_money -= 5
                            clues_found["ma_cukierki"] = True
                            dialogue_title = "Zakup"
                            dialogue_lines = ["Kupiłeś cukierki."]
                        else:
                            dialogue_title = "Brak gotówki"
                            dialogue_lines = ["Sprzedawca: Za darmo nie ma!"]
                        dialogue_choices = [("Wróc", "RETURN_SKLEP")]
                        current_choice_idx = 0
                        continue

                    elif c_code == "BUY_WINE":
                        if player_money >= 10:
                            player_money -= 10
                            clues_found["ma_tanie_wino"] = True
                            dialogue_title = "Zakup"
                            dialogue_lines = ["Kupiłeś mętne wino."]
                        else:
                            dialogue_title = "Brak gotówki"
                            dialogue_lines = ["Sprzedawca: Na zeszyt nie daję!"]
                        dialogue_choices = [("Wróc", "RETURN_SKLEP")]
                        current_choice_idx = 0
                        continue
                        
                    elif c_code == "RETURN_SKLEP":
                        t, c = get_sklep_dialogue()
                        dialogue_title = "Sklep"
                        dialogue_lines = [t]
                        dialogue_choices = c
                        current_choice_idx = 0
                        continue
                    
                    elif c_code == "DRWALE_MENELE":
                        clues_found["drwale_przekonani"] = True
                        end_message = "Menele po wypiciu wina przegonili drwali!\nUratowałeś Choły! (ZAKOŃCZENIE: PATOLOGICZNE WSPARCIE)"
                        current_state = STATE_END
                        continue
                        
                    elif c_code == "TEST_AGILITY_WINDOW":
                        roll = random.randint(1, 6) + random.randint(1, 6) + player_agility
                        if roll >= 9:
                            clues_found["podslyszano_soltysa"] = True
                            clues_found["zna_sekretny_schowek"] = True
                            dialogue_title = "Zręczność: Sukces!"
                            dialogue_lines = ["Słyszysz: 'Miastowy nie może znaleźć sztyletu w kapliczce.'"]
                            dialogue_choices = [("Zanotuj", "LEAVE_WINDOW")]
                        else:
                            player_hp -= 15
                            dialogue_title = "Zręczność: Porażka!"
                            dialogue_lines = ["Wypada na ciebie wściekły pies (-15 HP)."]
                            dialogue_choices = [("Uciekaj!", "LEAVE_WINDOW")]
                        current_choice_idx = 0
                        continue

                    elif c_code == "TEST_CHARISMA_ZIELARKA":
                        roll = random.randint(1, 6) + random.randint(1, 6) + player_charisma
                        if roll >= 9:
                            clues_found["zaufanie_zielarki"] = True
                            clues_found["klamstwo_zielarka_sukces"] = True
                            dialogue_title = "Charyzma: Sukces!"
                            dialogue_lines = ["'Dobrze... Szukaj w piecu spalonej chaty.'"]
                            dialogue_choices = [("Dobrze", "LEAVE")]
                        else:
                            clues_found["klamstwo_zielarka_porazka"] = True
                            clues_found["quest_zielarka_zaczety"] = True
                            dialogue_title = "Charyzma: Porażka!"
                            dialogue_lines = ["'Kłamiesz... Przynieś mi moją księgę od Maćka, to ci powiem.'"]
                            dialogue_choices = [("Zgoda.", "LEAVE")]
                        current_choice_idx = 0
                        continue

                    elif c_code == "ZAPYTAC_MACKA_O_KSIEGE":
                        dialogue_title = "Odzyskanie Księgi"
                        dialogue_lines = ["Maciek: 'Weź ją, niech się udławi.'"]
                        dialogue_choices = [("Zabierz", "WEZ_KSIEGE")]
                        current_choice_idx = 0
                        continue
                        
                    elif c_code == "WEZ_KSIEGE":
                        clues_found["ma_ksiege_zielarki"] = True
                        dialogue_title = "Zdobycz"
                        dialogue_lines = ["Otrzymałeś księgę."]
                        dialogue_choices = [("Odejdź", "LEAVE")]
                        current_choice_idx = 0
                        continue
                        
                    elif c_code == "ODDAJ_KSIEGE_ZIELARCE":
                        clues_found["zaufanie_zielarki"] = True
                        dialogue_title = "Dług spłacony"
                        dialogue_lines = ["Zielarka: 'Przeszukaj piec w spalonej chacie.'"]
                        dialogue_choices = [("Ruszaj", "LEAVE")]
                        current_choice_idx = 0
                        continue

                    elif c_code == "CLUE_DAGGER": 
                        clues_found["zardzewialy_sztylet"] = True
                        dialogue_title = "Zdobycz!"
                        dialogue_lines = ["Zabrałeś Zardzewiały Sztylet..."]
                        dialogue_choices = [("Schowaj", "LEAVE")]
                        current_choice_idx = 0
                        continue
                        
                    elif c_code == "SHOW_DAGGER":
                        dialogue_title = "Zaufanie Sołtysa"
                        dialogue_lines = ["'Idź do starej Zielarki.'"]
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
                        dialogue_lines = ["Znalazłeś sakiewkę (+20 zł) i kamień szlifierski (+5 Atak)!"]
                        dialogue_choices = [("Świetnie!", "LEAVE")]
                        current_choice_idx = 0
                        continue
                        
                    elif c_code and c_code.startswith("PAY_"):
                        if player_money >= 5:
                            player_money -= 5
                            if c_code == "PAY_ZIELARKA": 
                                clues_found["zaufanie_zielarki"] = True
                                dialogue_title = "Wiedza kupiona"
                                dialogue_lines = ["'Przeszukaj piec w spalonej chacie...'"]
                            elif c_code == "PAY_SOLTYS":
                                clues_found["zaufanie_soltysa"] = True
                                dialogue_title = "Zaufanie kupione"
                                dialogue_lines = ["'Idź do Zielarki. Powiedz, że ja przysłałem.'"]
                            dialogue_choices = [("Ruszaj", "LEAVE")]
                            current_choice_idx = 0
                            continue
                        else:
                            dialogue_title = "Brak Gotówki"
                            dialogue_lines = ["Nie masz złota..."]
                            dialogue_choices = [("Odejdź...", "LEAVE")]
                            current_choice_idx = 0
                            continue
                            
                    elif c_code == "CLUE_KOSCI": 
                        clues_found["dowod_kosci"] = True
                        player_sanity -= 20
                        dialogue_title = "Makabryczne Odkrycie"
                        dialogue_lines = ["Zabezpieczasz nadpalone kości odmieńca. (-20 Poczytalności)"]
                        dialogue_choices = [("Schowaj", "LEAVE")]
                        current_choice_idx = 0
                        continue

                    elif c_code == "GET_UPOWAZNIENIE":
                        clues_found["ma_upowaznienie_maciek"] = True
                        dialogue_title = "Zdobyto dokument!"
                        dialogue_lines = ["Otrzymałeś upoważnienie do Choroszczy."]
                        dialogue_choices = [("Odejdź", "LEAVE")]
                        current_choice_idx = 0
                        continue

                    elif c_code == "GO_CHOROSZCZ":
                        dialogue_title = "Choroszcz"
                        dialogue_lines = ["Maria: 'To Mamuna! Ignoruj iluzje i celuj w prawdziwe ciało!'"]
                        dialogue_choices = [("Przyjmuję to.", "RETURN_FROM_CHOROSZCZ")]
                        current_choice_idx = 0
                        continue

                    elif c_code == "RETURN_FROM_CHOROSZCZ":
                        clues_found["wiedza_o_mamunie"] = True
                        current_state = STATE_EXPLORE
                        player_pos.y += 30
                        continue

                    elif c_code == "TRIGGER_MOB_EVENT":
                        dialogue_title = "Środek Nocy - Bunt!"
                        dialogue_lines = ["Lusia: 'Drozd, wstawaj! Chłopi idą cię spalić!'"]
                        dialogue_choices = [
                            ("Zaakceptuj pomoc (Teleport)", "MOB_LUSIA_HELP"),
                            ("Uciekaj oknem (Zręczność)", "MOB_ESCAPE_FOREST"),
                            ("Biegnij do Żuka (Zręczność)", "MOB_ESCAPE_CAR")
                        ]
                        current_choice_idx = 0
                        continue

                    elif c_code == "MOB_LUSIA_HELP":
                        clues_found["wspolpraca_z_lusia"] = True
                        dialogue_title = "Teleportacja"
                        dialogue_lines = ["Świat wiruje!"]
                        dialogue_choices = [("Rozejrzyj się", "GO_TO_STRANGE_PLACE_FROM_MOB")]
                        current_choice_idx = 0
                        continue

                    elif c_code == "MOB_ESCAPE_FOREST":
                        roll = random.randint(1, 6) + random.randint(1, 6) + player_agility
                        if roll >= 7:
                            dialogue_title = "Zręczność: Sukces!"
                            dialogue_lines = ["Wyskoczyłeś do ciemnego lasu..."]
                            dialogue_choices = [("Biegnij dalej", "MEET_DZIADEK_DIALOGUE")]
                            current_choice_idx = 0
                        else:
                            end_message = "Zostałeś zlinczowany. (GAME OVER)"
                            current_state = STATE_END
                        continue

                    elif c_code == "MOB_ESCAPE_CAR":
                        roll = random.randint(1, 6) + random.randint(1, 6) + player_agility
                        if roll >= 8:
                            end_message = "Uciekłeś do Wrocławia. (ZAKOŃCZENIE: TCHÓRZLIWA UCIECZKA)"
                            current_state = STATE_END
                        else:
                            end_message = "Żuk nie odpalił. Zostałeś zlinczowany. (GAME OVER)"
                            current_state = STATE_END
                        continue

                    elif c_code == "MEET_DZIADEK_DIALOGUE":
                        dialogue_title = "Gąszcz"
                        dialogue_lines = ["Leśny Dziadek: 'Intruz! Kim jesteś?!'"]
                        dialogue_choices = [
                            ("Jestem Drozd! (Prawda)", "DZIADEK_TRUTH"),
                            ("Jestem demonem! (Charyzma)", "DZIADEK_LIE")
                        ]
                        current_choice_idx = 0
                        continue

                    elif c_code == "DZIADEK_TRUTH":
                        end_message = "Leśny Dziadek łamie ci kark. (GAME OVER)"
                        current_state = STATE_END
                        continue

                    elif c_code == "DZIADEK_LIE":
                        roll = random.randint(1, 6) + random.randint(1, 6) + player_charisma
                        if roll >= 7:
                            dialogue_title = "Charyzma: Sukces!"
                            dialogue_lines = ["Dziadek: 'Chodź ze mną w głąb puszczy.'"]
                            dialogue_choices = [("Podążaj", "GO_TO_STRANGE_PLACE_FROM_MOB")]
                            current_choice_idx = 0
                        else:
                            end_message = "Dziadek ci nie wierzy i cię dusi. (GAME OVER)"
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
                        dialogue_lines = ["Rany zagojone, umysł spokojny."]
                        dialogue_choices = [("Wstań", "LEAVE")]
                        current_choice_idx = 0
                        continue
                        
                    elif c_code == "GO_TO_FOREST":
                        current_state = STATE_TRANSITION
                        continue
                    
                    elif c_code == "INFO_LATARNIK":
                        dialogue_title = "Wiedza Demona Pnia"
                        dialogue_lines = ["Pień: Odebranie mu latarni przedwcześnie SPROWOKUJE Krzykacza, ale go osłabi!"]
                        dialogue_choices = [("Zrozumiałem.", "CROSS_DECISION")]
                        current_choice_idx = 0
                        clues_found["rozmowa_pien"] = True
                        continue
                    elif c_code == "INFO_KRZYKACZ_LAIR":
                        dialogue_title = "Wiedza Gawrona"
                        dialogue_lines = ["Gawron: Bez latarni Krzykacz cię zmasakruje."]
                        dialogue_choices = [("Zrozumiałem.", "CROSS_DECISION")]
                        current_choice_idx = 0
                        clues_found["rozmowa_gawron"] = True
                        continue
                    elif c_code == "INFO_LUSIA":
                        dialogue_title = "Tajemnica Lusi"
                        dialogue_lines = ["Skrzekacz: Lusia to patronka lasu!"]
                        dialogue_choices = [("Rozumiem.", "CROSS_DECISION")]
                        current_choice_idx = 0
                        clues_found["rozmowa_skrzekacz"] = True
                        continue
                    elif c_code == "CROSS_DECISION":
                        dialogue_title = "Wybierz Ścieżkę"
                        dialogue_lines = ["Co robisz dalej?"]
                        dialogue_choices = [("Eksploruj", "LEAVE")]
                        if clues_found["rozmowa_pien"] and not clues_found["latarnia_odebrana"]: dialogue_choices.append(("Idź do Latarnika", "START_LATARNIK_FIGHT"))
                        if clues_found["rozmowa_gawron"]: dialogue_choices.append(("Idź do Krzykacza", "START_KRZYKACZ_FIGHT"))
                        if clues_found["rozmowa_skrzekacz"]: dialogue_choices.append(("Werbuj Lusię", "RECRUIT_LUSIA"))
                        current_choice_idx = 0
                        continue

                    elif c_code == "RECRUIT_LUSIA":
                        clues_found["wspolpraca_z_lusia"] = True
                        dialogue_title = "Pomoc Patronki"
                        dialogue_lines = ["Teleport prosto do Latarnika!"]
                        dialogue_choices = [("Zawalcz z nim", "START_LATARNIK_FIGHT")]
                        current_choice_idx = 0
                        continue

                    elif c_code == "START_GENERIC_FIGHT":
                        current_state = STATE_COMBAT
                        boss_hp = boss_max_hp = 150
                        boss_mod_attack = 0
                        combat_timer = 0
                        combat_projectiles.clear()
                        combat_bullets.clear()
                        continue
                    
                    elif c_code == "GIVE_AMULET":
                        dialogue_title = "Osłabienie Latarnika"
                        dialogue_lines = ["Jego światło przygasa!"]
                        dialogue_choices = [("Zakończ to!", "START_LATARNIK_FIGHT")]
                        current_choice_idx = 0
                        continue

                    elif c_code.startswith("START_LATARNIK_FIGHT"):
                        slavic_sound.stop()
                        barka_sound.play(loops=-1, fade_ms=300)
                        current_state = STATE_COMBAT
                        active_boss_type = BOSS_LATARNIK
                        latarnik_fatigue = 0
                        boss_hp = boss_max_hp = 200
                        boss_mod_attack = -2 if clues_found["ma_amulet_zielarki"] else 2
                        mod_attack = 0 if clues_found["wspolpraca_z_lusia"] else -2
                        combat_timer = 0
                        combat_projectiles.clear()
                        combat_bullets.clear()
                        continue

                    elif c_code == "FIGHT_MAMUNA":
                        current_state = STATE_COMBAT
                        active_boss_type = BOSS_MAMUNA
                        boss_hp = boss_max_hp = 180
                        boss_mod_attack = 2
                        combat_timer = 0
                        combat_projectiles.clear()
                        combat_bullets.clear()
                        continue
                        
                    elif c_code == "SPARE_MAMUNA":
                        dialogue_title = "Pakt z Mamuną"
                        dialogue_lines = ["'Las ci tego nie zapomni.'"]
                        dialogue_choices = [("Opuść leże", "LEAVE_MAMUNA_PEACE")]
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
                        dialogue_title = "Duch Lasu"
                        dialogue_lines = ["Dziadek: 'Obudzimy Krzykacza by zabił drwali!'"]
                        if clues_found.get("latarnia_odebrana", False): dialogue_lines.append("[Latarnia pulsuje. Krzykacz się rzuca!]")
                        dialogue_choices = [
                            ("Atakuj Dziadka! (Trudne)", "TREE_FIGHT_DZIADEK"),
                            ("Okłam ich (Charyzma)", "TREE_LIE_1")
                        ]
                        if clues_found.get("wspolpraca_z_lusia", False) or clues_found.get("z_lusia", False):
                            dialogue_choices.append(("Przekonaj Lusię (+2 Charyzma)", "TREE_LUSIA"))
                        if clues_found.get("zardzewialy_sztylet", False):
                            dialogue_choices.append(("[PRZEDMIOT] Wbij Sztylet w Drzewo!", "TREE_STAB"))
                        current_choice_idx = 0
                        player_pos.y += 20 
                        continue

                    elif c_code == "TREE_STAB":
                        dialogue_title = "Krzykacz Przebudzony!"
                        dialogue_lines = ["Z otchłani wynurza się gigantyczny wilk z czaszką jelenia."]
                        if clues_found.get("latarnia_odebrana", False):
                            dialogue_lines.append("Potwór jest ODRATOWANY ze swej potęgi!")
                        else:
                            dialogue_lines.append("Demon jest w PEŁNI MOCY!")
                        dialogue_choices = [("Zawalcz!", "START_KRZYKACZ_FIGHT")]
                        current_choice_idx = 0
                        continue
                        
                    elif c_code == "START_KRZYKACZ_FIGHT":
                        current_state = STATE_COMBAT
                        active_boss_type = BOSS_TRUE_KRZYKACZ
                        if clues_found.get("latarnia_odebrana", False):
                            boss_hp = boss_max_hp = 150
                            boss_mod_attack = 1
                        else:
                            boss_hp = boss_max_hp = 300
                            boss_mod_attack = 5
                        combat_timer = 0
                        combat_projectiles.clear()
                        combat_bullets.clear()
                        continue

                    elif c_code == "TREE_FIGHT_DZIADEK":
                        current_state = STATE_RUNNER
                        runner_mode_vines = False
                        runner_dziadek_hp = runner_dziadek_max_hp = 150
                        runner_obstacles.clear()
                        runner_timer = 0
                        runner_player_vy = 0
                        runner_player_y = HEIGHT - 150
                        runner_bolts.clear()
                        continue

                    elif c_code == "TREE_LIE_1":
                        roll = random.randint(1,6) + random.randint(1,6) + player_charisma
                        if roll >= 7:
                            dialogue_title = "Charyzma (Sukces!)"
                            dialogue_lines = ["Duch: 'Czuję kłamstwo. Przekonaj mnie (Rzut 5+).'"]
                            dialogue_choices = [("Rzut", "TREE_LIE_2")]
                            current_choice_idx = 0
                        else:
                            dialogue_title = "Charyzma (Porażka!)"
                            dialogue_lines = ["Dziadek atakuje!"]
                            dialogue_choices = [("Uciekaj!", "TREE_FIGHT_DZIADEK")]
                            current_choice_idx = 0
                        continue

                    elif c_code == "TREE_LIE_2":
                        roll = random.randint(1,6)
                        if roll >= 5:
                            dialogue_title = "Odroczenie"
                            dialogue_lines = ["Udało się. Masz 3 dni by przegonić drwali z Chołów!"]
                            dialogue_choices = [("Wróć szybko do wioski!", "RETURN_TO_VILLAGE_ACT2")]
                            current_choice_idx = 0
                        else:
                            dialogue_title = "Porażka"
                            dialogue_lines = ["Pnącza atakują!"]
                            dialogue_choices = [("Uciekaj!", "TREE_FIGHT_DZIADEK_HARD")]
                            current_choice_idx = 0
                        continue

                    elif c_code == "TREE_LUSIA":
                        roll = random.randint(1,6) + random.randint(1,6) + player_charisma + 2
                        if roll >= 8:
                            dialogue_title = "Wsparcie"
                            dialogue_lines = ["Lusia wynegocjowała 3 dni odroczenia! Przegnaj drwali!"]
                            dialogue_choices = [("Wróć do wioski!", "RETURN_TO_VILLAGE_ACT2")]
                            current_choice_idx = 0
                        else:
                            dialogue_title = "Zdrada!"
                            dialogue_lines = ["Lusia: 'To zdrajca!'"]
                            dialogue_choices = [("Uciekaj!", "TREE_FIGHT_DZIADEK_HARD")]
                            current_choice_idx = 0
                        continue
                        
                    elif c_code == "TREE_FIGHT_DZIADEK_HARD":
                        current_state = STATE_RUNNER
                        runner_mode_vines = True
                        runner_dziadek_hp = runner_dziadek_max_hp = 180
                        runner_obstacles.clear()
                        runner_timer = 0
                        runner_player_vy = 0
                        runner_player_y = HEIGHT - 150
                        runner_bolts.clear()
                        continue

            elif current_state == STATE_DICE_ROLL:
                if event.key in [pygame.K_RETURN, pygame.K_SPACE]:
                    current_state = STATE_COMBAT
                    combat_timer = 0
                    combat_projectiles.clear()
                    combat_bullets.clear()
                    player_combat_pos = pygame.Vector2(WIDTH//2, HEIGHT//2 + 150)

            elif current_state == STATE_END:
                if event.key == pygame.K_ESCAPE: running = False

    # 3. RENDEROWANIE (HIGH RES PIXEL ART)
    if current_state == STATE_INTRO:
        screen.fill(C_BLACK)
        game_surface.fill(C_BLACK)
        
        if intro_step == 0:
            for i in range(15): 
                tx = S((i*150 - anim_tick*6) % (WIDTH + 300) - 150)
                draw_tree(game_surface, tx, LOW_H - S(120))
            
            draw_zuk(game_surface, S(WIDTH // 2), LOW_H - S(80), light=True)
            
            for _ in range(60):
                rx, ry = random.randint(0, LOW_W), random.randint(0, LOW_H)
                pygame.draw.line(game_surface, C_GRAY, (rx, ry), (rx - S(15), ry + S(35)), 1)
                
        elif intro_step == 1:
            for i in range(12): 
                draw_tree(game_surface, S(30 + i*100 * SCALE_F), LOW_H - S(150))
            
            draw_zuk(game_surface, S(WIDTH // 2), LOW_H - S(100), light=(anim_tick % 60 < 40))
            
        apply_atmosphere(game_surface)
        screen.blit(pygame.transform.scale(game_surface, (WIDTH, HEIGHT)), (0, 0))
        
        pygame.draw.rect(screen, (10, 10, 10), (0, HEIGHT - 200, WIDTH, 200))
        pygame.draw.rect(screen, C_GRAY, (0, HEIGHT - 200, WIDTH, 200), 2)
        y_pos = HEIGHT - 180
        y_pos += draw_text_wrapped(screen, intro_sequence[intro_step]["title"], font_title, C_LIGHT, 80, y_pos, WIDTH - 160) + 10
        draw_text_wrapped(screen, intro_sequence[intro_step]["text"], font_main, C_GRAY, 80, y_pos, WIDTH - 160)
        screen.blit(font_sub.render("[Spacja / Enter]", True, C_DARK), (WIDTH - 200, HEIGHT - 40))
            
    elif current_state == STATE_TRANSITION:
        screen.fill(C_BLACK)
        for i in range(5):
            col = (20 + i*40, 20 + i*40, 20 + i*40)
            pygame.draw.rect(screen, col, (WIDTH//2 - 100 + i*20, HEIGHT//2, S(15), S(15)))
        screen.blit(font_title.render("Wejście w mrok...", True, C_GRAY), (WIDTH//2 - 120, HEIGHT - 180))

    elif current_state in [STATE_EXPLORE, STATE_HOUSE, STATE_DIALOGUE, STATE_DICE_ROLL]:
        game_surface.fill(C_BLACK)
        fx_surface.fill((0, 0, 0, 0))
        
        if current_map == "VILLAGE":
            if current_state == STATE_HOUSE or (current_state == STATE_DIALOGUE and active_house is not None and "Wóz" not in active_house.name):
                room_r = pygame.Rect(S(50), S(50), S(WIDTH - 100), S(HEIGHT - 100))
                pygame.draw.rect(game_surface, (25, 20, 20), room_r)
                floor_y = S(HEIGHT//2 + 50)
                floor_poly = [(S(50), floor_y), (S(WIDTH-50), floor_y), (S(WIDTH-50), S(HEIGHT-50)), (S(50), S(HEIGHT-50))]
                pygame.draw.polygon(game_surface, (35, 25, 20), floor_poly)
                for i in range(S(50), S(WIDTH-50), S(40)):
                    pygame.draw.line(game_surface, C_VOID, (i, floor_y), (i - S(30), S(HEIGHT-50)), 2)
                pygame.draw.rect(game_surface, C_BLACK, room_r, 4)
                pygame.draw.line(game_surface, C_BLACK, (S(50), floor_y), (S(WIDTH-50), floor_y), 4)

                hx, hy = S(WIDTH//2), S(HEIGHT//2)
                h_name = active_house.name if active_house else ""
                
                if "Sołtys" in h_name:
                    pygame.draw.rect(game_surface, C_VOID, (hx - S(60), hy + S(10), S(120), S(40)))
                    pygame.draw.rect(game_surface, C_BLACK, (hx - S(60), hy + S(10), S(120), S(40)), 2)
                    draw_npc_soltys(game_surface, hx, hy)
                    pygame.draw.rect(game_surface, (40, 80, 40), (hx - S(30), hy, S(8), S(15)))
                elif "Zielark" in h_name:
                    pygame.draw.ellipse(game_surface, C_BLACK, (hx - S(40), hy + S(20), S(40), S(30)))
                    pygame.draw.ellipse(game_surface, C_DARK, (hx - S(40), hy + S(20), S(40), S(30)), 2)
                    pygame.draw.ellipse(game_surface, (50, 100, 30), (hx - S(35), hy + S(22), S(30), S(10)))
                    draw_npc_zielarka(game_surface, hx + S(20), hy + S(10))
                elif "Pleban" in h_name:
                    pygame.draw.rect(game_surface, C_BROWN, (hx - S(30), hy + S(20), S(60), S(10)))
                    pygame.draw.rect(game_surface, C_BLACK, (hx - S(25), hy + S(30), S(5), S(20)))
                    pygame.draw.rect(game_surface, C_BLACK, (hx + S(20), hy + S(30), S(5), S(20)))
                    draw_npc_maciek(game_surface, hx, hy)
                elif "Sklep" in h_name:
                    pygame.draw.rect(game_surface, C_VOID, (hx - S(80), hy + S(20), S(160), S(30)))
                    pygame.draw.rect(game_surface, C_BLACK, (hx - S(80), hy + S(20), S(160), S(30)), 2)
                    draw_npc_sprzedawca(game_surface, hx, hy)
                elif "Mikołaj" in h_name:
                    pygame.draw.rect(game_surface, C_VOID, (hx - S(40), hy + S(20), S(80), S(30)))
                    draw_lusia(game_surface, hx + S(20), hy + S(15))

            else:
                game_surface.blit(low_terrain_surface, (0, 0))
                for tx, ty in decorations_trees: draw_tree(game_surface, S(tx), S(ty))
                draw_well(game_surface, S(490), S(420))
                
                if clues_found.get("powrot_do_cholow") and not clues_found.get("drwale_przekonani"):
                    pygame.draw.rect(game_surface, C_BROWN, (S(WIDTH//2 - 50), S(30), S(100), S(80)))
                    pygame.draw.rect(game_surface, C_BLACK, (S(WIDTH//2 - 50), S(30), S(100), S(80)), 2)

                for h in houses:
                    if "Wóz (Żuk)" in h.name:
                        draw_zuk(game_surface, S(h.rect.x), S(h.rect.y), light=False)
                    else:
                        draw_uncanny_house(game_surface, S(h.rect.x), S(h.rect.y), S(h.rect.width), S(h.rect.height), h.ruined)
        
        elif current_map == "FOREST":
            game_surface.fill((5, 5, 10)) 
            for tx, ty in forest_trees: draw_tree(game_surface, S(tx), S(ty))
            player_light_pos = (S(player_pos.x * SCALE_F), S(player_pos.y * SCALE_F))
            pygame.draw.circle(fx_surface, (200, 200, 180, 50), player_light_pos, S(80))
        
        elif current_map == "STRANGE_PLACE":
            game_surface.fill((2, 2, 8))
            draw_wielkie_drzewo(game_surface, S(WIDTH//2), S(HEIGHT//2 - 150))
            if clues_found.get("wspolpraca_z_lusia", False) or clues_found.get("z_lusia", False): 
                draw_lusia(game_surface, S(WIDTH//2 + 80), S(HEIGHT//2 + 50))
            draw_lesny_dziadek(game_surface, S(WIDTH//2 - 80), S(HEIGHT//2 + 50))

        if current_state in [STATE_EXPLORE, STATE_HOUSE]:
            draw_drozd(game_surface, S(player_pos.x), S(player_pos.y))

        apply_atmosphere(game_surface)
        screen.blit(pygame.transform.scale(game_surface, (WIDTH, HEIGHT)), (0, 0))
        screen.blit(pygame.transform.scale(fx_surface, (WIDTH, HEIGHT)), (0, 0))

        if current_map == "VILLAGE" and current_state == STATE_EXPLORE:
            screen.blit(font_main.render(f"Złoto: {player_money} zł", True, C_LIGHT), (20, 20))
            pygame.draw.rect(screen, C_DARK, (20, 50, 150, 15))
            pygame.draw.rect(screen, C_RED, (20, 50, 150 * (player_hp / player_max_hp), 15))
            pygame.draw.rect(screen, C_BLACK, (20, 50, 150, 15), 2)
            screen.blit(font_sub.render("Zdrowie", True, C_LIGHT), (20, 70))
            
            pygame.draw.rect(screen, C_DARK, (20, 90, 150, 15))
            pygame.draw.rect(screen, C_GRAY, (20, 90, 150 * (max(0, player_sanity) / player_max_sanity), 15))
            pygame.draw.rect(screen, C_BLACK, (20, 90, 150, 15), 2)
            screen.blit(font_sub.render("Poczytalność", True, C_LIGHT), (20, 110))
            
        elif current_state == STATE_HOUSE or (current_state == STATE_DIALOGUE and active_house is not None and "Wóz" not in active_house.name):
            house_name = active_house.name if active_house else "Wnętrze"
            screen.blit(font_title.render("Wnętrze: " + house_name, True, C_LIGHT), (70, 70))

        if current_state == STATE_DIALOGUE:
            pygame.draw.rect(screen, C_BLACK, (40, HEIGHT - 250, WIDTH - 80, 230))
            pygame.draw.rect(screen, C_GRAY, (40, HEIGHT - 250, WIDTH - 80, 230), 2)
            
            combined_dialogue = " ".join(dialogue_lines)
            avatar_x, avatar_y = 90, HEIGHT - 210
            
            if "Sołtys" in dialogue_title: draw_soltys(screen, avatar_x, avatar_y)
            elif "Zielark" in dialogue_title: draw_zielarka(screen, avatar_x, avatar_y)
            elif "Plebania" in dialogue_title or "Maciek" in combined_dialogue: draw_maciek(screen, avatar_x, avatar_y)
            elif "Choroszcz" in dialogue_title or "Maria" in combined_dialogue: draw_maria(screen, avatar_x, avatar_y)
            elif "Drwal" in dialogue_title or "Drwal" in combined_dialogue: draw_szef_drwali(screen, avatar_x, avatar_y)
            elif "Sklep" in dialogue_title or "Sprzedawca" in combined_dialogue: draw_sprzedawca(screen, avatar_x, avatar_y)
            elif "Menel" in dialogue_title or "Menel" in combined_dialogue: draw_menel(screen, avatar_x, avatar_y)
            
            current_y = HEIGHT - 230
            current_y += draw_text_wrapped(screen, dialogue_title, font_title, C_LIGHT, 140, current_y, WIDTH - 200) + 10
            current_y += draw_text_wrapped(screen, combined_dialogue, font_main, C_GRAY, 140, current_y, WIDTH - 200) + 15
            
            for idx, choice in enumerate(dialogue_choices):
                color = C_RED if idx == current_choice_idx else C_DARK
                choice_text = f"> {choice[0]}"
                current_y += draw_text_wrapped(screen, choice_text, font_main, color, 140, current_y, WIDTH - 200) + 5

        if current_state == STATE_DICE_ROLL:
            pygame.draw.rect(screen, (10, 5, 5), (150, 180, WIDTH-300, 350))
            pygame.draw.rect(screen, C_RED, (150, 180, WIDTH-300, 350), 3)
            boss_display_name = active_boss_type if active_boss_type else "MROCZNY POMIOT"
            title = font_main.render(f"ZASADZKA BESTII: {boss_display_name}", True, C_RED)
            screen.blit(title, (WIDTH//2 - title.get_width()//2, 210))
            screen.blit(font_main.render(f"Atak ({mod_attack:+d}), Witalność ({mod_stamina:+d})", True, C_GRAY), (200, 290))
            screen.blit(font_main.render("NACIŚNIJ [ENTER] BY WALCZYĆ", True, C_LIGHT), (WIDTH//2 - 150, 450))

    elif current_state == STATE_COMBAT:
        game_surface.fill(C_BLACK)
        fx_surface.fill((0, 0, 0, 0)) 
        
        for i in range(10):
            fy = S(150 + i*50)
            pygame.draw.line(game_surface, C_VOID, (S(100), fy), (S(WIDTH-100), fy + S(15)), 2)

        if active_boss_type in [BOSS_TRUE_KRZYKACZ, BOSS_KRZYKACZ_FOREST]: 
            draw_true_krzykacz(game_surface, S(WIDTH//2), S(220), anim_tick)
        elif active_boss_type == BOSS_LATARNIK: draw_monster_latarnik(game_surface, S(latarnik_pos.x), S(latarnik_pos.y), anim_tick)
        elif active_boss_type == BOSS_PIEN: draw_monster_pien(game_surface, S(WIDTH//2), S(200))
        elif active_boss_type == BOSS_GAWRON: draw_monster_gawron(game_surface, S(WIDTH//2), S(200))
        elif active_boss_type == BOSS_SKRZEKACZ: draw_monster_skrzekacz(game_surface, S(WIDTH//2), S(200))
        elif active_boss_type == BOSS_MAMUNA: draw_monster_mamuna(game_surface, S(WIDTH//2), S(200), anim_tick)

        draw_drozd(game_surface, S(player_combat_pos.x), S(player_combat_pos.y))
        for p in combat_projectiles: p.draw(game_surface)
        for b in combat_bullets: b.draw(game_surface)

        apply_atmosphere(game_surface)
        screen.blit(pygame.transform.scale(game_surface, (WIDTH, HEIGHT)), (0, 0))
        if active_boss_type == BOSS_LATARNIK:
            screen.blit(pygame.transform.scale(fx_surface, (WIDTH, HEIGHT)), (0, 0))
        
        pygame.draw.rect(screen, C_DARK, (WIDTH//2 - 100, 50, 200, 20))
        pygame.draw.rect(screen, C_RED, (WIDTH//2 - 100, 50, 200 * (boss_hp / boss_max_hp), 20))
        pygame.draw.rect(screen, C_BLACK, (WIDTH//2 - 100, 50, 200, 20), 2)
        boss_name = active_boss_type if active_boss_type else "DEMON"
        screen.blit(font_title.render(boss_name, True, C_GRAY), (WIDTH//2 - 100, 20))
        
        pygame.draw.rect(screen, C_DARK, (20, HEIGHT - 40, 200, 20))
        pygame.draw.rect(screen, C_LIGHT, (20, HEIGHT - 40, 200 * (player_hp / player_max_hp), 20))
        pygame.draw.rect(screen, C_BLACK, (20, HEIGHT - 40, 200, 20), 2)

    elif current_state == STATE_RUNNER:
        game_surface.fill(C_BLACK)
        fx_surface.fill((0, 0, 0, 0))
        pygame.draw.line(game_surface, C_BROWN, (0, S(runner_ground_y) + S(20)), (LOW_W, S(runner_ground_y) + S(20)), S(6))
        
        draw_drozd(game_surface, S(400), S(runner_player_y))
        draw_lesny_dziadek(game_surface, S(100), S(runner_ground_y + int(math.sin(runner_timer*0.2)*5)))
        for o in runner_obstacles: o.draw(game_surface)
        for b in runner_bolts: pygame.draw.rect(game_surface, C_LIGHT, (S(b.x), S(b.y), S(10), S(3)))
        
        apply_atmosphere(game_surface)
        screen.blit(pygame.transform.scale(game_surface, (WIDTH, HEIGHT)), (0, 0))

        pygame.draw.rect(screen, C_DARK, (20, 20, 200, 20))
        pygame.draw.rect(screen, C_LIGHT, (20, 20, 200 * (player_hp / player_max_hp), 20))
        pygame.draw.rect(screen, C_DARK, (WIDTH - 220, 20, 200, 20))
        pygame.draw.rect(screen, C_RED, (WIDTH - 220, 20, 200 * (runner_dziadek_hp / runner_dziadek_max_hp), 20))
        screen.blit(font_main.render("[SPACE] - Skok  |  [E] - Strzał do tyłu", True, C_GRAY), (WIDTH//2 - 180, 60))

    elif current_state == STATE_END:
        screen.fill(C_BLACK)
        draw_text_wrapped(screen, "KONIEC GRY", font_title, C_RED, WIDTH//2 - 60, HEIGHT//2 - 100, 400)
        draw_text_wrapped(screen, end_message, font_main, C_LIGHT, WIDTH//2 - 250, HEIGHT//2 - 30, 500)
        screen.blit(font_sub.render("[ESC] - Wyjście", True, C_DARK), (WIDTH//2 - 50, HEIGHT - 100))

    pygame.display.flip()

pygame.quit()
sys.exit()
