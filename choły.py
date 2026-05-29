import pygame
import numpy as np
import wave
import sys
import os

# ==========================================
# 1. GENEROWANIE DŹWIĘKU (NumPy)
# ==========================================
def generate_music():
    if os.path.exists("slavic_horror.wav"):
        return # Nie generuj, jeśli już istnieje

    SAMPLE_RATE = 44100
    BEAT_SEC = 60.0 / 80

    def get_freq(note):
        notes = {'A':0, 'D':-7, 'E':-5, 'F':-4}
        if note == 'REST': return 0.0
        return 440.0 * (2.0 ** ((notes[note[:-1]] + (int(note[-1]) - 4) * 12) / 12.0))

    def gen_wave(note, dur_beats, w_type='square', vol=0.2):
        t = np.linspace(0, dur_beats * BEAT_SEC, int(SAMPLE_RATE * dur_beats * BEAT_SEC), False)
        f = get_freq(note)
        if f == 0: return np.zeros_like(t)
        wave_data = 2 * np.abs(2 * (t * f - np.floor(t * f + 0.5))) - 1 if w_type == 'triangle' else np.sin(2 * np.pi * f * t)
        
        fade = int(SAMPLE_RATE * 0.1)
        env = np.ones_like(t)
        if len(t) > fade * 2:
            env[:fade] = np.linspace(0, 1, fade)
            env[-fade:] = np.linspace(1, 0, fade)
        return wave_data * env * vol

    melody = [('A3', 2.0), ('E3', 2.0), ('F3', 2.0), ('D3', 2.0), ('E3', 4.0)]
    drone = [('A1', 12.0)]
    audio_track = np.sum([
        np.concatenate([gen_wave(n, d, 'triangle', 0.5) for n, d in melody]),
        np.concatenate([gen_wave(n, d, 'sine', 0.3) for n, d in drone])
    ], axis=0)

    audio_16bit = np.int16(audio_track / np.max(np.abs(audio_track)) * 32767)
    with wave.open("slavic_horror.wav", 'w') as f:
        f.setnchannels(1)
        f.setsampwidth(2)
        f.setframerate(SAMPLE_RATE)
        f.writeframes(audio_16bit.tobytes())

# ==========================================
# 2. INICJALIZACJA GRY I DŹWIĘKU
# ==========================================
generate_music()
pygame.init()
pygame.mixer.init()

# Zapętlenie muzyki w tle
pygame.mixer.music.load("slavic_horror.wav")
pygame.mixer.music.play(-1)

WIDTH, HEIGHT = 800, 600
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Krzykacz: Mrok Podlasia")
clock = pygame.time.Clock()

C_BG = (10, 10, 12)
C_BOX = (25, 25, 30)
C_TEXT = (230, 226, 216)
C_HOVER = (154, 3, 30)
C_BORDER = (72, 77, 86)

font_main = pygame.font.SysFont("georgia", 24)
font_title = pygame.font.SysFont("georgia", 36, bold=True)

def draw_text(surface, text, pos, font, color, max_width):
    words = text.split(' ')
    space_width, font_height = font.size(' ')
    x, y = pos
    for word in words:
        if word == '\n':
            x = pos[0]; y += font_height + 5; continue
        word_surface = font.render(word, True, color)
        word_width, word_height = word_surface.get_size()
        if x + word_width >= pos[0] + max_width:
            x = pos[0]; y += font_height + 5
        surface.blit(word_surface, (x, y))
        x += word_width + space_width

# ==========================================
# 3. FABUŁA
# ==========================================
story = {
    "start": {
        "title": "Przeklęta Wieś",
        "text": "Ciężkie buciory toną w podlaskim błocie. Przed tobą majaczą zarysy starych, drewnianych chałup. Przyjechałeś tu szukać zaginionego brata. Deszcz zmywa ślady, ale widzisz po lewej spalone zgliszcza jego chaty...\n\nCo robisz?",
        "choices": [("Zbadaj spaloną chatę", "chata"), ("Wejdź do karczmy, by popytać miejscowych", "karczma")]
    },
    "chata": {
        "title": "Spalone Zgliszcza",
        "text": "Wśród zwęglonych belek wyłania się młoda, blada dziewczyna. Ma bose stopy pomimo chłodu.\n- 'Jestem Lusia. Nie powinieneś tu być, drwalu' - szepcze. - 'Las upomina się o swoje.'",
        "choices": [("Zażądaj informacji o bracie", "final_boss"), ("Uciekaj z wioski", "death")]
    },
    "karczma": {
        "title": "Wroga Karczma",
        "text": "Gdy wchodzisz, gwar cichnie. Wszyscy patrzą na twoją siekierę, noszą na szyi dziwne, kościane amulety.\n- 'Zabłądziliście. Lepiej wracajcie na trakt przed zmrokiem. Nocą... Krzykacz poluje.'",
        "choices": [("Żądaj prawdy z siekierą w dłoni", "final_boss")]
    },
    "final_boss": {
        "title": "Krzykacz",
        "text": "Stoisz w mrocznym lesie. Spomiędzy drzew wychyla się monstrum - chude, ociekające krwią, z ogromnymi oczami. Ziemia drży. Wendigo zadaje ci zagadkę:\n\n'Co pożera wszystko: ptaki, bestie, drzewa i kwiaty? Gryzie żelazo, kruszy kamienie, a na końcu zabija sam las?'",
        "choices": [("Ogień", "death"), ("Czas", "victory"), ("Atakuj z siekierą bez myślenia!", "death")]
    },
    "victory": {
        "title": "Uwolnienie",
        "text": "Krzykacz zastyga. Odpowiedziałeś poprawnie. Potwór rozsypuje się w pył, a klątwa lasu znika. Wygrałeś.",
        "choices": [("Zagraj ponownie", "start")]
    },
    "death": {
        "title": "Śmierć",
        "text": "Rzucasz się naprzód, ale Krzykacz jest szybszy. Ostre pazury rozrywają ciemność. Kult zyskał kolejną ofiarę.",
        "choices": [("Spróbuj ponownie", "start")]
    }
}

current_node = "start"

# ==========================================
# 4. GŁÓWNA PĘTLA GRY
# ==========================================
running = True
while running:
    screen.fill(C_BG)
    node_data = story.get(current_node, story["start"])
    
    mouse_pos = pygame.mouse.get_pos()
    clicked = False
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            clicked = True
            
    pygame.draw.rect(screen, C_BOX, (50, 50, 700, 300), border_radius=10)
    pygame.draw.rect(screen, C_BORDER, (50, 50, 700, 300), width=3, border_radius=10)
    
    title_surf = font_title.render(node_data.get("title", ""), True, C_HOVER)
    screen.blit(title_surf, (80, 70))
    draw_text(screen, node_data["text"], (80, 130), font_main, C_TEXT, 640)
    
    choice_y = 380
    for i, choice in enumerate(node_data["choices"]):
        choice_text, next_node = choice
        button_rect = pygame.Rect(50, choice_y, 700, 50)
        
        if button_rect.collidepoint(mouse_pos):
            pygame.draw.rect(screen, C_HOVER, button_rect, border_radius=8)
            if clicked: current_node = next_node
        else:
            pygame.draw.rect(screen, C_BOX, button_rect, border_radius=8)
            
        pygame.draw.rect(screen, C_BORDER, button_rect, width=2, border_radius=8)
        btn_surf = font_main.render(f"{i+1}. {choice_text}", True, C_TEXT)
        screen.blit(btn_surf, (80, choice_y + 10))
        choice_y += 70

    pygame.display.flip()
    clock.tick(30)

pygame.quit()
sys.exit()
