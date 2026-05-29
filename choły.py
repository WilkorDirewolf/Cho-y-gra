import pygame
import sys
import random

pygame.init()
WIDTH, HEIGHT = 900, 650
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Krzykacz: Tajemnica Chołów - Silnik RPG")
clock = pygame.time.Clock()

# --- ZASTĘPCZA PALETA KOLORÓW ---
# W przyszłości zastąpimy te prostokąty plikami graficznymi (pygame.image.load)
C_BG = (20, 25, 30)         # Ziemia/Błoto
C_PLAYER = (180, 50, 50)    # Awatar Drozda
C_WALL = (80, 70, 60)       # Ściany chat
C_NPC = (100, 180, 100)     # Lusia / Mieszkańcy
C_ENEMY = (150, 0, 200)     # Demony
C_UI = (220, 200, 50)       # Złoty tekst interakcji

# --- MAPA WSI (Siatka 2D) ---
# 1 = Chaty/Przeszkody, 2 = Mieszkaniec, 3 = Ślad/Demon, 0 = Wolna przestrzeń
TILE_SIZE = 50
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

# --- KLASA GRACZA I FIZYKA KOLIZJI ---
class Player:
    def __init__(self, x, y):
        self.rect = pygame.Rect(x, y, 30, 40)
        self.speed = 5
        self.hp = 20

    def move(self, dx, dy, walls):
        # Osobna kalkulacja dla osi X i Y, aby gładko "ślizgać się" po ścianach
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
        elif tile == 2: npcs.append(pygame.Rect(x + 10, y + 10, 30, 30))
        elif tile == 3: demons.append(pygame.Rect(x + 10, y + 10, 30, 30))

player = Player(100, 100)
font = pygame.font.SysFont("georgia", 20)
dialogue_text = ""

# --- SYSTEM RZUTU KOŚĆMI (Mockup) ---
def resolve_dice_combat():
    drozd_roll = random.randint(1, 6) + random.randint(1, 6)
    demon_roll = random.randint(1, 6) + random.randint(1, 6)
    
    if drozd_roll > demon_roll:
        return f"Wyrzuciłeś {drozd_roll}, Demon {demon_roll}. Masz przewagę! Mod. Ataku +2"
    elif drozd_roll < demon_roll:
        return f"Wyrzuciłeś {drozd_roll}, Demon {demon_roll}. Przegrywasz! Mod. Obrony -2"
    else:
        return f"Remis {drozd_roll}:{demon_roll}. Wyrównana walka."

# --- GŁÓWNA PĘTLA ---
running = True
while running:
    screen.fill(C_BG)
    dx, dy = 0, 0
    keys = pygame.key.get_pressed()
    
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        if event.type == pygame.KEYDOWN and event.key == pygame.K_e:
            interacted = False
            # Sprawdzanie obszaru interakcji (rozszerzony kwadrat kolizji)
            interaction_zone = player.rect.inflate(50, 50)
            
            for npc in npcs:
                if interaction_zone.colliderect(npc):
                    dialogue_text = "Mieszkaniec: Czego tu szukasz miastowy? Zostaw nas w spokoju."
                    interacted = True
                    break
            
            for demon in demons:
                if interaction_zone.colliderect(demon):
                    dialogue_text = resolve_dice_combat()
                    interacted = True
                    break
                    
            if not interacted:
                dialogue_text = ""

    # Poruszanie się (WASD / Strzałki)
    if keys[pygame.K_w] or keys[pygame.K_UP]: dy -= player.speed
    if keys[pygame.K_s] or keys[pygame.K_DOWN]: dy += player.speed
    if keys[pygame.K_a] or keys[pygame.K_LEFT]: dx -= player.speed
    if keys[pygame.K_d] or keys[pygame.K_RIGHT]: dx += player.speed

    player.move(dx, dy, walls)

    # RENDEROWANIE (Zastępcze kształty do wymiany na pliki .png)
    for w in walls: pygame.draw.rect(screen, C_WALL, w)
    for n in npcs: pygame.draw.rect(screen, C_NPC, n)
    for d in demons: pygame.draw.rect(screen, C_ENEMY, d)
    pygame.draw.rect(screen, C_PLAYER, player.rect)

    # Wskaźnik interakcji unoszący się nad obiektem
    interaction_zone = player.rect.inflate(50, 50)
    for entity in npcs + demons:
        if interaction_zone.colliderect(entity):
            prompt = font.render("[E]", True, C_UI)
            screen.blit(prompt, (entity.x + 5, entity.y - 25))

    # Ramka dialogowa / Walki
    if dialogue_text:
        pygame.draw.rect(screen, (10, 10, 15), (50, 500, 800, 100))
        pygame.draw.rect(screen, (200, 200, 200), (50, 500, 800, 100), 2)
        txt_surf = font.render(dialogue_text, True, (255, 255, 255))
        screen.blit(txt_surf, (70, 540))

    pygame.display.flip()
    clock.tick(60)

pygame.quit()
sys.exit()
