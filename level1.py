import pygame
import os
import sys
import argparse
import random
import sqlite3

parser = argparse.ArgumentParser()
parser.add_argument("map", type=str, nargs="?", default="map1.map")
args = parser.parse_args()
map_file = args.map
player = None
running = True
clock = pygame.time.Clock()
sprite_group = pygame.sprite.Group()
heroes_group = pygame.sprite.Group()


def load_image(name, color_key=None):
    fullname = os.path.join('data', name)
    try:
        image = pygame.image.load(fullname)
    except pygame.error as message:
        print('Не удаётся загрузить:', name)
        raise SystemExit(message)
    image = image.convert_alpha()
    if color_key is not None:
        if color_key == -1:
            color_key = image.get_at((0, 0))
        image.set_colorkey(color_key)
    return image


pygame.init()
screen_size = (500, 500)
width = 500
height = 500
screen = pygame.display.set_mode(screen_size)
FPS = 50
gravity = 0.25

screen_rect = (0, 0, width, height)


class Particle(pygame.sprite.Sprite):
    # сгенерируем частицы разного размера
    fire = [load_image("star.png")]
    for scale in (5, 10, 20):
        fire.append(pygame.transform.scale(fire[0], (scale, scale)))

    def __init__(self, pos, dx, dy):
        super().__init__(all_sprites)
        self.image = random.choice(self.fire)
        self.rect = self.image.get_rect()

        # у каждой частицы своя скорость - это вектор
        self.velocity = [dx, dy]
        # и свои координаты
        self.rect.x = pos[0]
        self.rect.y = pos[1]

        # гравитация будет одинаковой
        self.gravity = gravity

    def update(self):
        # применяем гравитационный эффект:
        # движение с ускорением под действием гравитации
        self.velocity[1] += self.gravity
        # перемещаем частицу
        self.rect.x += self.velocity[0]
        self.rect.y += self.velocity[1]
        # убиваем, если частица ушла за экран
        if not self.rect.colliderect(screen_rect):
            self.kill()


def create_particles(position):
    # количество создаваемых частиц
    particle_count = 20
    # возможные скорости
    numbers = range(-5, 6)
    for _ in range(particle_count):
        Particle(position, random.choice(numbers), random.choice(numbers))


all_sprites = pygame.sprite.Group()

tile_images = {
    'wall': load_image('box.png'),
    'empty': load_image('grass.png'),
    'bomb': load_image('bomb.png'),
    'prin1': load_image('prin1.png'),
    'prin2': load_image('prin2.png'),
    'prin3': load_image('prin3.png'),
    'prin4': load_image('prin4.png'),
    'prin5': load_image('prin5.png')
}


tile_width = tile_height = 50


class SpriteGroup(pygame.sprite.Group):

    def __init__(self):
        super().__init__()

    def get_event(self, event):
        for sprite in self:
            sprite.get_event(event)


class Sprite(pygame.sprite.Sprite):

    def __init__(self, group):
        super().__init__(group)
        self.rect = None

    def get_event(self, event):
        pass


class Tile(Sprite):
    def __init__(self, tile_type, pos_x, pos_y):
        super().__init__(sprite_group)
        self.image = tile_images[tile_type]
        self.rect = self.image.get_rect().move(
            tile_width * pos_x, tile_height * pos_y)
        self.abs_pos = (self.rect.x, self.rect.y)


player_image = load_image("mar.png")


class Player(Sprite):
    def __init__(self, pos_x, pos_y):
        super().__init__(heroes_group)
        self.image = player_image
        self.rect = self.image.get_rect().move(
            tile_width * pos_x, tile_height * pos_y)
        self.pos = (pos_x, pos_y)

    def move(self, x, y):
        camera.dx -= tile_width * (x - self.pos[0])
        camera.dy -= tile_height * (y - self.pos[1])
        self.pos = (x, y)
        for sprite in sprite_group:
            camera.apply(sprite)


class Camera:
    def __init__(self):
        self.dx = 0
        self.dy = 0

    def apply(self, obj):
        obj.rect.x = obj.abs_pos[0] + self.dx
        obj.rect.y = obj.abs_pos[1] + self.dy

    def update(self, target):
        self.dx = 0
        self.dy = 0


def terminate():
    pygame.quit()
    sys.exit

def stop_music():
    pygame.mixer.music.stop()

def start_screen():
    pygame.mixer.music.load('data/ghoul.mp3')
    pygame.mixer.music.play()
    intro_text = ["Find princesses", "правила игры:",
                  "вам нужно найти всех принцесс и не нарваться на бомбы."]

    fon = pygame.transform.scale(load_image('fon.jpg'), screen_size)
    screen.blit(fon, (0, 0))
    font = pygame.font.Font(None, 30)
    text_coord = 50
    for line in intro_text:
        string_rendered = font.render(line, 1, pygame.Color('black'))
        intro_rect = string_rendered.get_rect()
        text_coord += 10
        intro_rect.top = text_coord
        intro_rect.x = 10
        text_coord += intro_rect.height
        screen.blit(string_rendered, intro_rect)

    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                terminate()
            elif event.type == pygame.MOUSEBUTTONDOWN:
                stop_music()
                return
        pygame.display.flip()
        clock.tick(FPS)


def load_level(filename):
    filename = "data/" + filename
    with open(filename, 'r') as mapFile:
        level_map = [line.strip() for line in mapFile]
    max_width = max(map(len, level_map))
    return list(map(lambda x: list(x.ljust(max_width, '.')), level_map))


def generate_level(level):
    new_player, x, y = None, None, None
    for y in range(len(level)):
        for x in range(len(level[y])):
            if level[y][x] == '.':
                Tile('empty', x, y)
            elif level[y][x] == '#':
                Tile('wall', x, y)
            elif level[y][x] == '@':
                Tile('empty', x, y)
                new_player = Player(x, y)
                level[y][x] = "."
            elif level[y][x] == '!':
                Tile('bomb', x, y)
            elif level[y][x] == '1':
                Tile('empty', x, y)
                Tile('prin1', x, y)
            elif level[y][x] == '2':
                Tile('empty', x, y)
                Tile('prin2', x, y)
            elif level[y][x] == '3':
                Tile('empty', x, y)
                Tile('prin3', x, y)
            elif level[y][x] == '4':
                Tile('empty', x, y)
                Tile('prin4', x, y)
            elif level[y][x] == '5':
                Tile('empty', x, y)
                Tile('prin5', x, y)
    return new_player, x, y


def move(hero, movement):
    x, y = hero.pos
    if movement == "up":
        if y > 0 and level_map[y - 1][x] == ".":
            hero.move(x, y - 1)
        elif y > 0 and level_map[y - 1][x] == "!":
            hero.move(x, y - 1)
            death_screen()
        elif y > 0 and level_map[y - 1][x] == "1":
            hero.move(x, y - 1)
            create_particles([x, y - 1])
            level_map[y - 1][x] = "."
            Tile('empty', x, y - 1)
            count()
        elif y > 0 and level_map[y - 1][x] == "2":
            hero.move(x, y - 1)
            create_particles([x, y - 1])
            level_map[y - 1][x] = "."
            Tile('empty', x, y - 1)
            count()
        elif y > 0 and level_map[y - 1][x] == "3":
            hero.move(x, y - 1)
            create_particles([x, y - 1])
            level_map[y - 1][x] = "."
            Tile('empty', x, y - 1)
            count()
        elif y > 0 and level_map[y - 1][x] == "4":
            hero.move(x, y - 1)
            create_particles([x, y - 1])
            level_map[y - 1][x] = "."
            Tile('empty', x, y - 1)
            count()
        elif y > 0 and level_map[y - 1][x] == "5":
            hero.move(x, y - 1)
            create_particles([x, y - 1])
            level_map[y - 1][x] = "."
            Tile('empty', x, y - 1)
            count()
    elif movement == "down":
        if y < max_y - 1 and level_map[y + 1][x] == ".":
            hero.move(x, y + 1)
        elif y < max_y - 1 and level_map[y + 1][x] == "!":
            hero.move(x, y + 1)
            death_screen()
        elif y < max_y - 1 and level_map[y + 1][x] == "1":
            hero.move(x, y + 1)
            create_particles([x, y + 1])
            level_map[y + 1][x] = "."
            Tile('empty', x, y + 1)
            count()
        elif y < max_y - 1 and level_map[y + 1][x] == "2":
            hero.move(x, y + 1)
            create_particles([x, y + 1])
            level_map[y + 1][x] = "."
            Tile('empty', x, y + 1)
            count()
        elif y < max_y - 1 and level_map[y + 1][x] == "3":
            hero.move(x, y + 1)
            create_particles([x, y + 1])
            level_map[y + 1][x] = "."
            Tile('empty', x, y + 1)
            count()
        elif y < max_y - 1 and level_map[y + 1][x] == "4":
            hero.move(x, y + 1)
            create_particles([x, y + 1])
            level_map[y + 1][x] = "."
            Tile('empty', x, y + 1)
            count()
        elif y < max_y - 1 and level_map[y + 1][x] == "5":
            hero.move(x, y + 1)
            create_particles([x, y + 1])
            level_map[y + 1][x] = "."
            Tile('empty', x, y + 1)
            count()
    elif movement == "left":
        if x > 0 and level_map[y][x - 1] == ".":
            hero.move(x - 1, y)
        elif x > 0 and level_map[y][x - 1] == "!":
            hero.move(x - 1, y)
            death_screen()
        elif x > 0 and level_map[y][x - 1] == "1":
            hero.move(x - 1, y)
            create_particles([x - 1, y])
            level_map[y][x - 1] = "."
            Tile('empty', x - 1, y)
            count()
        elif x > 0 and level_map[y][x - 1] == "2":
            hero.move(x - 1, y)
            create_particles([x - 1, y])
            level_map[y][x - 1] = "."
            Tile('empty', x - 1, y)
            count()
        elif x > 0 and level_map[y][x - 1] == "3":
            hero.move(x - 1, y)
            create_particles([x - 1, y])
            level_map[y][x - 1] = "."
            Tile('empty', x - 1, y)
            count()
        elif x > 0 and level_map[y][x - 1] == "4":
            hero.move(x - 1, y)
            create_particles([x - 1, y])
            level_map[y][x - 1] = "."
            Tile('empty', x - 1, y)
            count()
        elif x > 0 and level_map[y][x - 1] == "5":
            hero.move(x - 1, y)
            create_particles([x - 1, y])
            level_map[y][x - 1] = "."
            Tile('empty', x - 1, y)
            count()
    elif movement == "right":
        if x < max_x - 1 and level_map[y][x + 1] == ".":
            hero.move(x + 1, y)
        elif x < max_x - 1 and level_map[y][x + 1] == "!":
            hero.move(x + 1, y)
            death_screen()
        elif x < max_x - 1 and level_map[y][x + 1] == "1":
            hero.move(x + 1, y)
            create_particles([x + 1, y])
            level_map[y][x + 1] = "."
            Tile('empty', x + 1, y)
            count()
        elif x < max_x - 1 and level_map[y][x + 1] == "2":
            hero.move(x + 1, y)
            create_particles([x + 1, y])
            level_map[y][x + 1] = "."
            Tile('empty', x + 1, y)
            count()
        elif x < max_x - 1 and level_map[y][x + 1] == "3":
            hero.move(x + 1, y)
            create_particles([x + 1, y])
            level_map[y][x + 1] = "."
            Tile('empty', x + 1, y)
            count()
        elif x < max_x - 1 and level_map[y][x + 1] == "4":
            hero.move(x + 1, y)
            create_particles([x + 1, y])
            level_map[y][x + 1] = "."
            Tile('empty', x + 1, y)
            count()
        elif x < max_x - 1 and level_map[y][x + 1] == "5":
            hero.move(x + 1, y)
            create_particles([x + 1, y])
            level_map[y][x + 1] = "."
            Tile('empty', x + 1, y)
            count()


def death_screen():
    global count1
    pygame.mixer.music.load('data/ghoul2.mp3')
    pygame.mixer.music.play()
    fon = pygame.transform.scale(load_image('death_screen.png'), screen_size)
    screen.blit(fon, (0, 0))
    font = pygame.font.Font(None, 30)
    text1 = font.render('Принцесс спасено:', True, (0, 255, 0))
    text2 = font.render(str(count1), True, (0, 255, 0))
    textRect1 = text1.get_rect()
    textRect2 = text1.get_rect()
    textRect1.center = (250, 50)
    textRect2.center = (250, 100)
    screen.blit(text1, textRect1)
    screen.blit(text2, textRect2)
    add_to_db()

    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                terminate()
            if event.type == pygame.MOUSEBUTTONDOWN:
                terminate()
        pygame.display.flip()
        clock.tick(FPS)


def win_screen():
    pygame.mixer.music.load('data/ghoul3.mp3')
    pygame.mixer.music.play()
    fon = pygame.transform.scale(load_image('win_screen.png'), screen_size)
    screen.blit(fon, (0, 0))
    font = pygame.font.Font(None, 35)
    text1 = font.render('Принцесс спасено:', True, (0, 0, 0))
    text2 = font.render(str(count1), True, (0, 0, 0))
    textRect1 = text1.get_rect()
    textRect2 = text1.get_rect()
    textRect1.center = (250, 140)
    textRect2.center = (250, 170)
    screen.blit(text1, textRect1)
    screen.blit(text2, textRect2)
    add_to_db()

    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                terminate()
            if event.type == pygame.KEYDOWN or \
                    event.type == pygame.MOUSEBUTTONDOWN:
                terminate()
        pygame.display.flip()
        clock.tick(FPS)

    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                terminate()
            if event.type == pygame.MOUSEBUTTONDOWN:
                terminate()
        pygame.display.flip()
        clock.tick(FPS)


count1 = 0


def count():
    global count1
    count1 += 1
    if count1 == 2:
        win_screen()


def make_db():
    db = sqlite3.connect('plans.db')
    sql = db.cursor()

    sql.execute("""CREATE TABLE IF NOT EXISTS users (
    info TEXT)""")
    db.commit()


def add_to_db():
    db = sqlite3.connect('plans.db')
    sql = db.cursor()
    sql.execute(f"INSERT INTO users VALUES ('{str(count1)}')")
    db.commit()


make_db()
start_screen()
camera = Camera()
level_map = load_level(map_file)
hero, max_x, max_y = generate_level(level_map)
camera.update(hero)
pygame.mixer.music.load('data/ghoul4.mp3')
pygame.mixer.music.play()
while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

        elif event.type == pygame.KEYDOWN:
            if event.key == pygame.K_UP:
                move(hero, "up")
            elif event.key == pygame.K_DOWN:
                move(hero, "down")
            elif event.key == pygame.K_LEFT:
                move(hero, "left")
            elif event.key == pygame.K_RIGHT:
                move(hero, "right")
            elif event.key == pygame.K_f:
                pygame.mixer.music.stop()
            elif event.key == pygame.K_v:
                pygame.mixer.music.load('data/ghoul4.mp3')
                pygame.mixer.music.play()

    screen.fill(pygame.Color("black"))
    sprite_group.draw(screen)
    heroes_group.draw(screen)
    heroes_group.update()
    all_sprites.draw(screen)
    all_sprites.update()
    clock.tick(FPS)
    pygame.display.flip()
pygame.quit()