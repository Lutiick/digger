import pygame
import sys
import os
import time

FPS = 50
WIDTH, HEIGHT = 500, 400

pygame.init()
screen = pygame.display.set_mode((WIDTH, HEIGHT))
clock = pygame.time.Clock()
GRAVITY = 2
FONT = pygame.font.Font(None, 24)
pygame.mixer.init()
music = pygame.mixer.music.load(os.path.join('data', "music.mp3"))
pygame.mixer.music.play(loops=-1)


def terminate():
    pygame.quit()
    sys.exit()


def load_image(name, colorkey=None):
    fullname = os.path.join('data', name)
    image = pygame.image.load(fullname).convert()
    if colorkey is not None:
        if colorkey == -1:
            colorkey = image.get_at((0, 0))
        image.set_colorkey(colorkey)
    else:
        image = image.convert_alpha()
    return image


def load_level(filename):
    filename = "data/" + filename
    # читаем уровень, убирая символы перевода строки
    with open(filename, 'r') as mapFile:
        level_map = [line.strip() for line in mapFile]

    # и подсчитываем максимальную длину    
    max_width = max(map(len, level_map))

    # дополняем каждую строку пустыми клетками ('.')    
    return list(map(lambda x: x.ljust(max_width, '.'), level_map))

tile_width = tile_height = 32

tile_basis = {
    "ground": load_image("ground.png"),
    "clay": load_image("clay.png")
}

tiles_resourse = {
    '1': {
        "type": "empty",
        "quantity": 0,
        "strength": 1,
        "rarity": 990,
        "price": 0
    },
    '2': {
        "type": "quartz",
        "quantity": 1,
        "strength": 1.2,
        "rarity": 100,
        "price": 50
    },
    '3': {
        "type": "silver",
        "quantity": 1,
        "strength": 1.5,
        "rarity": 30,
        "price": 150
    },
    '4': {
        "type": "gold",
        "quantity": 1,
        "strength": 1.7,
        "rarity": 8,
        "price": 300
    },
    '5': {
        "type": "gem",
        "quantity": 1,
        "strength": 1.5,
        "rarity": 1,
        "price": 600
    },
}

for resourse in tiles_resourse.values():
    resourse["image"] = load_image(f"{resourse['type']}.png", -1)


class Interface:
    def __init__(self, screen, coins=0, oxygen=100):
        self.screen = screen
        self.oxygen = oxygen
        self.coins = coins
        self.coins_image = load_image("coins.png", -1)
    
    def set_coins(self, coins):
        self.coins = coins
    
    def set_oxygen(self, oxygen):
        self.oxygen = oxygen
    
    def draw(self):
        oxygen_sur = pygame.Surface((WIDTH * self.oxygen, 15))
        if self.oxygen > 0.30:
            oxygen_sur.fill(pygame.Color("blue"))
        else:
            oxygen_sur.fill(pygame.Color("red"))
        self.screen.blit(oxygen_sur, (0, 0))

        coins_sur = pygame.Surface((WIDTH, 20), pygame.SRCALPHA, 32)
        coins_sur.blit(self.coins_image, (3, 0))
        txt = FONT.render(str(self.coins), 0, (255, 255, 255))
        coins_sur.blit(txt, (26, 0))
        self.screen.blit(coins_sur, (0, 20))


class Barge(pygame.sprite.Sprite):
    def __init__(self, pos_x, pos_y, screen):
        super().__init__(barge_group, all_sprites)
        self.image = load_image("tanker.png", -1)
        self.rect = self.image.get_rect().move(pos_x, pos_y)
        self.screen = screen
        self.choosed = 1
        self.oxygen_lvl = 1
        self.drill_lvl = 1
        self.standart_price = 1500

    def draw_shop(self, surface):
        surface.fill(pygame.Color("blue"))
        if self.choosed == 1:
            upgrade_oxygen_btn = FONT.render(f"Upgrade oxygen tank: {str(self.standart_price * ((1 + self.oxygen_lvl) / 2))}", 0, (0, 255, 0))
            upgrade_drill_btn = FONT.render(f"Upgrade drill: {str(self.standart_price * ((1 + self.drill_lvl) / 2))}", 0, (255, 255, 255))
        else:
            upgrade_oxygen_btn = FONT.render(f"Upgrade oxygen tank: {str(self.standart_price * ((1 + self.oxygen_lvl) / 2))}", 0, (255, 255, 255))
            upgrade_drill_btn = FONT.render(f"Upgrade drill: {str(self.standart_price * ((1 + self.drill_lvl) / 2))}", 0, (0, 255, 0))
        
        surface.blit(upgrade_oxygen_btn, (5, 70))
        surface.blit(upgrade_drill_btn, (5, 90))
        interface.draw()

    def buy(self):
        if self.choosed == 1:
            if player.coins >= self.standart_price * ((1 + self.oxygen_lvl) // 2):
                player.coins -= self.standart_price * ((1 + self.oxygen_lvl) // 2)
                player.max_oxygen += 2000
                self.oxygen_lvl += 1
        else:
            if player.coins >= self.standart_price * ((1 + self.drill_lvl) // 2):
                player.coins -= self.standart_price * ((1 + self.drill_lvl) // 2)
                player.diging_velocity += 1
                self.drill_lvl += 1
        interface.set_coins(player.coins)

    def run_shop(self):
        surface = pygame.Surface((WIDTH, HEIGHT))
        while True:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    terminate()
                elif event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_ESCAPE:
                        return
                    elif event.key == pygame.K_KP_ENTER:
                        self.buy()
                    elif event.key == pygame.K_UP or event.key == pygame.K_DOWN:
                        if self.choosed == 1:
                            self.choosed = 2
                        else:
                            self.choosed = 1
            self.draw_shop(surface)
            self.screen.blit(surface, (0, 0))
            interface.draw()
            pygame.display.flip()
            clock.tick(FPS)
    
    def move_barge(self, pos_x):
        self.rect.x = pos_x
        

class Tile(pygame.sprite.Sprite):
    def __init__(self, pos_x, pos_y, basis, resourse):
        super().__init__(tiles_group, all_sprites)
        self.image = tile_basis[basis].copy()
        self.image.blit(tiles_resourse[resourse]["image"], (0, 0))
        self.quantity = tiles_resourse[resourse]["quantity"]
        self.strength = tiles_resourse[resourse]["strength"]
        self.rarity = tiles_resourse[resourse]["rarity"]
        self.price = tiles_resourse[resourse]["price"]
        self.rect = pygame.Rect(0, 0, 32, 32).move(tile_width * pos_x, tile_height * pos_y)

class Background(pygame.sprite.Sprite):
    def __init__(self, w, h):
        super().__init__(background_group)
        self.image = pygame.transform.scale(
                                            load_image("splash_gradient.png"),
                                            (w, h)
                                           )
        self.rect = self.image.get_rect()

class Border(pygame.sprite.Sprite):
    def __init__(self, map_width, h, side):
        super().__init__(border_group, all_sprites)
        if side == "right":
            self.rect = pygame.Rect(map_width, 0, 200, h)
            self.image = pygame.Surface((200, h))
            self.image.fill(pygame.Color("black"))
        elif side == "left":
            self.rect = pygame.Rect(-200, 0, 200, h)
            self.image = pygame.Surface((200, h))
            self.image.fill(pygame.Color("black"))
        elif side == "bottom":
            self.rect = pygame.Rect(0, h, map_width, 200)
            self.image = pygame.Surface((map_width, 200))
            self.image.fill(pygame.Color("black"))
        self.side = side

class Player(pygame.sprite.Sprite):
    def __init__(self, pos_x, pos_y):
        super().__init__(player_group, all_sprites)
        right_image = load_image('subright.png', -1)
        left_image = load_image('subleft.png', -1)

        self.rect = right_image.get_rect().move(tile_width * pos_x + 15, tile_height * pos_y + 5)
        self.blade = load_image("blade.png", -1)

        self.images = {
            "right": [],
            "left": []
        }
        for side in ("right", "left"):
            for i in range(4):
                if side == "left":
                    image = pygame.Surface((46, 32), pygame.SRCALPHA, 32)
                    image.blit(pygame.transform.rotate(self.blade, -90 * i), (0, 0))
                    image.blit(left_image, (6, 0))
                else:
                    image = pygame.Surface((46, 32), pygame.SRCALPHA, 32)
                    image.blit(pygame.transform.rotate(self.blade, -90 * i), (8, 0))
                    image.blit(right_image, (0, 0))       
                
                self.images[side].append(image)

        self.image_counter = 0
        self.image = 0
        self.image_side = "right"

        self.diging = 0
        self.diging_side = None
        self.diging_tile = None
        self.vel_x = 0
        self.vel_y = 0

        self.velocity = 2
        self.diging_velocity = 2
        self.gravity = GRAVITY
        self.oxygen = 4000
        self.max_oxygen = 4000

        self.coins = 0
    
    def _collide_borders(self):
        colliding = pygame.sprite.spritecollide(self, border_group, False)
        return list(map(lambda x: (x, x.side), colliding))

    def draw(self, screen):
        self.image_counter += 1
        if self.diging and (self.image_counter) % 4 == 0:
            self.image = (self.image + 1) % 4
            
        if self.image_side == "right":
            x = self.rect.x - 2
        else:
            x = self.rect.x - 4
        screen.blit(self.images[self.image_side][self.image], (x, self.rect.y))


    def action(self, keys):
        if self.oxygen <= 0:
            terminate()
        if self.diging:
            self.dig()
            self.oxygen -= 2
        else:
            self.move(keys)
            self.oxygen -= 1
    
    def move(self, keys):
        on_ground = False
        if keys[pygame.K_LEFT]:
            self.image_side = "left"
            self.vel_x = -self.velocity
        if keys[pygame.K_RIGHT]:
            self.image_side = "right"
            self.vel_x = self.velocity
        if keys[pygame.K_DOWN]:
            self.vel_y += self.velocity
        if keys[pygame.K_UP]:
            self.vel_y += -self.velocity
        if not keys[pygame.K_UP]:
            self.vel_y += self.gravity

        self.rect.y += self.vel_y
        colliding = pygame.sprite.spritecollide(self, tiles_group, False)
        if colliding:
            if self.vel_y > 0:
                self.rect.bottom = colliding[0].rect.top
            else:
                self.rect.top = colliding[0].rect.bottom

            if abs(colliding[0].rect.x - self.rect.x) <= tile_width // 2:
                col = colliding[0]
            elif len(colliding) > 1:
                col = colliding[1]
            else:
                col = None

            if col is not None:
                if keys[pygame.K_DOWN]:
                    self.rect.y -= self.vel_y
                    self.dig(col, "bottom")
                    return
                else:
                    on_ground = True   

        self.rect.x += self.vel_x
        colliding = pygame.sprite.spritecollide(self, tiles_group, False)
        if colliding:
            if self.vel_x > 0:
                self.rect.right = colliding[0].rect.left
            else:
                self.rect.left = colliding[0].rect.right
            if on_ground:
                if keys[pygame.K_RIGHT]:
                    self.dig(colliding[0], side="right")
                elif keys[pygame.K_LEFT]:
                    self.dig(colliding[0], side="left")

        for background in background_group:
            if background.rect.top -self.rect.top >= 15:
                self.rect.top += self.velocity
                self.oxygen = self.max_oxygen
        
        for coll, side in self._collide_borders():
            if side == "bottom":
                self.rect.bottom = coll.rect.top
            elif side == "right":
                self.rect.right = coll.rect.left
            elif side == "left":
                self.rect.left = coll.rect.right
        
        barge = pygame.sprite.spritecollide(self, barge_group, False)
        for b in barge:
            self.oxygen = self.max_oxygen
            b.run_shop()
        self.vel_y = 0
        self.vel_x = 0
        
    
    def dig(self, tile=None, side=None):
        if tile is not None:
            self.diging_tile = tile
        if side is not None:
            self.diging_side = side

        if self.diging >= 100:
            self.diging = 0
            self.diging_side = None
            self.coins += self.diging_tile.price
            self.diging_tile.kill()
            return

        if self.diging_side == "left":
            self.rect.left = self.diging_tile.rect.right - round(self.diging * tile_width / 100)
        elif self.diging_side == "right":
            self.rect.right = self.diging_tile.rect.left + round(self.diging * tile_width / 100)
        elif self.diging_side == "bottom":
            self.rect.bottom = self.diging_tile.rect.top + round(self.diging * tile_width / 100)

            if self.rect.left < self.diging_tile.rect.left:
                self.rect.left += 1
            elif self.rect.left > self.diging_tile.rect.left:
                self.rect.left -= 1


        self.diging += self.diging_velocity / self.diging_tile.strength
        

def start_screen():
    fon = pygame.transform.scale(load_image('gamestart.png'), (WIDTH, HEIGHT))
    screen.blit(fon, (0, 0))

    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                terminate()
            elif event.type == pygame.KEYDOWN or event.type == pygame.MOUSEBUTTONDOWN:
                return  # начинаем игру
        pygame.display.flip()
        clock.tick(FPS)


class Camera:
    # зададим начальный сдвиг камеры
    def __init__(self, start_depth=0):
        self.dx = 0
        self.dy = 0
        self.depth = start_depth
        
    # сдвинуть объект obj на смещение камеры
    def apply(self, obj):
        obj.rect.x += self.dx
        obj.rect.y += self.dy
    
    # позиционировать камеру на объекте target
    def update(self, target):
        self.dx = -(target.rect.x + target.rect.w // 2 - WIDTH // 2)
        self.dy = -(target.rect.y + target.rect.h // 2 - HEIGHT // 2)
        self.depth -= self.dy


player = None

# группы спрайтов
all_sprites = pygame.sprite.Group()
tiles_group = pygame.sprite.Group()
player_group = pygame.sprite.Group()


def random_resourse():
    from random import randrange
    for key, values in list(tiles_resourse.items())[::-1]:
        rand = randrange(1000)
        if rand < values["rarity"]:
            return key
    return "-"

def generate_level_txt(width, height):
    res = [["-"] * width for _ in range(5)]
    res = [ *res, *[[random_resourse() for i in range(width)] for _ in range(height)] ]
    res[0][width // 2] = "@"
    return res
            

def generate_level(level):
    new_player, x, y = None, None, None
    level_blocks_height = len(level)
    level_blocks_width = len(level[0])
    for y in range(len(level)):
        for x in range(len(level[y])):
            if level[y][x] in tiles_resourse:
                if y < 50:
                    Tile(x, y, 'ground', level[y][x])
                else:
                    Tile(x, y, 'clay', level[y][x])
            elif level[y][x] == '@':
                new_player = Player(x, y)
    return new_player, level_blocks_width, level_blocks_height


start_screen()

lvl = generate_level_txt(50, 100)
player, level_blocks_width, level_blocks_height = generate_level(lvl)

barge_group = pygame.sprite.Group()
barge = Barge(level_blocks_width * tile_width // 2, -tile_height, screen)

background_group = pygame.sprite.Group()
Background(level_blocks_width * tile_width, level_blocks_height * tile_height)

border_group = pygame.sprite.Group()
for side in ("right", "left", "bottom"):
    Border(level_blocks_width * tile_width, level_blocks_height * tile_height, side)
interface = Interface(screen)
camera = Camera(start_depth=(HEIGHT- player.rect.height) // 2)
running = True

while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

    keys = pygame.key.get_pressed()
    player.action(keys)
    interface.set_oxygen(player.oxygen / player.max_oxygen)
    interface.set_coins(player.coins)
    camera.update(player)
    if camera.depth > HEIGHT / 2:
        barge.move_barge(player.rect.x)

    for sprite in all_sprites:
        camera.apply(sprite)
    
    for background in background_group:
        camera.apply(background)
        
    screen.fill((213, 229, 251))
    all_sprites.update()
    
    background_group.draw(screen)
    tiles_group.draw(screen)
    player.draw(screen)
    barge_group.draw(screen)
    border_group.draw(screen)
    interface.draw()
    
    pygame.display.flip()
    clock.tick(FPS)


pygame.quit()