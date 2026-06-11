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

# Konfiguracja okna bazowego
WIDTH, HEIGHT = 950, 700
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Krzykacz: Polowanie na Mamunę - Retro Horror Edition")
clock = pygame.time.Clock()

# --- NOWY KIERUNEK ARTYSTYCZNY (LOW-RES & PALETA) ---
SCALE_F = 3.0
LOW_W, LOW_H = int(WIDTH / SCALE_F), int(HEIGHT / SCALE_F) # Ok. 316x233
game_surface = pygame.Surface((LOW_W, LOW_H))
fx_surface = pygame.Surface((LOW_W, LOW_H), pygame.SRCALPHA)

# POPRAWKA: Współrzędne muszą być dzielone przez skalę, żeby zmieściły się na małym ekranie!

def S(val):
    return int(val / SCALE_F)

def S(val):
    return int(val)

# Mroczna paleta barw z przejściami tonalnymi
C_BLACK = (4, 4, 7)
C_VOID = (12, 11, 16)
C_DARK = (26, 24, 30)
C_DARK_MOSS = (18, 32, 20)
C_MOSS = (42, 65, 45)
C_BROWN_DARK = (40, 28, 22)
C_BROWN = (80, 55, 40)
C_BROWN_LIGHT = (115, 90, 70)
C_GRAY_DARK = (50, 50, 55)
C_GRAY = (105, 105, 115)
C_GRAY_LIGHT = (165, 165, 175)
C_LIGHT = (220, 215, 200)
C_RED_DARK = (100, 5, 5)
C_RED = (195, 15, 15)
C_BLOOD = (130, 0, 5)
C_GOLD_DARK = (130, 95, 25)
C_GOLD = (215, 165, 45) 
C_GOLD_LIGHT = (250, 220, 140)
C_SKIN = (230, 190, 160)
C_SKIN_SHADOW = (190, 145, 115)

def draw_pixel_line(surface, color, start, end, thickness=1):
    pygame.draw.line(surface, color, start, end, int(thickness))

def apply_dither_rect(surface, rect, color1, color2, density=2):
    for x in range(rect.x, rect.x + rect.width):
        for y in range(rect.y, rect.y + rect.height):
            if (x + y) % density == 0:
                surface.set_at((x, y), color1)
            else:
                surface.set_at((x, y), color2)

# --- PROCEDURALNY GENERATOR MUZYKI ---
def generate_slavic_theme():
    sample_rate = 44100
    notes = {
        'D3': 146.83, 'E3': 164.81, 'F3': 174.61, 'G3': 196.00,
        'A3': 220.00, 'C4': 261.63, 'D4': 293.66, 'E4': 329.63, 'F4': 349.23, 'rest': 0.0
    }
    melody = [
        ('D4', 0.2), ('D4', 0.2), ('F4', 0.2), ('E4', 0.2), 
        ('D4', 0.2), ('C4', 0.2), ('A3', 0.4),
        ('D4', 0.2), ('D4', 0.2), ('F4', 0.2), ('E4', 0.2), 
        ('G3', 0.2), ('A3', 0.2), ('D3', 0.4)
    ] * 2
    total_samples = sum(int(sample_rate * dur) for _, dur in melody)
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
            track[current_sample:current_sample+samples] += wave * env * 0.45
        current_sample += samples
    t_total = np.linspace(0, total_samples / sample_rate, total_samples, False)
    bass_track = np.zeros(total_samples)
    beat_interval = 0.4
    for i in range(int(len(track) / (sample_rate * beat_interval))):
        start = int(i * beat_interval * sample_rate)
        end = int(start + 0.15 * sample_rate)
        if end < total_samples:
            t_beat = t_total[start:end] - t_total[start]
            kick = np.sin(2 * np.pi * np.linspace(140, 30, len(t_beat)) * t_beat)
            bass_track[start:end] += kick * (np.linspace(1, 0, len(t_beat)) ** 2) * 0.8
    track += bass_track
    track = np.clip(track, -1.0, 1.0)
    track_16bit = np.int16(track * 32767)
    return np.ascontiguousarray(np.column_stack((track_16bit, track_16bit)))

def generate_barka_theme():
    sample_rate = 44100
    notes = {
        'G3': 196.00, 'A3': 220.00, 'B3': 246.94, 'C4': 261.63, 'D4': 293.66, 
        'E4': 329.63, 'F4': 349.23, 'G4': 392.00, 'A4': 440.00, 'rest': 0.0
    }
    melody = [
        ('G4', 0.3), ('C4', 0.3), ('D4', 0.3), ('E4', 0.5), ('D4', 0.3), ('C4', 0.3), ('A4', 0.6), ('rest', 0.1),
        ('A4', 0.3), ('F4', 0.3), ('G4', 0.3), ('A4', 0.5), ('G4', 0.3), ('F4', 0.3), ('E4', 0.6)
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

slavic_sound = pygame.sndarray.make_sound(generate_slavic_theme())
slavic_sound.set_volume(0.2)
slavic_sound.play(loops=-1, fade_ms=1000)

barka_sound = pygame.sndarray.make_sound(generate_barka_theme())
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

# --- BLOK DEFINICJI BOSSÓW ---
BOSS_MAMUNA = "MAMUNA (Pani Lasu)"
BOSS_LATARNIK = "LATARNIK (Zwodzący Cień)"
BOSS_PIEN = "PIEŃ (Zgniły Strażnik)"
BOSS_GAWRON = "GAWRON (Czarny Anioł)"
BOSS_SKRZEKACZ = "SKRZEKACZ (Demon)"
BOSS_KRZYKACZ_FOREST = "MŁODY KRZYKACZ"
BOSS_TRUE_KRZYKACZ = "KRZYKACZ (Ucieleśnienie Lasu)"

# --- POSTACIE (SZCZEGÓŁOWE MODELE ANATOMICZNE) ---
def draw_drozd(surface, x, y):
    pygame.draw.rect(surface, C_BLACK, (x - 6, y + 16, 4, 14))
    pygame.draw.rect(surface, C_BLACK, (x + 2, y + 16, 4, 14))
    pygame.draw.rect(surface, (15, 15, 22), (x - 9, y + 27, 7, 3))
    pygame.draw.rect(surface, (15, 15, 22), (x + 2, y + 27, 7, 3))
    coat_rect = pygame.Rect(x - 11, y - 8, 22, 25)
    pygame.draw.rect(surface, C_DARK, coat_rect)
    pygame.draw.rect(surface, C_BROWN_DARK, (x - 10, y - 7, 20, 23))
    for px in range(x - 9, x + 9, 2):
        for py in range(y - 5, y + 14, 3):
            surface.set_at((px + (py % 2), py), C_DARK)
    pygame.draw.polygon(surface, C_BLACK, [(x - 11, y - 8), (x - 4, y + 2), (x, y - 8)])
    pygame.draw.polygon(surface, C_BLACK, [(x + 11, y - 8), (x + 4, y + 2), (x, y - 8)])
    surface.set_at((x - 4, y + 4), C_GOLD)
    surface.set_at((x - 4, y + 10), C_GOLD)
    surface.set_at((x + 3, y + 4), C_GOLD)
    surface.set_at((x + 3, y + 10), C_GOLD)
    pygame.draw.rect(surface, C_RED_DARK, (x - 2, y - 8, 4, 5))
    pygame.draw.rect(surface, C_SKIN_SHADOW, (x - 7, y - 18, 14, 11))
    pygame.draw.rect(surface, C_SKIN, (x - 6, y - 18, 12, 9))
    pygame.draw.line(surface, C_SKIN_SHADOW, (x - 6, y - 18), (x + 5, y - 18))
    # Okulary, Błysk i Nos
    pygame.draw.rect(surface, C_VOID, (x - 5, y - 15, 4, 4), 1)
    pygame.draw.rect(surface, C_VOID, (x + 1, y - 15, 4, 4), 1)
    pygame.draw.line(surface, C_VOID, (x - 1, y - 14), (x + 1, y - 14))
    surface.set_at((x - 4, y - 14), (180, 240, 255))
    surface.set_at((x + 2, y - 14), (255, 255, 255))
    pygame.draw.polygon(surface, C_BROWN, [(x - 1, y - 12), (x + 1, y - 12), (x, y - 9)]) # Nos
    pygame.draw.line(surface, C_VOID, (x - 3, y - 7), (x + 3, y - 7), 1) # Usta
    pygame.draw.rect(surface, C_VOID, (x - 12, y - 21, 24, 3)) 
    pygame.draw.rect(surface, C_VOID, (x - 8, y - 35, 16, 15)) 
    pygame.draw.rect(surface, C_RED, (x - 8, y - 24, 16, 3)) 

def draw_lusia(surface, x, y):
    C_BLUE_DARK = (25, 45, 90)
    C_HAIR = (225, 185, 45)
    pygame.draw.polygon(surface, C_BLUE_DARK, [(x - 10, y + 2), (x + 10, y + 2), (x + 14, y + 26), (x - 14, y + 26)])
    for bx in range(x - 11, x + 12, 3):
        surface.set_at((bx, y + 22), C_RED)
        surface.set_at((bx + 1, y + 23), C_GOLD)
    pygame.draw.rect(surface, C_DARK, (x - 7, y - 6, 14, 9))
    pygame.draw.rect(surface, C_SKIN, (x - 4, y + 3, 8, 4))
    pygame.draw.rect(surface, C_SKIN_SHADOW, (x - 6, y - 15, 12, 10))
    pygame.draw.rect(surface, C_SKIN, (x - 5, y - 15, 10, 8))
    # Nos i Usta i Oczy
    pygame.draw.rect(surface, C_VOID, (x - 3, y - 11, 1, 1))
    pygame.draw.rect(surface, C_VOID, (x + 2, y - 11, 1, 1))
    pygame.draw.rect(surface, C_BROWN, (x, y - 9, 1, 1))
    pygame.draw.line(surface, C_BLOOD, (x - 2, y - 7), (x + 2, y - 7), 1)
    # Włosy
    for h_dot in range(y - 6, y + 14, 4):
        pygame.draw.rect(surface, C_HAIR, (x - 11, h_dot, 3, 2))
        pygame.draw.rect(surface, C_HAIR, (x + 8, h_dot, 3, 2))
    pygame.draw.line(surface, C_HAIR, (x - 5, y - 17), (x - 1, y - 15))
    pygame.draw.line(surface, C_HAIR, (x + 4, y - 17), (x, y - 15))

def draw_npc_soltys(surface, x, y):
    pygame.draw.rect(surface, C_BROWN_DARK, (x - 14, y - 2, 28, 34))
    pygame.draw.rect(surface, C_VOID, (x - 14, y + 12, 28, 4)) 
    pygame.draw.rect(surface, C_GOLD, (x - 2, y + 11, 4, 6)) 
    pygame.draw.circle(surface, C_LIGHT, (x, y - 10), 9)
    pygame.draw.polygon(surface, C_DARK, [(x - 14, y - 12), (x + 14, y - 12), (x, y - 24)])
    # Oczy i ogromny Nos
    pygame.draw.circle(surface, C_VOID, (x - 3, y - 12), 2)
    pygame.draw.circle(surface, C_VOID, (x + 3, y - 12), 2)
    pygame.draw.polygon(surface, C_BROWN_DARK, [(x - 2, y - 10), (x + 2, y - 10), (x, y - 6)]) 
    # Sumiasty wąs
    pygame.draw.polygon(surface, C_GRAY, [(x - 8, y - 6), (x + 8, y - 6), (x, y - 3)])

def draw_npc_zielarka(surface, x, y):
    pygame.draw.polygon(surface, C_DARK, [(x, y - 10), (x - 15, y + 30), (x + 15, y + 30)])
    pygame.draw.circle(surface, C_LIGHT, (x, y + 2), 8) 
    pygame.draw.polygon(surface, C_GRAY, [(x - 9, y - 4), (x + 9, y - 4), (x, y - 10)]) 
    # Haczykowaty nos, usta, oczy
    pygame.draw.line(surface, C_VOID, (x - 4, y - 1), (x - 1, y - 1), 1)
    pygame.draw.line(surface, C_VOID, (x + 1, y - 1), (x + 4, y - 1), 1)
    pygame.draw.polygon(surface, C_BROWN, [(x, y + 1), (x - 2, y + 5), (x, y + 5)])
    pygame.draw.line(surface, C_BLOOD, (x - 3, y + 7), (x + 3, y + 7), 1)
    pygame.draw.line(surface, C_BROWN, (x + 12, y - 5), (x + 12, y + 35), 2) # Kostur

def draw_npc_maciek(surface, x, y):
    pygame.draw.rect(surface, C_GRAY, (x - 11, y, 22, 30))
    pygame.draw.circle(surface, C_LIGHT, (x, y - 8), 8)
    pygame.draw.rect(surface, C_VOID, (x - 9, y - 16, 18, 5))
    pygame.draw.circle(surface, C_VOID, (x - 3, y - 9), 1)
    pygame.draw.circle(surface, C_VOID, (x + 3, y - 9), 1)
    pygame.draw.rect(surface, C_DARK, (x - 1, y - 7, 2, 3))
    pygame.draw.line(surface, C_VOID, (x - 4, y - 3), (x + 4, y - 3), 1)

def draw_npc_maria(surface, x, y):
    pygame.draw.polygon(surface, C_BLOOD, [(x, y - 2), (x - 13, y + 28), (x + 13, y + 28)])
    pygame.draw.circle(surface, C_LIGHT, (x, y - 2), 7)
    pygame.draw.circle(surface, C_VOID, (x - 2, y - 4), 1)
    pygame.draw.circle(surface, C_VOID, (x + 2, y - 4), 1)
    pygame.draw.line(surface, C_BROWN, (x, y - 3), (x, y - 1), 1)
    pygame.draw.line(surface, C_VOID, (x - 3, y + 1), (x + 3, y + 1), 1)

def draw_szef_drwali(surface, x, y):
    pygame.draw.rect(surface, C_BROWN_DARK, (x-12, y-5, 24, 25))
    pygame.draw.rect(surface, C_RED_DARK, (x-10, y-3, 20, 21))
    for i in range(x-10, x+10, 4): pygame.draw.line(surface, C_BLACK, (i, y-3), (i, y+17), 1)
    for i in range(y-3, y+17, 4): pygame.draw.line(surface, C_BLACK, (x-10, i), (x+10, i), 1)
    pygame.draw.rect(surface, C_SKIN_SHADOW, (x-6, y-12, 12, 10))
    pygame.draw.rect(surface, C_SKIN, (x-5, y-12, 10, 8))
    pygame.draw.polygon(surface, C_BROWN, [(x-2, y-10), (x+2, y-10), (x, y-6)])
    pygame.draw.circle(surface, C_VOID, (x-3, y-10), 1)
    pygame.draw.circle(surface, C_VOID, (x+3, y-10), 1)
    pygame.draw.polygon(surface, C_BROWN_DARK, [(x-7, y-5), (x+7, y-5), (x, y+6)])
    pygame.draw.ellipse(surface, C_BROWN, (x-12, y-16, 24, 6))
    pygame.draw.rect(surface, C_BROWN_DARK, (x-7, y-22, 14, 8))

def draw_sprzedawca(surface, x, y):
    pygame.draw.polygon(surface, C_VOID, [(x, y-15), (x-15, y+25), (x+15, y+25)])
    pygame.draw.rect(surface, C_BLACK, (x-12, y, 24, 25))
    surface.set_at((x-4, y-8), C_GOLD)
    surface.set_at((x+4, y-8), C_GOLD)
    surface.set_at((x-3, y-8), C_LIGHT)
    surface.set_at((x+3, y-8), C_LIGHT)
    pygame.draw.line(surface, C_SKIN, (x-8, y+5), (x, y+10), 2)
    pygame.draw.line(surface, C_SKIN, (x+8, y+5), (x, y+10), 2)

def draw_menel(surface, x, y):
    pygame.draw.polygon(surface, C_GRAY_DARK, [(x-12, y-5), (x-16, y+25), (x+12, y+25)])
    pygame.draw.line(surface, C_BLACK, (x-10, y), (x-10, y+20), 2)
    pygame.draw.line(surface, C_BLACK, (x+5, y), (x+5, y+20), 2)
    pygame.draw.rect(surface, C_BLACK, (x-6, y-12, 12, 10))
    pygame.draw.rect(surface, C_SKIN_SHADOW, (x-4, y-10, 8, 6))
    pygame.draw.rect(surface, C_RED_DARK, (x-1, y-8, 2, 2))
    surface.set_at((x-2, y-9), C_VOID)
    surface.set_at((x+2, y-9), C_VOID)
    pygame.draw.rect(surface, (10, 50, 20), (x-10, y+10, 4, 8))
    pygame.draw.line(surface, C_LIGHT, (x-9, y+10), (x-9, y+18), 1)

# --- POTWORY ---
def draw_monster_latarnik(surface, x, y, anim_tick):
    offset_y = int(math.sin(anim_tick * 0.15) * 6)
    pygame.draw.ellipse(surface, C_VOID, (x - 15, y - 20 + offset_y, 30, 50))
    pygame.draw.circle(surface, C_DARK, (x, y - 12 + offset_y), 8)
    pygame.draw.circle(surface, C_RED, (x - 3, y - 13 + offset_y), 2)
    pygame.draw.circle(surface, C_RED, (x + 3, y - 13 + offset_y), 2)
    pygame.draw.rect(surface, C_VOID, (x - 1, y - 10 + offset_y, 2, 2)) 
    pygame.draw.ellipse(surface, C_VOID, (x - 4, y - 7 + offset_y, 8, 5)) 
    pygame.draw.rect(surface, C_GOLD, (x + 15, y + offset_y, 10, 14))
    pygame.draw.circle(surface, (255, 255, 180), (x + 20, y + 7 + offset_y), 5)

def draw_monster_mamuna(surface, x, y, anim_tick):
    offset_x = int(math.sin(anim_tick * 0.1) * 5)
    pygame.draw.ellipse(surface, C_DARK, (x - 20 + offset_x, y - 10, 40, 40))
    pygame.draw.circle(surface, C_VOID, (x + offset_x, y - 15), 12)
    pygame.draw.circle(surface, C_RED, (x - 4 + offset_x, y - 18), 3)
    pygame.draw.circle(surface, C_LIGHT, (x + 4 + offset_x, y - 19), 1)
    pygame.draw.polygon(surface, C_BLACK, [(x + offset_x, y - 16), (x - 2 + offset_x, y - 12), (x + 3 + offset_x, y - 12)])
    pygame.draw.ellipse(surface, C_BLOOD, (x - 6 + offset_x, y - 10, 12, 5))
    pygame.draw.line(surface, C_LIGHT, (x - 4 + offset_x, y - 8), (x + 4 + offset_x, y - 8), 1) 

def draw_lesny_dziadek(surface, x, y):
    pygame.draw.rect(surface, C_VOID, (x - 12, y - 30, 24, 60))
    pygame.draw.polygon(surface, C_DARK, [(x - 15, y + 15), (x + 15, y + 15), (x, y - 40)])
    pygame.draw.circle(surface, C_GOLD, (x - 5, y - 15), 3)
    pygame.draw.circle(surface, C_GOLD, (x + 5, y - 15), 3)
    pygame.draw.circle(surface, C_RED, (x - 5, y - 15), 1)
    pygame.draw.circle(surface, C_RED, (x + 5, y - 15), 1)
    pygame.draw.polygon(surface, C_BROWN, [(x - 2, y - 14), (x + 2, y - 14), (x, y - 8)])
    pygame.draw.polygon(surface, C_VOID, [(x - 6, y - 5), (x + 6, y - 5), (x, y - 1)])

def draw_monster_pien(surface, x, y):
    body_poly = [(x - 40, y + 20), (x + 45, y + 25), (x + 30, y - 50), (x - 35, y - 45)]
    pygame.draw.polygon(surface, C_BROWN_DARK, body_poly)
    pygame.draw.polygon(surface, C_VOID, body_poly, 3)
    for i in range(5):
        dist = 8 + i * 6
        pygame.draw.ellipse(surface, C_BLACK, (x - dist*1.2, y - dist - 10, dist*2.4, dist*2), 2)
    korzenie = [[(x - 30, y + 15), (x - 50, y + 40), (x - 45, y + 45)], [(x - 10, y + 20), (x - 15, y + 55), (x - 5, y + 60)], [(x + 25, y + 20), (x + 40, y + 50), (x + 35, y + 55)]]
    for korz in korzenie:
        pygame.draw.polygon(surface, C_VOID, korz)
        pygame.draw.polygon(surface, C_BLACK, korz, 1)
    skull_poly = [(x - 20, y - 25), (x + 18, y - 28), (x + 15, y - 5), (x, y + 15), (x - 17, y - 8)]
    pygame.draw.polygon(surface, C_LIGHT, skull_poly)
    pygame.draw.polygon(surface, C_GRAY, skull_poly, 1)
    pygame.draw.circle(surface, C_BLACK, (x - 7, y - 15), 3)
    pygame.draw.circle(surface, C_RED, (x - 7, y - 15), 1) 
    pygame.draw.circle(surface, C_BLACK, (x + 6, y - 17), 3)
    pygame.draw.circle(surface, C_RED, (x + 6, y - 17), 1)
    draw_pixel_line(surface, C_LIGHT, (x - 15, y - 20), (x - 35, y - 40), 2)
    draw_pixel_line(surface, C_GRAY, (x + 12, y - 22), (x + 25, y - 35), 2)

def draw_monster_gawron(surface, x, y):
    wing_poly_l = [(x, y - 30), (x - 60, y - 50), (x - 40, y + 10), (x, y + 10)]
    wing_poly_r = [(x, y - 30), (x + 60, y - 50), (x + 40, y + 10), (x, y + 10)]
    pygame.draw.polygon(surface, C_VOID, wing_poly_l)
    pygame.draw.polygon(surface, C_VOID, wing_poly_r)
    skull_poly = [(x - 8, y - 45), (x + 8, y - 45), (x + 4, y - 20), (x - 4, y - 20)]
    pygame.draw.polygon(surface, C_LIGHT, skull_poly)
    beak_poly = [(x - 2, y - 25), (x + 2, y - 25), (x + 1, y - 5), (x - 10, y - 15)]
    pygame.draw.polygon(surface, C_GRAY, beak_poly)
    pygame.draw.polygon(surface, C_BLOOD, [(x - 2, y - 10), (x, y - 5), (x - 6, y - 8)], 0)
    pygame.draw.circle(surface, C_RED, (x - 3, y - 35), 1)
    pygame.draw.circle(surface, C_RED, (x + 3, y - 35), 1)

def draw_monster_skrzekacz(surface, x, y):
    pygame.draw.ellipse(surface, C_VOID, (x - 35, y - 20, 70, 45))
    pygame.draw.ellipse(surface, C_BLACK, (x - 25, y - 15, 50, 35), 2)
    legs = [[(x - 30, y - 10), (x - 55, y - 30), (x - 50, y - 35)], [(x - 30, y + 10), (x - 60, y + 30), (x - 55, y + 35)], [(x + 30, y - 10), (x + 55, y - 30), (x + 50, y - 35)], [(x + 30, y + 10), (x + 60, y + 30), (x + 55, y + 35)]]
    for leg in legs:
        pygame.draw.polygon(surface, C_VOID, leg)
    eyes = [(-15, -8), (18, -12), (-5, 10), (12, 8), (0, -15)]
    for ex, ey in eyes:
        pygame.draw.circle(surface, C_RED, (x + ex, y + ey), 2)

def draw_true_krzykacz(surface, x, y, anim_tick):
    w, h = 180, 260 
    breathe = int(math.sin(anim_tick * 0.05) * 8)
    legs = [[(x - w//3, y - h//3), (x - w, y + h//4), (x - w*0.9, y + h//3)], [(x + w//3, y - h//3), (x + w, y + h//4), (x + w*0.9, y + h//3)]]
    for leg in legs:
        pygame.draw.polygon(surface, C_VOID, leg)
    torso_poly = [(x, y - h//2 + 30), (x - w//2.5, y + h//2), (x + w//2.5, y + h//2)]
    pygame.draw.polygon(surface, C_VOID, torso_poly)
    for i in range(5):
        rib_y = y - h//2 + 60 + (i * 18) + breathe
        rib_w = 25 + i * 4
        pygame.draw.ellipse(surface, C_LIGHT, (x - rib_w//2, rib_y, rib_w, 6))
    skull_y = y - h//2 - 20 + breathe
    skull_poly = [(x - 30, skull_y), (x + 30, skull_y), (x + 5, skull_y + 50), (x - 5, skull_y + 50)]
    pygame.draw.polygon(surface, C_LIGHT, skull_poly)
    pygame.draw.circle(surface, C_BLACK, (x - 12, skull_y + 20), 5)
    pygame.draw.circle(surface, C_BLOOD, (x - 12, skull_y + 20), 2) 
    pygame.draw.circle(surface, C_BLACK, (x + 12, skull_y + 20), 5)
    pygame.draw.circle(surface, C_BLOOD, (x + 12, skull_y + 20), 2)
    draw_pixel_line(surface, C_LIGHT, (x - 20, skull_y), (x - 70, skull_y - 60), 3)
    draw_pixel_line(surface, C_LIGHT, (x + 20, skull_y), (x + 70, skull_y - 60), 3)

# --- ARCHITEKTURA I ŚRODOWISKO ---
def draw_uncanny_house(surface, x, y, width=170, height=120, ruined=False):
    if ruined:
        pygame.draw.rect(surface, (35, 30, 32), (x, y + 30, width, height - 30))
        pygame.draw.polygon(surface, C_VOID, [(x - 10, y + 30), (x + width//3, y - 10), (x + width - 20, y + 30)])
    else:
        pygame.draw.rect(surface, (90, 80, 70), (x, y, width, height))
        pygame.draw.rect(surface, C_BLACK, (x, y, width, height), 2)
        roof_poly = [(x - 20, y), (x + width // 2, y - 80), (x + width + 20, y)]
        pygame.draw.polygon(surface, (55, 45, 45), roof_poly)
        pygame.draw.polygon(surface, C_BLACK, roof_poly, 3)
        pygame.draw.rect(surface, C_BROWN_DARK, (x + width//2 - 20, y + height - 55, 40, 55))
        win_rect = pygame.Rect(x + 25, y + 30, 35, 40)
        pygame.draw.rect(surface, C_VOID, win_rect)
        apply_dither_rect(surface, pygame.Rect(x + 27, y + 32, 31, 36), (70, 50, 20), C_VOID, 2)

def draw_tree(surface, x, y):
    pygame.draw.polygon(surface, C_BLACK, [(x - 12, y + 15), (x + 14, y + 12), (x + 8, y - 60), (x + 2, y - 130), (x - 10, y - 50)])
    pygame.draw.polygon(surface, C_VOID, [(x - 6, y - 110), (x - 45, y - 140), (x - 20, y - 170), (x + 2, y - 130)])
    pygame.draw.polygon(surface, C_VOID, [(x + 4, y - 100), (x + 50, y - 120), (x + 35, y - 155), (x - 2, y - 125)])

def draw_wielkie_drzewo(surface, x, y):
    pygame.draw.polygon(surface, C_VOID, [(x-40, y+50), (x+50, y+40), (x+30, y-100), (x-45, y-90)])
    pygame.draw.polygon(surface, C_BLACK, [(x-40, y+50), (x+50, y+40), (x+30, y-100), (x-45, y-90)], 3)
    pygame.draw.circle(surface, C_RED, (x - 4, y - 50), 2)
    pygame.draw.circle(surface, C_RED, (x + 4, y - 48), 2)

def draw_well(surface, x, y):
    w, h = 55, 40
    pygame.draw.rect(surface, C_GRAY_DARK, (x - w//2, y - h//2, w, h))
    pygame.draw.line(surface, C_BROWN_DARK, (x - w//2 + 6, y - h//2), (x - w//2 + 6, y - 50), 4)
    pygame.draw.line(surface, C_BROWN_DARK, (x + w//2 - 6, y - h//2), (x + w//2 - 6, y - 50), 4)
    pygame.draw.polygon(surface, C_DARK, [(x - w//2 - 6, y - 50), (x, y - 70), (x + w//2 + 6, y - 50)])

def draw_zuk(surface, x, y, light=False):
    pygame.draw.rect(surface, (110, 110, 105), (x - 90, y - 85, 110, 50))
    pygame.draw.rect(surface, (75, 85, 95), (x - 90, y - 35, 110, 25))
    pygame.draw.rect(surface, (75, 85, 95), (x + 20, y - 70, 45, 60))
    pygame.draw.polygon(surface, C_VOID, [(x + 25, y - 62), (x + 58, y - 62), (x + 58, y - 42), (x + 25, y - 42)])
    surface.set_at((x + 35, y - 50), C_DARK)
    pygame.draw.circle(surface, (12, 12, 15), (x - 50, y + 5), 18)
    pygame.draw.circle(surface, (12, 12, 15), (x + 40, y + 5), 18)
    if light:
        light_surf = pygame.Surface((350, 160), pygame.SRCALPHA)
        pygame.draw.polygon(light_surf, (255, 240, 170, 60), [(0, 30), (350, 0), (350, 160)])
        surface.blit(light_surf, (x + 68, y - 80))

def apply_atmosphere(surface):
    vignette = pygame.Surface((LOW_W, LOW_H), pygame.SRCALPHA)
    pygame.draw.rect(vignette, (C_BLACK[0], C_BLACK[1], C_BLACK[2], 220), (0, 0, LOW_W, LOW_H), 40)
    pygame.draw.rect(vignette, (C_BLACK[0], C_BLACK[1], C_BLACK[2], 120), (40, 40, LOW_W-80, LOW_H-80), 30)
    
    fog = pygame.Surface((LOW_W, LOW_H), pygame.SRCALPHA)
    pygame.draw.rect(fog, (C_GRAY[0], C_GRAY[1], C_GRAY[2], 40), (0, LOW_H - 100, LOW_W, 100))
    surface.blit(fog, (0, 0))
    surface.blit(vignette, (0, 0))

# --- SILNIK TEKSTOWY ---
font_main = pygame.font.SysFont("Courier New", 20, bold=True)
font_sub = pygame.font.SysFont("Courier New", 15)

def draw_text_wrapped(surface, text, font, color, x, y, max_width):
    paragraphs = text.split('\n')
    y_offset = 0
    font_height = font.size('Tg')[1]
    for paragraph in paragraphs:
        words = paragraph.split(' ')
        current_line = []
        for word in words:
            test_line = ' '.join(current_line + [word])
            if font.size(test_line)[0] <= max_width:
                current_line.append(word)
            else:
                text_surface = font.render(' '.join(current_line), True, color)
                surface.blit(text_surface, (x, y + y_offset))
                y_offset += font_height + 4
                current_line = [word]
        if current_line:
            text_surface = font.render(' '.join(current_line), True, color)
            surface.blit(text_surface, (x, y + y_offset))
            y_offset += font_height + 4
    return y_offset

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
            pygame.draw.lines(surface, C_BLOOD, False, self.trail, 3)
        pygame.draw.circle(surface, self.color, (int(self.x), int(self.y)), self.radius)

class RunnerObstacle:
    def __init__(self, x, y, width, height, type_id, speed):
        self.rect = pygame.Rect(x, y, width, height)
        self.type = type_id
        self.speed = speed
        self.x = x
    def update(self):
        self.x -= self.speed
        self.rect.x = self.x
    def draw(self, surface):
        pygame.draw.rect(surface, C_BROWN if self.type == "LOG" else C_DARK, self.rect, border_radius=4)

class House:
    def __init__(self, x, y, w, h, name, dialog_func, ruined=False):
        self.rect = pygame.Rect(x, y, w, h)
        self.door_rect = pygame.Rect(x + w//2 - 30, y + h - 20, 60, 40)
        self.name = name
        self.dialog_func = dialog_func
        self.ruined = ruined

# --- DANE FABULARNE I LOKACJE ---
clues_found = defaultdict(bool)

def get_drwale_dialogue():
    if clues_found.get("drwale_przekonani", False):
        return ("Obóz drwali jest pusty. Zwinęli sprzęt i uciekli w popłochu.", [("Odejdź", "LEAVE")])
    choices = [("Odejdź i przemyśl sprawę", "LEAVE")]
    if clues_found.get("ma_bimber", False): choices.insert(0, ("Daj Szefowi drwali bimber Sołtysa", "DRWALE_BIMBER"))
    if clues_found.get("ma_miksture_smrodu", False): choices.insert(0, ("Wrzuć miksturę smrodu do ich ogniska!", "DRWALE_SMROD"))
    if clues_found.get("ma_tanie_wino", False): choices.insert(0, ("Daj Tanie Wino menelom", "DRWALE_MENELE"))
    choices.insert(0, ("Przekonaj ich do wyjazdu groźbami", "DRWALE_CHARISMA"))
    return ("Szef Drwali: Czego tu szukasz? Urząd kazał rżnąć las, to rżniemy! \nNieopodal siedzi grupka tutejszych meneli, łypiąc ponuro na drwali.", choices)
    
def get_kapliczka_dialogue():
    if clues_found.get("rozmowa_zielarka_smrod", False) and not clues_found.get("ma_zgnily_grzyb", False):
        return ("Pod starą kapliczką rośnie pulsujący Zgniły Grzyb. Obok niego zwija się żmija!", 
                [("Spróbuj zabrać grzyb (Zręczność)", "TEST_AGILITY_GRZYB"), ("Odejdź", "LEAVE")])
    if clues_found["zardzewialy_sztylet"]: return ("Stara kapliczka. Zabrałeś stąd już wszystko.", [("Odejdź", "LEAVE")])
    return ("Pod deskami starej kapliczki znajdujesz przedziwny artefakt...\nTo Zardzewiały Sztylet, emanujący chłodem.", 
            [("Zabierz sztylet", "CLUE_DAGGER"), ("Zostaw go", "LEAVE")])

def get_soltys_dialogue():
    if clues_found.get("powrot_do_cholow", False):
        if not clues_found.get("ma_bimber", False):
            return ("Sołtys: Doktorze! Ci drwale z urzędu sprowadzą na nas gniew lasu! Masz, weź mój bimber.", 
                    [("Weź bimber", "TAKE_BIMBER"), ("Odejdź", "LEAVE")])
        return ("Sołtys: Błagam, przegnaj tych drwali!", [("Odejdź", "LEAVE")])
    if clues_found["zaufanie_soltysa"]: 
        return ("Sołtys: Idź do Zielarki. Powiedz, że ja cię przysłałem.", [("Odejdź", "LEAVE")])
    choices = [("Wybacz najście.", "LEAVE")]
    if clues_found["zardzewialy_sztylet"]: choices.insert(0, ("Znalazłem ten zardzewiały sztylet.", "SHOW_DAGGER"))
    return ("Sołtys: Aha, pan jest tym doktorem z miasta? Będzie pan leczył? \nDrozd: Psychologii... \nSołtys: Phiii. Myślałem, że chociaż lekarza przysłali. Fiodora wilki zjadły o 21:37... Zostały po nim tylko kremówki.", choices)

def get_zielarka_dialogue():
    if clues_found.get("powrot_do_cholow", False):
        if not clues_found.get("rozmowa_zielarka_smrod", False):
            return ("Zielarka: Drwale to problem. Przynieś mi Zgniły Grzyb spod kapliczki, a uwarzę miksturę smrodu.", 
                    [("Podejmuję się", "START_SMROD_QUEST"), ("Odejdź", "LEAVE")])
        elif clues_found.get("ma_zgnily_grzyb", False) and not clues_found.get("ma_miksture_smrodu", False):
            return ("Zielarka: Dawaj go tu! Ugh, ten odór... Gotowe.", [("Zabierz słoik", "TAKE_MIKSTURA")])
        elif clues_found.get("ma_miksture_smrodu", False):
            return ("Zielarka: Rzuć to w ich ognisko.", [("Odejdź", "LEAVE")])

    if clues_found["zaufanie_zielarki"]: 
        if clues_found["ma_amulet_zielarki"]: return ("Zielarka: Szukaj w spalonej chacie.", [("Odejdź", "LEAVE")])
        return ("Zielarka: Użyj Amuletu przeciw demonom...", [("Schowaj amulet", "CLUE_AMULET")])
    
    if clues_found["quest_zielarka_zaczety"] and not clues_found["zaufanie_zielarki"]:
        if clues_found["ma_ksiege_zielarki"]: return ("Zielarka: Odzyskałeś moją księgę!", [("Oddaj księgę", "ODDAJ_KSIEGE_ZIELARCE")])
        else: return ("Zielarka: Bez księgi nie mamy o czym gadać.", [("Odejdź", "LEAVE")])
    
    choices = [("Odejdź", "LEAVE")]
    if clues_found["zaufanie_soltysa"]:
        choices.insert(0, ("Zapłać za wskazówkę (5 zł)", "PAY_ZIELARKA"))
        choices.insert(1, ("Skłam: 'Sołtys kazał' (Charyzma)", "TEST_CHARISMA_ZIELARKA"))
        return ("Zielarka: Bieniasz cię przysłał? Zapłać 5 zł.", choices)
    return ("Zielarka: Udowodnij najpierw, że tutejsi chcą z tobą gadać.", [("Wyjdź z namiotu", "LEAVE")])

def get_ruiny_dialogue():
    if clues_found.get("mamuna_zalatwiona", False) and not clues_found.get("ruiny_skarb", False):
        return ("W świetle księżyca dostrzegasz błyszczącą sakiewkę pod deską...", [("Przeszukaj gruzy", "CLUE_RUINY_SKARB")])
    if clues_found["zaufanie_zielarki"] and not clues_found["dowod_kosci"]:
        return ("Rozgarniasz popiół w piecu. Znajdujesz zwęglone kości odmieńca...", [("Zabezpiecz dowód", "CLUE_KOSCI")])
    elif clues_found["dowod_kosci"]: return ("Masz już dowód. Czas pokazać go Maćkowi.", [("Odejdź", "LEAVE")])
    return ("Osmalone ściany potęgują odór pożaru.", [("Odejdź", "LEAVE")])

def get_plebania_dialogue():
    if clues_found["ma_upowaznienie_maciek"]: return ("Maciek: Jedź do Marii. Żuk stoi na skraju wsi.", [("Odejdź", "LEAVE")])
    if clues_found["dowod_kosci"]:
        return ("Maciek: Te kości... Ona nie spaliła naszego dziecka!\nWeź upoważnienie i jedź do niej do Choroszczy.", [("Weź upoważnienie", "GET_UPOWAZNIENIE")])
    choices = [("Wyjdź", "LEAVE")]
    if clues_found["quest_zielarka_zaczety"] and not clues_found["ma_ksiege_zielarki"]: choices.insert(0, ("Zielarka przysłała mnie po księgę.", "ZAPYTAC_MACKA_O_KSIEGE"))
    return ("Maciek: Zostaw mnie... Moje dziecko nie żyje, a żonę zabrali...", choices)

def get_zuk_dialogue():
    if clues_found.get("mamuna_zalatwiona", False): return ("Żuk gotowy. Czas odpocząć w chacie.", [("Odejdź", "LEAVE")])
    if clues_found["wiedza_o_mamunie"]: return ("Żuk gotowy, ale musisz zabić Mamunę w Lesie.", [("Jedź do lasu walczyć z Mamuną", "GO_TO_FOREST"), ("Odejdź", "LEAVE")])
    if clues_found["ma_upowaznienie_maciek"]: return ("Masz dokumenty. Wsiadasz do Żuka.", [("Jedź do Choroszczy", "GO_CHOROSZCZ"), ("Jeszcze nie", "LEAVE")])
    return ("Twój stary Żuk. Szkoda paliwa.", [("Odejdź", "LEAVE")])

def get_bed_dialogue():
    if clues_found.get("mamuna_zalatwiona", False) and not clues_found.get("powrot_do_cholow", False):
        return ("Czujesz dziwny, mroczny niepokój unoszący się nad Chołami...", [("Połóż się spać (Rozpocznij kolejny akt)", "TRIGGER_MOB_EVENT")])
    choices = [("Prześpij się (Regeneracja HP i Poczytalności)", "SLEEP")]
    if not clues_found.get("wspolpraca_z_lusia", False):
        if clues_found.get("ma_cukierki", False): choices.insert(0, ("Daj Lusi cukierki", "LUSIA_GIVE_CANDY"))
        else: choices.insert(0, ("Porozmawiaj z małą Lusią", "LUSIA_TALK"))
    else:
        choices.insert(0, ("Porozmawiaj z Lusią", "LUSIA_TALK_TRUST"))
    choices.append(("Wyjdź", "LEAVE"))
    return ("Twoje posłanie. W kącie kuli się mała Lusia.", choices)

def get_sklep_dialogue():
    choices = [("Wyjdź", "LEAVE")]
    if not clues_found.get("ma_cukierki", False): choices.insert(0, ("Kup Cukierki (5 zł)", "BUY_CANDY"))
    if not clues_found.get("ma_tanie_wino", False): choices.insert(0, ("Kup Wino (10 zł)", "BUY_WINE"))
    return ("Sklep 'Słodycze Wina'. Półki świecą pustkami.\nSprzedawca: Czego dusza pragnie?", choices)

houses = [
    House(150, 150, 160, 110, "Dom Sołtysa Bieniasza", get_soltys_dialogue),
    House(450, 250, 140, 60, "Wóz (Żuk)", get_zuk_dialogue),
    House(600, 100, 150, 110, "Spalona Chata Marii", get_ruiny_dialogue, ruined=True),
    House(150, 400, 130, 90, "Sklep 'Słodycze Wina'", get_sklep_dialogue),
    House(400, 450, 150, 130, "Plebania (Maciek)", get_plebania_dialogue),
    House(650, 450, 130, 90, "Chata po starym Mikołaju", get_bed_dialogue),
    House(800, 150, 140, 100, "Namiot Starej Zielarki", get_zielarka_dialogue),
    House(360, 520, 160, 90, "Obóz Drwali (Urząd)", get_drwale_dialogue)
]

decorations_trees = [(random.randint(0, WIDTH), random.randint(0, HEIGHT)) for _ in range(15)]
forest_trees = [(random.randint(0, WIDTH), random.randint(0, HEIGHT)) for _ in range(35)]
monster_triggers_forest = [
    {"rect": pygame.Rect(WIDTH//2 - 250, HEIGHT//2 - 200, 60, 60), "type": BOSS_LATARNIK, "beaten": False},
    {"rect": pygame.Rect(WIDTH//2 + 190, HEIGHT//2 - 200, 60, 60), "type": BOSS_PIEN, "beaten": False},
    {"rect": pygame.Rect(WIDTH//2 - 30, HEIGHT//2 + 100, 60, 60), "type": BOSS_MAMUNA, "beaten": False}, 
    {"rect": pygame.Rect(WIDTH//2 - 50, HEIGHT//2 - 250, 60, 60), "type": BOSS_GAWRON, "beaten": False},
    {"rect": pygame.Rect(WIDTH//2 + 190, HEIGHT//2 + 150, 60, 60), "type": BOSS_SKRZEKACZ, "beaten": False} 
]

# Tło wioski
low_terrain_surface = pygame.Surface((LOW_W, LOW_H))
low_terrain_surface.fill((40, 45, 40)) 
draw_oily_mud(low_terrain_surface, 200, 350, 80, 20)
draw_oily_mud(low_terrain_surface, 500, 400, 120, 25)
for _ in range(400):
    pygame.draw.line(low_terrain_surface, (70, 85, 70), (random.randint(0, LOW_W), random.randint(LOW_H//2, LOW_H)), (random.randint(0, LOW_W), random.randint(LOW_H//2, LOW_H) - random.randint(6, 12)), 1)

# --- ZMIENNE STANU GRY ---
current_state = STATE_INTRO
current_map = "VILLAGE" 
anim_tick = 0
active_house = None 
player_pos = pygame.Vector2(250, 450) 
player_hp, player_max_hp = 100, 100
player_sanity, player_max_sanity = 100, 100
player_money = 10 
base_attack, mod_attack, mod_stamina = 10, 0, 0
player_agility, player_charisma = 5, 5

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

runner_player_y = HEIGHT - 150
runner_player_vy = 0
runner_is_jumping = False
runner_ground_y = HEIGHT - 150
runner_obstacles = []
runner_bolts = []
runner_dziadek_hp, runner_dziadek_max_hp = 150, 150
runner_timer = 0
runner_mode_vines = False

intro_sequence = [
    {"title": "Wnętrze Żuka. Cuchnie tanim tytoniem.", "text": "Kierowca Władek: W Chołach babka spaliła dzieciaka w piecu. Chore... Maciej rozpacza, a Marię zabrali do Choroszczy..."},
    {"title": "Wioska Choły. Ciemność.", "text": "Drozd, psycholog śledczy: 'Zobaczymy ile w tym prawdy...' (Porozmawiaj z ludźmi. Znajdź poszlaki. Rozwiąż sprawę. Strzeż umysłu...)"}
]
intro_step = 0

# --- GŁÓWNA PĘTLA ---
running = True
while running:
    anim_tick += 1
    clock.tick(60)
    keys = pygame.key.get_pressed()

    # 1. EKSPLORACJA
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
                        if "Wóz (Żuk)" in h.name:
                            current_state = STATE_DIALOGUE
                            active_house = h
                            dialogue_title = h.name
                            t, c = h.dialog_func()
                            dialogue_lines = [t]
                            dialogue_choices = c
                            current_choice_idx = 0
                        else:
                            current_state = STATE_HOUSE
                            active_house = h
                            player_pos = pygame.Vector2(WIDTH // 2, HEIGHT - 130)
                        break
                
                if current_state == STATE_EXPLORE:
                    okno_soltysa = pygame.Rect(200, 220, 50, 50)
                    if okno_soltysa.collidepoint(player_pos.x, player_pos.y):
                        current_state = STATE_DIALOGUE
                        dialogue_title = "Ciemne Okno"
                        if clues_found["podslyszano_soltysa"]:
                            dialogue_lines = ["Nic więcej nie usłyszysz. Głucha cisza."]
                            dialogue_choices = [("Odejdź", "LEAVE_WINDOW")]
                        else:
                            dialogue_lines = ["Widzisz migoczące światło. Sołtys z kimś rozmawia. Podsłuchujesz?"]
                            dialogue_choices = [
                                ("Podsłuchuj (Zręczność)", "TEST_AGILITY_WINDOW"), 
                                ("Zostaw to", "LEAVE_WINDOW")
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
            if active_house is None:
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
        if keys[pygame.K_SPACE] and not runner_is_jumping:
            runner_player_vy = -14
            runner_is_jumping = True
            
        runner_player_y += runner_player_vy
        runner_player_vy += 0.8
        
        if runner_player_y >= runner_ground_y:
            runner_player_y = runner_ground_y
            runner_player_vy = 0
            runner_is_jumping = False
            
        if keys[pygame.K_e] and runner_timer % 15 == 0:
            runner_bolts.append(Projectile(400, runner_player_y + 15, -10, 0, C_GOLD))
            
        if runner_timer % 90 == 0:
            o_type = "LOG"
            if runner_mode_vines and random.choice([True, False]): o_type = "VINE"
            runner_obstacles.append(RunnerObstacle(WIDTH, 455, 30, 25, o_type, 6))
            
        for o in runner_obstacles[:]:
            o.update()
            if o.x < 420 and o.x > 380 and runner_player_y > 420:
                player_hp -= 10
                runner_obstacles.remove(o)
            elif o.x < 0:
                runner_obstacles.remove(o)

        for b in runner_bolts[:]:
            b.update()
            if b.x < 150 and abs(b.y - (runner_ground_y - 20)) < 60:
                runner_dziadek_hp -= 5
                runner_bolts.remove(b)

        if runner_dziadek_hp <= 0:
            current_state = STATE_END
            end_message = "Zgubiłeś Dziadka i zgładziłeś go z kuszy!\nUratowałeś drwali z urzędu. Lecz twój konflikt z Lasem dopiero się zaczął..."
            barka_sound.stop()
        elif player_hp <= 0:
            current_state = STATE_END
            end_message = "Potknąłeś się, a pnącza wciągnęły cię pod ziemię. (GAME OVER)"
            barka_sound.stop()

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
                                active_house = None 
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

    # 3. RENDEROWANIE Z WYSOKĄ ROZDZIELCZOŚCIĄ W HORROROWYM STYLU
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
        draw_text_wrapped(screen, intro_sequence[intro_step]["text"], font_main, C_GRAY_LIGHT, 80, y_pos, WIDTH - 160)
        screen.blit(font_sub.render("[Spacja / Enter]", True, C_GRAY), (WIDTH - 200, HEIGHT - 40))
            
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
                    draw_sprzedawca(game_surface, hx, hy)
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
                        draw_zuk(game_surface, S(h.rect.centerx), S(h.door_rect.centery - 15), light=False)
                    else:
                        draw_uncanny_house(game_surface, S(h.rect.x), S(h.rect.y), S(h.rect.width), S(h.rect.height), ruined=h.ruined)
                    
                    pygame.draw.ellipse(game_surface, (15, 12, 10), (S(h.door_rect.x), S(h.door_rect.y), S(h.door_rect.w), S(h.door_rect.h)))
                    pygame.draw.ellipse(game_surface, C_BLACK, (S(h.door_rect.x), S(h.door_rect.y), S(h.door_rect.w), S(h.door_rect.h)), 1)
        
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
            current_y += draw_text_wrapped(screen, combined_dialogue, font_main, C_GRAY_LIGHT, 140, current_y, WIDTH - 200) + 15
            
            for idx, choice in enumerate(dialogue_choices):
                color = C_RED if idx == current_choice_idx else C_GRAY
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
