import pygame
import numpy as np
import sys
import random

pygame.init()
WIDTH, HEIGHT = 900, 650
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Krzykacz: Tajemnica Chołów - Tekstury i Postaci")
clock = pygame.time.Clock()

TILE_SIZE = 50

# ==========================================
# 1. PROCEDURALNE GENEROWANIE TEKSTUR I GRAFIK
# ==========================================

def create_terrain_texture():
    """Generuje szum numeryczny imitujący błotnistą ziemię z rzadką trawą."""
    # Tworzymy tablicę (X, Y, RGB)
    noise = np.random.randint(20, 35, (TILE_SIZE, TILE_SIZE, 3))
    
    # Dodajemy losowe plamy ciemnej zieleni (trawa/mech)
    grass_mask = np.random.random((TILE_SIZE, TILE_SIZE)) > 0.85
    noise[grass_mask] = [25, 45, 20]
    
    return pygame.surfarray.make_surface(noise)

def create_wall_texture():
    """Generuje teksturę starych, horyzontalnych bali drewna."""
    tex = np.zeros((TILE_SIZE, TILE_SIZE, 3), dtype=int)
    for y in range(TILE_SIZE):
        color_val = 50 + random.randint(-4, 4)
        if y % 10 == 0 or y % 10 == 1: 
            color_val -= 20  # Szczeliny między balami
        tex[:, y] = [color_val, color_val - 15, color_val - 25]
    return pygame.surfarray.make_surface(tex)

def create_character_surface(body_color, skin_color, is_demon=False):
    """Rysuje postać (pionek RPG) z korpusem, głową i oczami."""
    surf = pygame.Surface((30, 40), pygame.SRCALPHA)
    
    # Korpus / Płaszcz
    pygame.draw.ellipse(surf, body_color, (2, 10, 26, 30))
    # Głowa
    pygame.draw.circle(surf, skin_color, (15, 12), 10)
    
    if is_demon:
        # Upiorne czerwone ślepia demona
        pygame.draw.circle(surf, (220, 20, 20), (11, 10), 2)
        pygame.draw.circle(surf, (220, 20, 20), (19, 10), 2)
    else:
        # Zwykłe oczy człowieka
        pygame.draw.circle(surf, (10, 10, 15), (11, 10), 1)
        pygame.draw.circle(surf, (10, 10, 15), (19, 10), 1)
        
    return surf

# Wygenerowanie zasobów w pamięci
TEX_TERRAIN = create_terrain_texture()
TEX_WALL = create_wall_texture()

SPRITE_PLAYER = create_character_surface((60, 60, 80), (220, 180, 150)) # Drozd w szarym płaszczu
SPRITE_NPC = create_character_surface((80, 120, 80), (240, 200, 170))   # Lusia w zieleni
SPRITE_DEMON = create_character_surface((30, 15, 40), (50, 40, 60), is_demon=True) # Mrok i czerwień

# ==========================================
# 2. STRUKTURA MAPY I FIZYKA
# ==========================================

MAP_DATA = [
    [1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1],
    [1, 0, 0, 0, 0, 0, 1, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1],
    [1, 0, 0, 2, 0, 0, 0, 0, 0, 0, 1, 1, 1, 0, 0, 3, 0, 1],
    [1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1, 0, 1, 0, 0, 0, 0, 1],
    [1, 1, 1, 0, 0, 0, 0, 0, 0, 0, 1, 1, 1, 0, 0, 0, 0, 1],
    [1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1],
    [1, 0, 0, 0, 0, 0, 0, 2, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1],
    [1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1],
]

class Player:
    def __init__(self, x, y):
        self.rect = pygame.Rect(x, y, 30, 40)
        self.speed = 5

    def move(self, dx, dy, walls):
        self.rect.x += dx
        for wall in walls:
            if self.rect.colliderect(wall):
                if dx > 0: self.rect.right = wall.left
                if dx < 0: self.rect.left = wall.right
        
        self.rect.y += dy
        for wall in walls:
            if self.rect.colliderect(wall):
                if dy > 0: self.rect.bottom = wall.top
                if dy < 0: self.rect.top = wall.bottom

# Budowanie środowiska
walls = []
npcs = []
demons = []

for row_idx, row in enumerate(MAP_DATA):
    for col_idx, tile in enumerate(row):
        x, y = col_idx * TILE_SIZE, row_idx * TILE_SIZE
        if tile == 1: walls.append(pygame.Rect(x, y, TILE_SIZE, TILE_SIZE))
        elif tile == 2: npcs.append(pygame.Rect(x + 10, y + 5, 30, 40))
        elif tile == 3: demons.append(pygame.Rect(x + 10, y + 5, 30, 40))

player = Player(100, 100)
font = pygame.font.SysFont("georgia", 20)
dialogue_text = ""

def resolve_dice_combat():
    drozd_roll = random.randint(1, 6) + random.randint(1, 6)
    demon_roll = random.randint(1, 6) + random.randint(1, 6)
    if drozd_roll > demon_roll: return f"Atakujesz! Wyrzuciłeś {drozd_roll}, Demon {demon_roll}. Masz przewagę."
    elif drozd_roll < demon_roll: return f"Unikasz! Wyrzuciłeś {drozd_roll}, Demon {demon_roll}. Tracisz krew."
    return f"Zwarcie! Remis {drozd_roll}:{demon_roll}. Napięcie rośnie."

# ==========================================
# 3. GŁÓWNA PĘTLA
# ==========================================
running = True
while running:
    # 1. Rysowanie terenu na całym ekranie (kafelek po kafelku)
    for y in range(0, HEIGHT, TILE_SIZE):
        for x in range(0, WIDTH, TILE_SIZE):
            screen.blit(TEX_TERRAIN, (x, y))

    dx, dy = 0, 0
    keys = pygame.key.get_pressed()
    
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        if event.type == pygame.KEYDOWN and event.key == pygame.K_e:
            interacted = False
            interaction_zone = player.rect.inflate(50, 50)
            
            for npc in npcs:
                if interaction_zone.colliderect(npc):
                    dialogue_text = "Mieszkaniec: Czego tu szukasz miastowy? Odejdź, póki masz nogi."
                    interacted = True
                    break
            for demon in demons:
                if interaction_zone.colliderect(demon):
                    dialogue_text = resolve_dice_combat()
                    interacted = True
                    break
            if not interacted: dialogue_text = ""

    # Poruszanie się (WASD / Strzałki)
    if keys[pygame.K_w] or keys[pygame.K_UP]: dy -= player.speed
    if keys[pygame.K_s] or keys[pygame.K_DOWN]: dy += player.speed
    if keys[pygame.K_a] or keys[pygame.K_LEFT]: dx -= player.speed
    if keys[pygame.K_d] or keys[pygame.K_RIGHT]: dx += player.speed

    player.move(dx, dy, walls)

    # 2. RENDEROWANIE OBIEKTÓW MAPY (Z użyciem tekstur i sprite'ów)
    for w in walls: 
        screen.blit(TEX_WALL, (w.x, w.y))
    
    for n in npcs: 
        screen.blit(SPRITE_NPC, (n.x, n.y))
        
    for d in demons: 
        screen.blit(SPRITE_DEMON, (d.x, d.y))
        
    screen.blit(SPRITE_PLAYER, (player.rect.x, player.rect.y))

    # 3. INTERFEJS UŻYTKOWNIKA
    interaction_zone = player.rect.inflate(50, 50)
    for entity in npcs + demons:
        if interaction_zone.colliderect(entity):
            prompt = font.render("[E] Interakcja", True, (255, 220, 100))
            screen.blit(prompt, (entity.x - 20, entity.y - 25))

    if dialogue_text:
        pygame.draw.rect(screen, (15, 12, 10), (50, 500, 800, 100))
        pygame.draw.rect(screen, (150, 120, 90), (50, 500, 800, 100), 3)
        txt_surf = font.render(dialogue_text, True, (240, 230, 220))
        screen.blit(txt_surf, (70, 535))

    pygame.display.flip()
    clock.tick(60)

pygame.quit()
sys.exit()
