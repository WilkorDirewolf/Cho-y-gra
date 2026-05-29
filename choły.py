import pygame
import numpy as np
import wave
import sys
import os
import random

# ==========================================
# 1. GENERATOR PROCEDURALNEJ MUZYKI (NumPy)
# ==========================================
def generate_music():
    if os.path.exists("slavic_horror.wav"):
        return
    SAMPLE_RATE = 44100
    BEAT_SEC = 60.0 / 75
    def get_freq(note):
        notes = {'A':0, 'D':-7, 'E':-5, 'F':-4, 'C':-9, 'G':-2}
        if note == 'REST': return 0.0
        return 440.0 * (2.0 ** ((notes[note[:-1]] + (int(note[-1]) - 4) * 12) / 12.0))

    def gen_wave(note, dur_beats, w_type='triangle', vol=0.3):
        t = np.linspace(0, dur_beats * BEAT_SEC, int(SAMPLE_RATE * dur_beats * BEAT_SEC), False)
        f = get_freq(note)
        if f == 0: return np.zeros_like(t)
        w = 2 * np.abs(2 * (t * f - np.floor(t * f + 0.5))) - 1 if w_type == 'triangle' else np.sign(np.sin(2 * np.pi * f * t))
        fade = int(SAMPLE_RATE * 0.1)
        env = np.ones_like(t)
        if len(t) > fade * 2:
            env[:fade] = np.linspace(0, 1, fade)
            env[-fade:] = np.linspace(1, 0, fade)
        return w * env * vol

    melody = [('A3', 2.0), ('F3', 2.0), ('E3', 4.0), ('D3', 2.0), ('C3', 2.0), ('E3', 4.0)]
    audio_track = np.concatenate([gen_wave(n, d, 'triangle', 0.4) for n, d in melody])
    audio_16bit = np.int16(audio_track / np.max(np.abs(audio_track)) * 32767)
    with wave.open("slavic_horror.wav", 'w') as f:
        f.setnchannels(1); f.setsampwidth(2); f.setframerate(SAMPLE_RATE)
        f.writeframes(audio_16bit.tobytes())

# ==========================================
# 2. INICJALIZACJA WYŚWIETLANIA I AUDIO
# ==========================================
generate_music()
pygame.init()
pygame.mixer.init()

try:
    pygame.mixer.music.load("slavic_horror.wav")
    pygame.mixer.music.play(-1)
except:
    pass

WIDTH, HEIGHT = 900, 650
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Krzykacz: Tajemnica Chołów")
clock = pygame.time.Clock()

# Paleta kolorów retro-horror
PALETTE = {
    0: (12, 12, 16),    # Głęboka czerń
    1: (220, 215, 200), # Kościana biel
    2: (80, 85, 95),    # Zimna szarość
    3: (40, 42, 48),    # Ciemna szarość
    4: (160, 20, 35),   # Krew / Czerwień
    5: (230, 175, 45),  # Światło latarni
    6: (35, 75, 45),    # Zgniła zieleń
    7: (140, 90, 55)    # Drewno / Brąz
}

font_text = pygame.font.SysFont("georgia", 20)
font_ui = pygame.font.SysFont("georgia", 18, bold=True)
font_title = pygame.font.SysFont("georgia", 32, bold=True)

# ==========================================
# 3. PROCEDURALNY SILNIK GRAFICZNY (PIXEL ART)
# ==========================================
def generate_pixel_art(scene_type):
    grid = np.zeros((64, 64), dtype=int)
    
    if scene_type == "village":
        grid[40:64, :] = 3  # Błoto
        grid[25:50, 10:35] = 7 # Chata
        grid[15:25, 8:37] = 2  # Dach
        grid[32:42, 45:55] = 1 # Postać w tle
    elif scene_type == "lusia":
        grid[15:50, 20:44] = 1 # Twarz i skóra
        grid[10:35, 15:49] = 7 # Włosy
        grid[25:30, 25:29] = 6; grid[25:30, 35:39] = 6 # Zielone oczy lasu
        grid[45:64, 15:49] = 6 # Roślinna suknia
    elif scene_type == "mamuna":
        grid[10:55, 20:44] = 3 # Garbata sylwetka
        grid[15:22, 28:36] = 2 # Pomarszczona twarz
        grid[20:25, 26:38] = 4 # Ślepia
        grid[40:55, 30:50] = 7 # Kołyska w dłoniach
    elif scene_type == "latarnik":
        grid[5:25, 10:54] = 0 # Skrzydła nietoperza (kontury w mroku)
        grid[10:45, 25:39] = 2 # Chude ciało
        grid[15:22, 28:31] = 5; grid[15:22, 33:36] = 5 # Oczy jak latarnie
        grid[35:55, 38:46] = 7 # Ramię trzymające latarnię
        grid[48:58, 36:48] = 5 # Płonąca ludzka głowa-latarnia
    elif scene_type == "gawron":
        grid[25:64, 20:44] = 3 # Ludzkie ciało w garniturze
        grid[5:25, 25:39] = 0 # Głowa ptaka
        grid[12:25, 15:28] = 0 # Wielki czarny dziób
        grid[14:17, 28:30] = 1 # Bystre oko
    elif scene_type == "pien":
        grid[20:55, 15:50] = 7 # Gruby tułów prosiaka
        grid[10:30, 10:30] = 2 # Głowa łosia
        grid[5:15, 5:20] = 3  # Poroże
        grid[50:60, 45:52] = 4 # Zakręcony ogon
    elif scene_type == "krzykacz":
        grid[:, :] = np.where(random.random() > 0.92, 4, 0) # Zakłócenia mroku
        grid[8:55, 22:42] = 2 # Makabryczna chuda sylwetka
        grid[12:20, 25:29] = 4; grid[12:20, 35:39] = 4 # Wielkie czerwone ślepia
        grid[25:38, 27:37] = 4 # Rozwarta paszcza

    # Konwersja na Surface Pygame
    surf = pygame.Surface((64, 64))
    for y in range(64):
        for x in range(64):
            surf.set_at((x, y), PALETTE[grid[y, x]])
    return pygame.transform.scale(surf, (350, 350))

# ==========================================
# 4. BAZA DANYCH: ZAGADKI GAWRONA (20 sztuk)
# ==========================================
RIDDLES = [
    {"q": "Co ma zęby, ale nigdy niczego nie zje?", "a": ["Grzebień", "Piła", "Wilk"], "c": 0},
    {"q": "Idzie przez świat, ale nie zostawia śladów?", "a": ["Cień", "Wiatr", "Dym"], "c": 1},
    {"q": "Im więcej z niej zabierasz, tym większa się staje.", "a": ["Dziura", "Kopalnia", "Pamięć"], "c": 0},
    {"q": "Zawsze biegnie, nigdy nie chodzi. Ma łożysko, lecz nie śpi.", "a": ["Rzeka", "Koło", "Zegar"], "c": 0},
    {"q": "Co staje się wilgotne, im dłużej coś suszy?", "a": ["Ręcznik", "Liść", "Ogień"], "c": 0},
    {"q": "Należy do ciebie, ale inni używają tego znacznie częściej.", "a": ["Imię", "Buty", "Cień"], "c": 0},
    {"q": "Co potrafi mówić bez języka i słyszeć bez uszu?", "a": ["Echo", "Wiatr", "List"], "c": 0},
    {"q": "Rodzi się małe, umiera potężne, a woda niesie mu zgubę.", "a": ["Ogień", "Drzewo", "Strach"], "c": 0},
    {"q": "Ma klucze, ale nie otworzy żadnych drzwi.", "a": ["Fortepian", "Skarbiec", "Mapa"], "c": 0},
    {"q": "Traci głowę o poranku, odzyskuje ją dopiero wieczorem.", "a": ["Poduszka", "Kogut", "Słońce"], "c": 0},
    {"q": "Ma pióra, a nie lata. Ma grzbiet, a nie chodzi.", "a": ["Książka", "Gawron", "Strzała"], "c": 0},
    {"q": "Co ma jedno oko, ale absolutnie nic nie widzi?", "a": ["Igła", "Cyklop", "Burza"], "c": 0},
    {"q": "Można mnie łatwo złapać, ale niezwykle trudno rzucić.", "a": ["Przeziębienie", "Kamień", "Uciekinier"], "c": 0},
    {"q": "Co pożera wszystko: ptaki, drzewa, kamień i stal, a na końcu sam las?", "a": ["Czas", "Ogień", "Krzykacz"], "c": 0},
    {"q": "Stoisz przed nią, widzi cię idealnie, ale nigdy nie odezwie się pierwsza.", "a": ["Lustro", "Ściana", "Lusia"], "c": 0},
    {"q": "Czym jest to, co ukrywasz, a gdy komuś dasz, natychmiast tracisz?", "a": ["Sekret", "Słowo", "Moneta"], "c": 0},
    {"q": "Lata bez skrzydeł, płacze bez oczu.", "a": ["Chmura", "Nietoperz", "Duch"], "c": 0},
    {"q": "Im jest ich więcej wokół ciebie, tym mniej widzisz.", "a": ["Ciemność", "Drzewa", "Oczy"], "c": 0},
    {"q": "Nie ma ciała, ale żyje. Nie ma domu, ale wyje.", "a": ["Wiatr", "Wilk", "Upiór"], "c": 0},
    {"q": "Daje mleko, lecz nie jest krową. Ma poroże, lecz nie jest jeleniem.", "a": ["Pień", "Koza", "Mit"], "c": 1}
]

# ==========================================
# 5. GŁÓWNA STRUKTURA STANÓW GRY
# ==========================================
class GameState:
    def __init__(self):
        self.state = "INTRO"
        self.items_found = set()
        self.charisma = 6  # Statystyka do testów dialogowych Jerzego Drozda
        self.selected_riddle = random.choice(RIDDLES)
        self.timer = 0
        self.arcade_pos = [450, 150]
        self.arcade_dir = 5
        self.bolt_pos = None
        self.boss_hp = 3
        self.qte_sequence = []
        self.qte_index = 0
        self.qte_timer = 0

game = GameState()

def draw_wrapped_text(surface, text, pos, max_width, font=font_text, color=PALETTE[1]):
    words = text.split(' ')
    space_w, font_h = font.size(' ')
    x, y = pos
    for word in words:
        if '\n' in word:
            parts = word.split('\n')
            for part in parts[:-1]:
                surf = font.render(part, True, color)
                surface.blit(surf, (x, y))
                x = pos[0]; y += font_h + 6
            word = parts[-1]
        surf = font.render(word, True, color)
        w, h = surf.get_size()
        if x + w >= pos[0] + max_width:
            x = pos[0]; y += font_h + 6
        surface.blit(surf, (x, y))
        x += w + space_w

# ==========================================
# 6. GŁÓWNA PĘTLA GRY
# ==========================================
running = True
while running:
    screen.fill(PALETTE[0])
    mouse_pos = pygame.mouse.get_pos()
    clicked = False
    
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            clicked = True
        if event.type == pygame.KEYDOWN and game.state == "MINIGAME_LATARNIK":
            if event.key == pygame.K_SPACE and game.bolt_pos is None:
                game.bolt_pos = [450, 500]

    # Renderowanie ramki graficznej po lewej stronie ekranu
    if game.state not in ["GAME_OVER", "VICTORY", "MINIGAME_LATARNIK"]:
        img_key = "village"
        if "MAMUNA" in game.state: img_key = "mamuna"
        elif "LUSIA" in game.state: img_key = "lusia"
        elif "GAWRON" in game.state: img_key = "gawron"
        elif "PIEN" in game.state: img_key = "pien"
        elif "KRZYKACZ" in game.state: img_key = "krzykacz"
        
        # Rysowanie tła pod obrazek
        pygame.draw.rect(screen, PALETTE[3], (30, 40, 360, 360))
        pygame.draw.rect(screen, PALETTE[2], (30, 40, 360, 360), 3)
        screen.blit(generate_pixel_art(img_key), (35, 45))

    # Blok interfejsu opisowego po prawej stronie ekranu
    text_rect = pygame.Rect(420, 40, 450, 360)
    pygame.draw.rect(screen, PALETTE[3], text_rect)
    pygame.draw.rect(screen, PALETTE[2], text_rect, 3)

    # Przyciski wyborów (dolny panel)
    btn1 = pygame.Rect(50, 440, 800, 45)
    btn2 = pygame.Rect(50, 500, 800, 45)
    btn3 = pygame.Rect(50, 560, 800, 45)

    def draw_btn(rect, text):
        hover = rect.collidepoint(mouse_pos)
        pygame.draw.rect(screen, PALETTE[4] if hover else PALETTE[3], rect, border_radius=6)
        pygame.draw.rect(screen, PALETTE[1] if hover else PALETTE[2], rect, width=2, border_radius=6)
        t_surf = font_ui.render(text, True, PALETTE[1])
        screen.blit(t_surf, (rect.x + 20, rect.y + 12))
        return hover and clicked

    # ----------------------------------------------------
    # SILNIK SCENARIUSZA (STANÓW)
    # ----------------------------------------------------
    if game.state == "INTRO":
        draw_wrapped_text(screen, "TAJEMNICA CHOŁÓW\n\nNazywasz się Jerzy Drozd. Jesteś wielkomiejskim psychologiem, który przybył do odciętej od świata wsi Choły. Twoim celem jest zbadanie wstrząsającej sprawy makabrycznego obłędu: miejscowa kobieta spaliła własne dziecko w piecu chałupy.\n\nMusisz przeszukać wieś i odnaleźć ślady ukrywane przez mieszkańców.", (440, 60), 410)
        if draw_btn(btn1, "Rozpocznij śledztwo i przeszukaj wieś"):
            game.state = "SEARCH_VILLAGE"

    elif game.state == "SEARCH_VILLAGE":
        desc = f"Przeszukujesz zakamarki Chołów. Mieszkańcy unikają twojego wzroku.\n\nZnalezione dowody ({len(game.items_found)}/5):\n"
        desc += ", ".join(game.items_found) if game.items_found else "Brak śladów."
        draw_wrapped_text(screen, desc, (440, 60), 410)
        
        if "Lalka z sitowia" not in game.items_found and draw_btn(btn1, "Przeszukaj spaloną chatę"):
            game.items_found.add("Lalka z sitowia")
        if "Kościany amulet" not in game.items_found and draw_btn(btn2, "Zbadaj starą kapliczkę"):
            game.items_found.add("Kościany amulet")
        if "Podmienione runy" not in game.items_found and draw_btn(btn3, "Przeszukaj oborę sołtysa"):
            game.items_found.add("Podmienione runy")
            
        # Gdy zbierze podstawowe, odblokowują się kolejne miejsca
        if len(game.items_found) >= 2 and "Zgliszcza pieca" not in game.items_found:
            if draw_btn(pygame.Rect(50, 380, 340, 40), "Rozkop zgliszcza pieca"):
                game.items_found.add("Zgliszcza pieca")
        if len(game.items_found) >= 3 and "Ślady kopyt przy studni" not in game.items_found:
            if draw_btn(pygame.Rect(50, 330, 340, 40), "Zbadaj starą studnię"):
                game.items_found.add("Ślady kopyt przy studni")

        if len(game.items_found) == 5:
            game.state = "REVELATION"

    elif game.state == "REVELATION":
        draw_wrapped_text(screen, "Prawda wychodzi na jaw!\n\nAnaliza 5 przedmiotów daje makabryczną odpowiedź: demon Mamuna podmienił noworodka na swojego potwornego odmieńca. Przerażona kobieta, odkrywszy prawdę, wrzuciła do pieca demona, nie własną krew!\n\nW tym momencie z cienia piwnicy wyłania się rycząca Mamuna!", (440, 60), 410)
        if draw_btn(btn1, "Walcz z Mamuną za pomocą drewnianego kija"):
            game.state = "MAMUNA_FIGHT"
        if draw_btn(btn2, "Użyj charyzmy, by przekonać ją do rozejmu"):
            game.state = "MAMUNA_TALK"

    elif game.state == "MAMUNA_FIGHT":
        draw_wrapped_text(screen, "Rzucasz się na demona z grubym sękiem. Mamuna uderza szponami, lecz udaje ci się rozpłatać jej czerep. Bestia ucieka w mrok, ale jej ryk alarmuje inne potwory lasu!", (440, 60), 410)
        if draw_btn(btn1, "Uciekaj w stronę gęstwiny"):
            game.state = "LATARNIK_PRE"

    elif game.state == "MAMUNA_TALK":
        if game.charisma >= 5:
            draw_wrapped_text(screen, "Sukces testu charyzmy!\n\nTwoje opanowanie i głęboki głos psychologa dezorientują Mamunę. Mówisz o przełamaniu pętli cierpienia. Demon cofa się w głąb cieni i pozwala ci odejść bez walki.", (440, 60), 410)
            if draw_btn(btn1, "Idź dalej"): game.state = "LATARNIK_PRE"
        else:
            draw_wrapped_text(screen, "Porażka! Demon nie słucha logicznych argumentów i dotkliwie cię rani.", (440, 60), 410)
            if draw_btn(btn1, "Dalej"): game.state = "GAME_OVER"

    elif game.state == "LATARNIK_PRE":
        draw_wrapped_text(screen, "Noc rozrywa potworny pisk. Sekrety lasu zostały naruszone. Atakuje cię Latarnik – nietoperzopodobny potwór ze skrzydłami. Jego ślepia świecą jak reflektory, a w łapie trzyma odrąbaną ludzką głowę, która służy mu za gorejącą latarnię!\n\nChwytasz porzuconą kuszę!", (440, 60), 410)
        if draw_btn(btn1, "Uruchom kuszę (MINIGRA)"):
            game.state = "MINIGAME_LATARNIK"
            game.boss_hp = 3
            game.bolt_pos = None

    # --- MINIGRA ZRĘCZNOŚCIOWA: LATARNIK ---
    elif game.state == "MINIGAME_LATARNIK":
        pygame.draw.rect(screen, PALETTE[3], (50, 50, 800, 500))
        # Ruch Latarnika (celu)
        game.arcade_pos[0] += game.arcade_dir
        if game.arcade_pos[0] < 80 or game.arcade_pos[0] > 720:
            game.arcade_dir *= -1
            
        # Rysowanie Latarnika jako czerwonego kwadratu w minigrze
        pygame.draw.circle(screen, PALETTE[4], (game.arcade_pos[0], game.arcade_pos[1]), 25)
        pygame.draw.circle(screen, PALETTE[5], (game.arcade_pos[0], game.arcade_pos[1]), 10) # Oko-latarnia
        
        # Tekst pomocniczy
        lbl = font_ui.render(f"Życie Latarnika: {game.boss_hp}  |  NACIŚNIJ SPACJĘ ABY WYSTRZELIĆ KUSZĘ!", True, PALETTE[1])
        screen.fill(PALETTE[0], (50, 570, 800, 40))
        screen.blit(lbl, (70, 575))

        # Rysowanie i ruch bełtu z kuszy
        if game.bolt_pos:
            game.bolt_pos[1] -= 12
            pygame.draw.rect(screen, PALETTE[1], (game.bolt_pos[0]-2, game.bolt_pos[1], 4, 15))
            # Kolizja
            if abs(game.bolt_pos[0] - game.arcade_pos[0]) < 30 and abs(game.bolt_pos[1] - game.arcade_pos[1]) < 30:
                game.boss_hp -= 1
                game.bolt_pos = None
                if game.boss_hp <= 0:
                    game.state = "VILLAGERS_ATTACK"
            elif game.bolt_pos[1] < 40:
                game.bolt_pos = None # Pudło

    elif game.state == "VILLAGERS_ATTACK":
        draw_wrapped_text(screen, "Latarnik spada martwy na ściółkę! Widząc to, mieszkańcy Chołów, lojalni paktom z demonami, rzucają się na ciebie z widłami. \n\nZdejmujesz z kapliczki świętą maskę jelenia, zakładasz ją i uciekasz na niższe, niezbadane piętro lasu.", (440, 60), 410)
        if draw_btn(btn1, "Zejdź głębiej do kniei"):
            game.state = "GAWRON_RIDDLE"
            game.selected_riddle = random.choice(RIDDLES)

    elif game.state == "GAWRON_RIDDLE":
        q_data = game.selected_riddle
        draw_wrapped_text(screen, f"W mroku czeka Gawron – demon o ciele człowieka i głowie wielkiego ptaka. Blokuje drogę i skrzeczy:\n\n'Rozwiąż moją zagadkę albo twoje mięso nakarmi robaki!'\n\nZAGADKA:\n{q_data['q']}", (440, 60), 410)
        
        if draw_btn(btn1, q_data['a'][0]):
            game.state = "LUSIA_REUNION" if q_data['c'] == 0 else "GAME_OVER"
        if draw_btn(btn2, q_data['a'][1]):
            game.state = "LUSIA_REUNION" if q_data['c'] == 1 else "GAME_OVER"
        if draw_btn(btn3, q_data['a'][2]):
            game.state = "LUSIA_REUNION" if q_data['c'] == 2 else "GAME_OVER"

    elif game.state == "LUSIA_REUNION":
        draw_wrapped_text(screen, "Gawron kłania się nisko i rozwiewa w powietrzu. Chwilę później zza pni wybiega Lusia, córka sołtysa.\n\nWyznaje ci prawdę: 'Krzykacz się przebudził! Chce pożreć Choły za złamanie paktów. Ja... jestem patronką tego lasu, władam korzeniami. Musimy uciekać!'", (440, 60), 410)
        if draw_btn(btn1, "Biegnij z Lusią"):
            game.state = "PIEN_KIDNAP"

    elif game.state == "PIEN_KIDNAP":
        draw_wrapped_text(screen, "Nagle wielka łapa wyrywa cię z ziemi! To Pień – potworny strażnik o twarzy łosia i ciele tłustego prosiaka. Ryczy przeraźliwie:\n\n'Oddam obcego Krzykaczowi! Wtedy oszczędzi nasze domy!'\n\nMusisz działać natychmiast!", (440, 60), 410)
        if draw_btn(btn1, "Użyj charyzmy (Przekonaj Pnia do buntu)"):
            game.state = "PIEN_CONVINCE"
        if draw_btn(btn2, "Walcz na śmierć i życie wręcz"):
            game.state = "PIEN_BOSS_FIGHT"

    elif game.state == "PIEN_CONVINCE":
        if game.charisma >= 6:
            draw_wrapped_text(screen, "SUKCES! Krzyczysz pod maską jelenia, że Krzykacz pożre wszystkich, niezależnie od ofiar. Pień zaczyna drżeć i wypuszcza cię. \n\nW tej samej sekundzie z mroku wyskakuje gigantyczny KRZYKACZ! Atakuje wieś!", (440, 60), 410)
            if draw_btn(btn1, "Ostateczna obrona Chołów"):
                game.state = "MINIGAME_KRZYKACZ"
                game.timer = pygame.get_ticks()
                game.boss_hp = 15
        else:
            game.state = "PIEN_BOSS_FIGHT"

    elif game.state == "PIEN_BOSS_FIGHT":
        draw_wrapped_text(screen, "Pień nie słucha! Atakujesz jego świńskie cielsko. Musisz szybko uderzać!", (440, 60), 410)
        if draw_btn(btn1, "Zasztyletuj bestię!"):
            game.state = "MINIGAME_KRZYKACZ"
            game.timer = pygame.get_ticks()
            game.boss_hp = 15

    # --- MINIGRA FINALNA: SURVIVAL PRZECIWMKO KRZYKACZOWI ---
    elif game.state == "MINIGAME_KRZYKACZ":
        pygame.draw.rect(screen, PALETTE[3], (50, 50, 800, 500))
        time_left = 60 - (pygame.get_ticks() - game.timer) // 1000
        
        if time_left <= 0 or game.boss_hp <= 0:
            game.state = "VICTORY"
            
        # Losowa zmiana pozycji Krzykacza na ekranie co sekundę
        if pygame.get_ticks() % 30 == 0:
            game.arcade_pos = [random.randint(100, 700), random.randint(100, 400)]
            
        pygame.draw.circle(screen, PALETTE[4], game.arcade_pos, 40) # Cel-Krzykacz
        pygame.draw.circle(screen, PALETTE[0], game.arcade_pos, 15)
        
        # Sprawdzenie strzału (kliknięcia myszką)
        if clicked:
            if abs(mouse_pos[0] - game.arcade_pos[0]) < 40 and abs(mouse_pos[1] - game.arcade_pos[1]) < 40:
                game.boss_hp -= 1
                
        lbl = font_ui.render(f"ZAKOŃCZ STRZELANIE Z KUSZY! HP Bossa: {game.boss_hp} | CZAS: {max(0, time_left)}s", True, PALETTE[1])
        screen.fill(PALETTE[0], (50, 570, 800, 40))
        screen.blit(lbl, (70, 575))

    elif game.state == "VICTORY":
        screen.fill(PALETTE[0])
        title = font_title.render("ZWYCIĘSTWO!", True, PALETTE[5])
        screen.blit(title, (300, 100))
        txt = "Krzykacz ryczy z bólu pod naporem bełtów z kuszy! Nagle ziemia pęka – Lusia unosi ręce, a potężne, kolczaste pnącza i korzenie lasu owijają się wokół szyi potwora, miażdżąc go i wciągając pod ziemię.\n\nKlątwa została zdjęta. Ocalali mieszkańcy Chołów wiwatują na cześć wielkomiejskiego psychologa. Jerzy Drozd podchodzi do Lusi i mocno ją przytula. Koszmar Podlasia dobiegł końca."
        draw_wrapped_text(screen, txt, (100, 180), 700)
        if draw_btn(btn3, "Zagraj ponownie"):
            game.__init__()

    elif game.state == "GAME_OVER":
        screen.fill((30, 0, 0))
        title = font_title.render("NIE ŻYJESZ", True, PALETTE[4])
        screen.blit(title, (350, 150))
        draw_wrapped_text(screen, "Mroki Chołów cię pochłonęły. Jerzy Drozd stał się kolejną bezimienną ofiarą podlaskiego kultu i przedwiecznych demonów.", (200, 250), 500)
        if draw_btn(btn3, "Spróbuj ponownie"):
            game.__init__()

    pygame.display.flip()
    clock.tick(30)

pygame.quit()
sys.exit()
