import pygame
import sys
import os
import random
import math

pygame.init()

# Configuration
WIDTH, HEIGHT = 960, 640
FPS = 60
PLAYER_VEL = 6
TILE_SIZE = 32
MAX_LIVES = 5

window = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("L'Odyssée : Le Retour du Roi")

# Couleurs
BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
BROWN = (139, 69, 19)
GRAY = (100, 100, 100)
DIALOGUE_BG = (20, 20, 40, 200)

# Couleurs Interface Style Hades
HADES_GOLD = (255, 215, 0)
HADES_HIGHLIGHT = (255, 255, 255, 50)

def load_sprite(filename, scale=None):
    """Charge un sprite et le redimensionne si besoin"""
    possible_paths = [
        os.path.join("assets", filename),
        f"assets/{filename}",
        os.path.join(os.path.dirname(__file__), "assets", filename)
    ]
    
    for sprite_path in possible_paths:
        try:
            sprite = pygame.image.load(sprite_path).convert_alpha()
            if scale:
                sprite = pygame.transform.scale(sprite, scale)
            return sprite
        except Exception:
            continue
    print(f"✗ Échec du chargement de '{filename}'")
    return None

def load_menu_background():
    """Charge l'image du menu générée (menu_hades.png)"""
    bg = load_sprite("menu_hades.png") 
    if bg:
        bg = pygame.transform.scale(bg, (WIDTH, HEIGHT))
        return bg
    print("! menu_hades.png introuvable.")
    return None

def load_player_sprite(): return load_sprite("player.png", (32, 32))
def load_heart_sprite(): return load_sprite("heart.png", (48, 48))  # Agrandi
def load_cyclops_sprite(): return load_sprite("cyclope.png", (32, 32))
def load_miro_sprite(): return load_sprite("miro.png", (64, 64))
def load_shower_sprite(): return load_sprite("shower.png", (48, 48))
def load_Odysseus_portrait(): return load_sprite("ulysse.png")
def load_cyclops_portrait(): return load_sprite("cyclope_portrait.png")
def load_siren1_portrait(): return load_sprite("siren1.png")
def load_siren2_portrait(): return load_sprite("siren2.png")
def load_game_over_image(): return load_sprite("game_over_img.png")
def load_victory_image(): return load_sprite("absolute_cinema.png")

def load_background():
    bg = load_sprite("background.png", (WIDTH, HEIGHT))
    if bg: return bg
    
    print("Utilisation d'un fond généré par défaut")
    bg = pygame.Surface((WIDTH, HEIGHT))
    for y in range(HEIGHT):
        color_value = int(30 + (y / HEIGHT) * 30)
        pygame.draw.line(bg, (color_value, color_value, color_value + 40), (0, y), (WIDTH, y))
    return bg

def load_ocean_background():
    bg = load_sprite("ocean_background.png", (WIDTH, HEIGHT))
    if bg: return bg
    
    print("Utilisation d'un fond océan par défaut")
    bg = pygame.Surface((WIDTH, HEIGHT))
    for y in range(HEIGHT):
        color_value = int(50 + (y / HEIGHT) * 100)
        pygame.draw.line(bg, (20, color_value, color_value + 50), (0, y), (WIDTH, y))
    return bg

def load_tileset():
    possible_paths = [
        os.path.join("assets", "tileset.png"),
        "assets/tileset.png",
        os.path.join(os.path.dirname(__file__), "assets", "tileset.png")
    ]
    for tileset_path in possible_paths:
        try:
            tileset = pygame.image.load(tileset_path).convert_alpha()
            tiles = {}
            tileset_width = tileset.get_width() // 16
            tileset_height = tileset.get_height() // 16
            
            tile_surface = pygame.Surface((16, 16), pygame.SRCALPHA)
            rect = pygame.Rect(0, 0, 16, 16)
            tile_surface.blit(tileset, (0, 0), rect)
            tile_surface = pygame.transform.scale(tile_surface, (TILE_SIZE, TILE_SIZE))
            tiles['block'] = tile_surface
            tiles['wall'] = tile_surface
            return tiles
        except Exception:
            continue
    
    default_tile = pygame.Surface((TILE_SIZE, TILE_SIZE))
    default_tile.fill(BROWN)
    pygame.draw.rect(default_tile, (100, 60, 10), default_tile.get_rect(), 2)
    return {'block': default_tile, 'wall': default_tile}

# --- CLASSE DU MENU PRINCIPAL ---
class MainMenu:
    def __init__(self, background):
        self.background = background
        self.play_rect = pygame.Rect(95, 250, 280, 75)
        self.hovered = False

    def update(self, events):
        mouse_pos = pygame.mouse.get_pos()
        self.hovered = self.play_rect.collidepoint(mouse_pos)

        for event in events:
            if event.type == pygame.MOUSEBUTTONDOWN:
                if event.button == 1 and self.hovered:
                    return "start"
        return None

    def draw(self, surface):
        if self.background:
            surface.blit(self.background, (0, 0))
        else:
            surface.fill((30, 0, 0))

        if self.hovered:
            pygame.draw.rect(surface, HADES_GOLD, self.play_rect, 3)
            highlight = pygame.Surface((self.play_rect.width, self.play_rect.height), pygame.SRCALPHA)
            highlight.fill(HADES_HIGHLIGHT)
            surface.blit(highlight, self.play_rect.topleft)

# --- CLASSES DU JEU ---

class DialogueScene:
    def __init__(self, background, dialogue_type="Cyclops", portraits=None):
        self.background = background
        self.portraits = portraits or {}
        self.font = pygame.font.Font(None, 36)
        self.font_large = pygame.font.Font(None, 48)
        self.portrait_data = {}
        
        if 'Odysseus' in self.portraits and self.portraits['Odysseus']:
            portrait = self.portraits['Odysseus']
            max_height = HEIGHT - 150
            max_width = WIDTH // 2 - 100
            ratio = min(max_width / portrait.get_width(), max_height / portrait.get_height())
            scaled = pygame.transform.scale(portrait, (int(portrait.get_width() * ratio), int(portrait.get_height() * ratio)))
            self.portrait_data['Odysseus'] = {'image': scaled, 'pos': (50, HEIGHT - scaled.get_height() - 140)}
        
        if dialogue_type == "Cyclops":
            if 'Cyclops' in self.portraits and self.portraits['Cyclops']:
                portrait = self.portraits['Cyclops']
                max_height = HEIGHT - 150
                max_width = WIDTH // 2 - 100
                ratio = min(max_width / portrait.get_width(), max_height / portrait.get_height())
                scaled = pygame.transform.scale(portrait, (int(portrait.get_width() * ratio), int(portrait.get_height() * ratio)))
                self.portrait_data['Cyclops'] = {'image': scaled, 'pos': (WIDTH - scaled.get_width() - 50, HEIGHT - scaled.get_height() - 140)}
            
            self.dialogues = [
                ("Odysseus", "I am Odysseus, certified SCRUM MASTER, who are you creature?"),
                ("Cyclops", "I am a Java Addict, son of IDE god!"),
                ("Cyclops", "You haven't submitted your assignment on time... You will be my meal!"),
                ("Odysseus", "I will not be devoured without a fight!"),
                ("Odysseus", "I must escape from this Blackboard cave before she catches me and force me to do JAVA!"),
            ]
        
        elif dialogue_type == "sirens":
            if 'siren1' in self.portraits and self.portraits['siren1']:
                portrait = self.portraits['siren1']
                max_height = HEIGHT - 150
                max_width = WIDTH // 3 - 50
                ratio = min(max_width / portrait.get_width(), max_height / portrait.get_height())
                scaled = pygame.transform.scale(portrait, (int(portrait.get_width() * ratio), int(portrait.get_height() * ratio)))
                self.portrait_data['siren1'] = {'image': scaled, 'pos': (WIDTH // 2 + 20, HEIGHT - scaled.get_height() - 140)}
            
            if 'siren2' in self.portraits and self.portraits['siren2']:
                portrait = self.portraits['siren2']
                max_height = HEIGHT - 150
                max_width = WIDTH // 3 - 50
                ratio = min(max_width / portrait.get_width(), max_height / portrait.get_height())
                scaled = pygame.transform.scale(portrait, (int(portrait.get_width() * ratio), int(portrait.get_height() * ratio)))
                self.portrait_data['siren2'] = {'image': scaled, 'pos': (WIDTH - scaled.get_width() - 50, HEIGHT - scaled.get_height() - 140)}
            
            self.dialogues = [
                ("siren1", "Ohh... ARE YOU ALIVE ???"),
                ("siren2", "Come my child, join us or else I'll Kirill you !"),
                ("Odysseus", "Your voices are enchanting, but I know your traps!"),
                ("siren1", "We want you to stay with us..IS THAT CLEAR TO YOU?????"),
                ("Odysseus", "Never! I must find my way back to my coffee store!"),
                ("siren2", "Then flee, mortal... If you can!"),
            ]
        
        self.current_dialogue = 0
        self.finished = False
    
    def draw_dialogue_box(self, surface, text, speaker_name):
        box_height = 120
        box_rect = pygame.Rect(50, HEIGHT - box_height - 20, WIDTH - 100, box_height)
        
        dialogue_surface = pygame.Surface((box_rect.width, box_rect.height), pygame.SRCALPHA)
        dialogue_surface.fill(DIALOGUE_BG)
        surface.blit(dialogue_surface, box_rect.topleft)
        pygame.draw.rect(surface, WHITE, box_rect, 3)
        
        name_text = self.font_large.render(speaker_name, True, (255, 215, 0))
        surface.blit(name_text, (box_rect.x + 20, box_rect.y + 10))
        
        words = text.split()
        lines = []
        current_line = ""
        for word in words:
            test_line = current_line + word + " "
            if self.font.size(test_line)[0] < box_rect.width - 40:
                current_line = test_line
            else:
                lines.append(current_line)
                current_line = word + " "
        lines.append(current_line)
        
        y_offset = box_rect.y + 55
        for line in lines:
            dialogue_text = self.font.render(line, True, WHITE)
            surface.blit(dialogue_text, (box_rect.x + 20, y_offset))
            y_offset += 35
        
        hint_text = self.font.render("Press SPACE to continue...", True, GRAY)
        surface.blit(hint_text, (WIDTH - 380, HEIGHT - 30))
    
    def update(self, events):
        for event in events:
            if event.type == pygame.KEYDOWN and event.key == pygame.K_SPACE:
                self.current_dialogue += 1
                if self.current_dialogue >= len(self.dialogues):
                    self.finished = True
    
    def draw(self, surface):
        surface.blit(self.background, (0, 0))
        if self.current_dialogue < len(self.dialogues):
            speaker, text = self.dialogues[self.current_dialogue]
            speaker_names = {"Odysseus": "Odysseus", "Cyclops": "Cyclops", "siren1": "Siren", "siren2": "Siren"}
            if speaker in self.portrait_data:
                data = self.portrait_data[speaker]
                surface.blit(data['image'], data['pos'])
            self.draw_dialogue_box(surface, text, speaker_names.get(speaker, speaker))

class Player(pygame.sprite.Sprite):
    GRAVITY = 0.5
    JUMP_STRENGTH = -10
    
    def __init__(self, x, y, sprite_image=None):
        super().__init__()
        self.width = 32
        self.height = 32 if sprite_image else 48
        self.rect = pygame.Rect(x, y, self.width, self.height)
        self.x_vel = 0
        self.y_vel = 0
        self.jump_count = 0
        self.on_ground = False
        self.direction = 1
        self.sprite_image = sprite_image
        self.sprite_flipped = pygame.transform.flip(sprite_image, True, False) if sprite_image else None
        self.lives = MAX_LIVES
        
    def jump(self):
        if self.jump_count < 2:
            self.y_vel = self.JUMP_STRENGTH
            self.jump_count += 1
            self.on_ground = False
    
    def move(self, dx, dy):
        self.rect.x += dx
        self.rect.y += dy
    
    def update(self, platforms):
        self.y_vel = min(self.y_vel + self.GRAVITY, 15)
        self.move(self.x_vel, 0)
        self.check_collision_x(platforms)
        self.move(0, self.y_vel)
        self.on_ground = False
        self.check_collision_y(platforms)
        self.rect.clamp_ip(window.get_rect())
    
    def check_collision_x(self, platforms):
        for platform in platforms:
            if self.rect.colliderect(platform.rect):
                if self.x_vel > 0: self.rect.right = platform.rect.left
                elif self.x_vel < 0: self.rect.left = platform.rect.right
    
    def check_collision_y(self, platforms):
        for platform in platforms:
            if self.rect.colliderect(platform.rect):
                if self.y_vel > 0:
                    self.rect.bottom = platform.rect.top
                    self.y_vel = 0
                    self.on_ground = True
                    self.jump_count = 0
                elif self.y_vel < 0:
                    self.rect.top = platform.rect.bottom
                    self.y_vel = 0
    
    def draw(self, surface):
        if self.sprite_image:
            img = self.sprite_flipped if self.direction == -1 else self.sprite_image
            surface.blit(img, (self.rect.x, self.rect.y))
        else:
            pygame.draw.rect(surface, (255, 0, 0), self.rect)

class Cyclops(pygame.sprite.Sprite):
    SPEED = 1.5
    def __init__(self, x, y, sprite_image=None):
        super().__init__()
        width = sprite_image.get_width() if sprite_image else 32
        height = sprite_image.get_height() if sprite_image else 32
        self.rect = pygame.Rect(x, y, width, height)
        self.start_x = x
        self.start_y = y
        self.sprite_image = sprite_image
        self.sprite_flipped = pygame.transform.flip(sprite_image, True, False) if sprite_image else None
        self.direction = 1

    def update(self, player_rect):
        dx = player_rect.centerx - self.rect.centerx
        dy = player_rect.centery - self.rect.centery
        dist = math.hypot(dx, dy)
        if dist != 0:
            self.rect.x += (dx / dist) * self.SPEED
            self.rect.y += (dy / dist) * self.SPEED
            self.direction = 1 if dx > 0 else -1

    def reset_position(self):
        self.rect.x = self.start_x
        self.rect.y = self.start_y

    def draw(self, surface):
        if self.sprite_image:
            img = self.sprite_flipped if self.direction == -1 else self.sprite_image
            surface.blit(img, (self.rect.x, self.rect.y))
        else:
            pygame.draw.rect(surface, (150, 0, 150), self.rect)

class Heart(pygame.sprite.Sprite):
    def __init__(self, x, y, sprite_image):
        super().__init__()
        self.image = sprite_image
        self.rect = self.image.get_rect(topleft=(x, y))
    def draw(self, surface): surface.blit(self.image, self.rect)

class Platform(pygame.sprite.Sprite):
    def __init__(self, x, y, width, height, tile_image=None, tile_type=0):
        super().__init__()
        self.rect = pygame.Rect(x, y, width, height)
        self.tile_image = tile_image
    def draw(self, surface):
        if self.tile_image:
            for ty in range(self.rect.height // TILE_SIZE):
                for tx in range(self.rect.width // TILE_SIZE):
                    surface.blit(self.tile_image, (self.rect.x + tx * TILE_SIZE, self.rect.y + ty * TILE_SIZE))
        else:
            pygame.draw.rect(surface, BROWN, self.rect)
            pygame.draw.rect(surface, (100, 60, 10), self.rect, 2)

class Shower(pygame.sprite.Sprite):
    """Douche qui redonne de la vie"""
    def __init__(self, x, y, sprite_image=None):
        super().__init__()
        self.rect = pygame.Rect(x, y, 48, 48)
        self.sprite_image = sprite_image
        self.animation_frame = 0
    
    def update(self):
        self.animation_frame = (self.animation_frame + 1) % 30
    
    def draw(self, surface):
        if self.sprite_image:
            surface.blit(self.sprite_image, (self.rect.x, self.rect.y))
        else:
            # Fallback bleu
            color = [(100, 150, 255), (120, 170, 255), (140, 190, 255)][self.animation_frame // 10]
            pygame.draw.rect(surface, color, self.rect)

class Exit(pygame.sprite.Sprite):
    def __init__(self, x, y, width, height):
        super().__init__()
        self.rect = pygame.Rect(x, y, width, height)
        self.animation_frame = 0
    def update(self): self.animation_frame = (self.animation_frame + 1) % 60
    def draw(self, surface):
        glow = abs((self.animation_frame - 30)) / 30.0
        c_base = int(100 + glow * 100)
        color = (c_base, 200 + int(glow * 55), c_base)
        pygame.draw.rect(surface, (80, 80, 80), self.rect, 4)
        pygame.draw.rect(surface, color, self.rect.inflate(-8, -8))

def generate_random_level(level_num, tiles, enemy_sprite, shower_sprite):
    platforms, showers, enemy_list = [], [], []
    platform_tile = tiles.get('block') if tiles else None
    wall_tile = tiles.get('wall') if tiles else None
    
    # Bordures
    for i in range(WIDTH // TILE_SIZE + 1):
        platforms.append(Platform(i * TILE_SIZE, 0, TILE_SIZE, TILE_SIZE, wall_tile))
        platforms.append(Platform(i * TILE_SIZE, TILE_SIZE, TILE_SIZE, TILE_SIZE, wall_tile))
        platforms.append(Platform(i * TILE_SIZE, HEIGHT - TILE_SIZE, TILE_SIZE, TILE_SIZE, wall_tile))
        platforms.append(Platform(i * TILE_SIZE, HEIGHT - TILE_SIZE * 2, TILE_SIZE, TILE_SIZE, wall_tile))
    for i in range(HEIGHT // TILE_SIZE + 1):
        platforms.append(Platform(0, i * TILE_SIZE, TILE_SIZE, TILE_SIZE, wall_tile))
        platforms.append(Platform(TILE_SIZE, i * TILE_SIZE, TILE_SIZE, TILE_SIZE, wall_tile))
    
    exit_start = (HEIGHT // 2) // TILE_SIZE - 2
    for i in range(HEIGHT // TILE_SIZE + 1):
        if i < exit_start or i > exit_start + 4:
            platforms.append(Platform(WIDTH - TILE_SIZE, i * TILE_SIZE, TILE_SIZE, TILE_SIZE, wall_tile))
            platforms.append(Platform(WIDTH - TILE_SIZE * 2, i * TILE_SIZE, TILE_SIZE, TILE_SIZE, wall_tile))
    
    enemy_height = enemy_sprite.get_height() if enemy_sprite else 32
    
    possible_enemy_spawns = []
    for _ in range(12 + (level_num % 5)):
        x = random.randint(TILE_SIZE * 4, WIDTH - TILE_SIZE * 6)
        y = random.randint(TILE_SIZE * 4, HEIGHT - TILE_SIZE * 4)
        x, y = (x // TILE_SIZE) * TILE_SIZE, (y // TILE_SIZE) * TILE_SIZE
        width = random.choice([64, 96, 128, 160])
        platforms.append(Platform(x, y, width, 32, platform_tile))
        possible_enemy_spawns.append((x + width // 2, y - enemy_height))

    # Douches au lieu des obstacles de feu
    for _ in range(min(level_num // 2, 5)):
        x = random.randint(TILE_SIZE * 4, WIDTH - TILE_SIZE * 6)
        y = HEIGHT - TILE_SIZE * 2 - 64
        showers.append(Shower(x, y, shower_sprite))

    if possible_enemy_spawns:
        random.shuffle(possible_enemy_spawns)
        for i in range(min(10, len(possible_enemy_spawns))):
            enemy_list.append(Cyclops(possible_enemy_spawns[i][0], possible_enemy_spawns[i][1], enemy_sprite))
    
    return platforms, showers, Exit(WIDTH - TILE_SIZE * 2 - 32, HEIGHT // 2 - 64, 64, 128), enemy_list

def reset_player(player):
    player.rect.topleft = (100, HEIGHT - 200)
    player.x_vel, player.y_vel = 0, 0

# --- BOUCLE PRINCIPALE ---

def main():
    clock = pygame.time.Clock()
    
    print("Chargement des ressources...")
    cave_bg = load_background()
    ocean_bg = load_ocean_background()
    menu_bg = load_menu_background()
    
    tiles = load_tileset()
    player_sprite = load_player_sprite()
    heart_sprite = load_heart_sprite()
    shower_sprite = load_shower_sprite()
    
    # Chargement des sprites ennemis
    cyclops_sprite = load_cyclops_sprite()
    miro_sprite = load_miro_sprite()
    
    Odysseus_p = load_Odysseus_portrait()
    cyclops_p = load_cyclops_portrait()
    siren1_p = load_siren1_portrait()
    siren2_p = load_siren2_portrait()
    game_over_img = load_game_over_image() 
    victory_img = load_victory_image()
    print("Ressources chargées!")
    
    # --- ETATS DU JEU ---
    GAME_STATE_MENU = 0
    GAME_STATE_DIALOGUE = 1
    GAME_STATE_PLAYING = 2
    
    current_state = GAME_STATE_MENU
    
    # Initialisation du Menu
    main_menu = MainMenu(menu_bg)

    # Initialisation Scène Dialogue
    dialogue_scene = DialogueScene(cave_bg, "Cyclops", {'Odysseus': Odysseus_p, 'Cyclops': cyclops_p})
    
    # Initialisation Jeu
    current_level = 1
    levels_per_biome = 3 # 3 niveaux par biome
    max_levels = 6       # 6 niveaux au total
    current_biome = 1 
    current_bg = cave_bg
    
    player = Player(100, HEIGHT - 200, player_sprite)
    
    # Sélectionne le sprite ennemi selon le biome initial (1 = Cyclope)
    current_enemy_sprite = cyclops_sprite if current_biome == 1 else miro_sprite
    platforms, showers, exit_door, enemy_list = generate_random_level(current_level, tiles, current_enemy_sprite, shower_sprite)
    
    hearts = []
    if heart_sprite:
        for i in range(MAX_LIVES): hearts.append(Heart(20 + i * 55, 20, heart_sprite))

    font = pygame.font.Font(None, 48)
    big_font = pygame.font.Font(None, 72)
    
    running = True
    game_over = False
    victory = False
    waiting_for_siren_dialogue = False

    while running:
        clock.tick(FPS)
        events = pygame.event.get()
        for event in events:
            if event.type == pygame.QUIT: running = False

        # --- GESTION DES ETATS ---
        
        # 1. MENU
        if current_state == GAME_STATE_MENU:
            action = main_menu.update(events)
            if action == "start":
                current_state = GAME_STATE_DIALOGUE
            main_menu.draw(window)

        # 2. DIALOGUE
        elif current_state == GAME_STATE_DIALOGUE:
            dialogue_scene.update(events)
            dialogue_scene.draw(window)
            
            if dialogue_scene.finished:
                current_state = GAME_STATE_PLAYING
                if waiting_for_siren_dialogue:
                    waiting_for_siren_dialogue = False
        
        # 3. JEU (PLAYING)
        elif current_state == GAME_STATE_PLAYING:
            for event in events:
                if event.type == pygame.KEYDOWN:
                    if not game_over and not victory:
                        if event.key == pygame.K_SPACE: player.jump()
                    
                    if game_over or victory:
                        if event.key == pygame.K_r:
                            # Reset
                            current_level = 1
                            current_biome = 1
                            current_bg = cave_bg
                            player.lives = MAX_LIVES
                            reset_player(player)
                            
                            current_enemy_sprite = cyclops_sprite if current_biome == 1 else miro_sprite
                            platforms, showers, exit_door, enemy_list = generate_random_level(current_level, tiles, current_enemy_sprite, shower_sprite)
                            game_over = False
                            victory = False

            if not game_over and not victory:
                keys = pygame.key.get_pressed()
                player.x_vel = 0
                if keys[pygame.K_LEFT]: 
                    player.x_vel = -PLAYER_VEL
                    player.direction = -1
                if keys[pygame.K_RIGHT]: 
                    player.x_vel = PLAYER_VEL
                    player.direction = 1
                
                player.update(platforms)
                
                for s in showers: s.update()
                for c in enemy_list: c.update(player.rect)
                exit_door.update()
                
                # Douches redonnent de la vie
                for shower in showers[:]:
                    if player.rect.colliderect(shower.rect):
                        if player.lives < MAX_LIVES:
                            player.lives += 1
                        showers.remove(shower)
                
                hit_enemy = any(player.rect.colliderect(c.rect) for c in enemy_list)

                if hit_enemy:
                    player.lives -= 1
                    if player.lives <= 0: 
                        game_over = True
                    else: 
                        reset_player(player)
                        # Réinitialiser la position des ennemis quand le joueur meurt
                        for c in enemy_list:
                            c.reset_position()
                
                if player.rect.colliderect(exit_door.rect):
                    if current_level < max_levels:
                        current_level += 1
                        
                        # Changement de Biome
                        if current_level == levels_per_biome + 1 and current_biome == 1:
                            current_biome = 2
                            current_bg = ocean_bg
                            dialogue_scene = DialogueScene(ocean_bg, "sirens", {'Odysseus': Odysseus_p, 'siren1': siren1_p, 'siren2': siren2_p})
                            current_state = GAME_STATE_DIALOGUE
                            waiting_for_siren_dialogue = True
                        
                        # Génération du niveau avec le bon sprite
                        current_enemy_sprite = cyclops_sprite if current_biome == 1 else miro_sprite
                        platforms, showers, exit_door, enemy_list = generate_random_level(current_level, tiles, current_enemy_sprite, shower_sprite)
                        reset_player(player)
                    else:
                        victory = True
            
            # Dessin
            window.blit(current_bg, (0, 0))
            for p in platforms: p.draw(window)
            for s in showers: s.draw(window)
            exit_door.draw(window)
            player.draw(window)
            for c in enemy_list: c.draw(window)
            
            if heart_sprite:
                for i in range(player.lives): hearts[i].draw(window)
            else:
                window.blit(font.render(f"Lives: {player.lives}", True, WHITE), (20, 20))

            biome_name = "Java Cave" if current_biome == 1 else "Prosanta's Sea"
            lvl_in_biome = current_level if current_biome == 1 else current_level - levels_per_biome
            window.blit(font.render(f"{biome_name} - Level {lvl_in_biome}/{levels_per_biome}", True, WHITE), (WIDTH - 500, 20))
            
            if victory:
                # Affiche l'image de victoire si elle est chargée
                if victory_img:
                    scaled_img = pygame.transform.scale(victory_img, (WIDTH, HEIGHT))
                    window.blit(scaled_img, (0, 0))
                else:
                    pygame.draw.rect(window, BLACK, (0, 0, WIDTH, HEIGHT))
                window.blit(big_font.render("VICTORY!", True, HADES_GOLD), (WIDTH // 2 - 150, HEIGHT // 2 - 50))
                window.blit(font.render("Press R to restart", True, WHITE), (WIDTH // 2 - 250, HEIGHT // 2 + 20))
            elif game_over:
                if game_over_img:
                    scaled_img = pygame.transform.scale(game_over_img, (WIDTH, HEIGHT))
                    window.blit(scaled_img, (0, 0))
                else:
                    pygame.draw.rect(window, BLACK, (0, 0, WIDTH, HEIGHT))
                
                window.blit(big_font.render("GAME OVER", True, (255, 0, 0)), (WIDTH // 2 - 150, HEIGHT // 2 - 50))
                window.blit(font.render("Press R to restart", True, WHITE), (WIDTH // 2 - 250, HEIGHT // 2 + 20))
        
        pygame.display.flip()
    
    pygame.quit()
    sys.exit()

if __name__ == "__main__":
    main()