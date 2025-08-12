import os
import random
import math
import pygame
from os import listdir
from os.path import isfile, join
from pygame import  mixer
mixer.init()
# from pkg_resources import non_empty_lines
# from pygame.examples.sprite_texture import sprite

# from pygame.examples.go_over_there import running

pygame.init()

pygame.display.set_caption("Platformer")
mixer.music.load('assets/Super Mario Bros. medley.mp3')
mixer.music.play(-1)
WIDTH, HEIGHT = 1000, 700

FPS = 60
PLAYER_VEL = 5

window = pygame.display.set_mode((WIDTH, HEIGHT))
my_image2 = pygame.image.load("assets/Items/Checkpoints/End/End(Idle).png").convert_alpha()


def get_background(name):
    # load background image
    image = pygame.image.load(join(".", name))  # "." means current folder
    _, _, width, height = image.get_rect()  # i dont care about x,y
    tiles = []
    for i in range(WIDTH // width + 1):  # +1 ensures  image fully covers the screen even if it is not multiple
        for j in range(HEIGHT // height + 1):
            pos = (i * width, j * height)  # tuple :A fixed collection of items,Written with (),cannot be changed
            tiles.append(pos)
    return tiles, image

SCORE_FONT = pygame.font.SysFont("Arial", 32)
def draw(window, background, bg_image, player, objects, offset_x,score,my_image):

    for tile in background:
        window.blit(bg_image, tile)

    for obj in objects:
        obj.draw(window, offset_x)
    player.draw(window, offset_x)
    #my_image = pygame.image.load(".venv/End(Idle).png").convert_alpha()
    window.blit(my_image, (1400-offset_x,HEIGHT-155))
    score_surface = SCORE_FONT.render(f"Score: {score}", True, (255, 255, 255))
    window.blit(score_surface, (100, 5))

    pygame.display.update()


def handle_vertical_collision(player, objects, dy):
    collided_objects = []
    for obj in objects:
        if pygame.sprite.collide_mask(player, obj):
            if dy > 0:  # falling down
                player.rect.bottom = obj.rect.top
                player.landed()
            elif dy < 0:  # player jumbed up and  hit the underside of something.
                player.rect.top = obj.rect.bottom
                player.hit_head()
            collided_objects.append(obj)
    return collided_objects


def collide(player, objects, dx):
    player.move(dx, 0)
    player.update()
    collide_object = None
    for obj in objects:
        if pygame.sprite.collide_mask(player, obj):
            collide_object = obj
            break
    player.move(-dx, 0)
    player.update()
    return collide_object


def handle_move(player, objects):
    keys = pygame.key.get_pressed()
    player.x_vel = 0  # if we don’t, your player would keep moving even if no key is pressed.
    collide_left = collide(player, objects, -PLAYER_VEL * 2)
    collide_right = collide(player, objects, PLAYER_VEL * 2)
    if keys[pygame.K_LEFT] and not collide_left:
        player.move_left(PLAYER_VEL)
    if keys[pygame.K_RIGHT] and not collide_right:
        player.move_right(PLAYER_VEL)


    vertical_collide = handle_vertical_collision(player, objects, player.y_vel)
    to_check = [collide_left, collide_right, *vertical_collide]
    hit_fire = False
    for obj in to_check:
        if obj and obj.name == "Fire":
            player.make_hit()
            hit_fire = True
    return hit_fire


def flip(sprites):  # Returns a horizontally flipped version of every sprite image in the list.
    return [pygame.transform.flip(sprite, True, False) for sprite in sprites]


# Store them neatly by name like: all_sprites["run"] = [frame1, frame2, frame3], all_sprites["idle"] = [frame1, frame2] so on
def load_sprite_sheets(dir1, dir2, width, height, direction: False):
    # direction controls hether to generate flipped versions of the spirites
    path = join("assets", dir1, dir2)
    images = [f for f in listdir(path) if
              isfile(join(path, f))]  # this line creates a list of all sprite image files inside the folder
    all_sprites = {}
    for image in images:
        # load image file
        sprite_sheet = pygame.image.load(join(path, image)).convert_alpha()
        sprites = []
        # to slice 1: rect to define what to extract 2: new surface to put it on 3: blit to do the copying
        for i in range(
                sprite_sheet.get_width() // width):  # This loop cuts the sprite sheet horizontally into smaller pieces
            # sprite_sheet.get_width()//width= tells you how many frames are in your sprite sheet horizontally.
            surface = pygame.Surface((width, height), pygame.SRCALPHA,
                                     32)  # creates a blank transparent surface same size as each frame
            rect = pygame.Rect(i * width, 0, width,
                               height)  # defines a rectangle area from the sprite sheet to copy , i*width shifts x position to get each frame
            surface.blit(sprite_sheet, (0, 0),
                         rect)  # cuts out the rect part from sprite_sheet,pastes it into your blank surface at 0,0
            # surface now holds one frame
            sprites.append(pygame.transform.scale2x(surface))

        if direction:
            all_sprites[image.replace(".png", "" + "_right")] = sprites
            all_sprites[image.replace(".png", "" + "_left")] = flip(sprites)
        else:
            all_sprites[image.replace(".png", "")] = sprites
    return all_sprites


def get_block(size):
    path = join("assets", "Terrain", "Terrain.png")
    image = pygame.image.load(path).convert_alpha()
    surface = pygame.Surface((size, size), pygame.SRCALPHA, 32)
    rect = pygame.Rect(96, 0, size, size)
    surface.blit(image, (0, 0), rect)
    return pygame.transform.scale2x(surface)


def get_smaller_block(size):
    path = join("assets", "Terrain", "Terrain.png")
    image = pygame.image.load(path).convert_alpha()
    surface = pygame.Surface((16, 15), pygame.SRCALPHA, 32)
    rect = pygame.Rect(152, 16, 16, 15)
    surface.blit(image, (0, 0), rect)
    return pygame.transform.scale2x(surface)


class Object(pygame.sprite.Sprite):
    def __init__(self, x, y, width, height, name: None):
        super().__init__()
        self.rect = pygame.Rect(x, y, width, height)
        self.image = pygame.Surface((width, height), pygame.SRCALPHA)
        self.width = width
        self.height = height
        self.name = name

    def draw(self, window, offset_x):
        window.blit(self.image, (self.rect.x - offset_x, self.rect.y))


class Block(Object):
    def __init__(self, x, y, size):
        super().__init__(x, y, size, size, name="block")
        block = get_block(size)
        self.image.blit(block, (0, 0))
        self.mask = pygame.mask.from_surface(self.image)


class smaller_block(Object):
    def __init__(self, x, y, size):
        super().__init__(x, y, size, size, name="smallerBlock")
        block = get_smaller_block(size)
        self.image.blit(block, (0, 0))
        self.mask = pygame.mask.from_surface(self.image)


# creating the player object
class Player(
    pygame.sprite.Sprite):  # A sprite group is like a list that stores multiple sprites (e.g. player, enemies, bullets)
    # — but with special powers. It helps you manage, update, and draw multiple sprites at once.
    COLOR = (255, 0, 0)
    GRAVITY = 1
    SPRITES = load_sprite_sheets("MainCharacters", "MaskDude", 32, 32, True)
    Animation_delay = 5

    def __init__(self, x, y, width, height):
        super().__init__()
        self.rect = pygame.Rect(x, y, width, height)
        self.x_vel = 0
        self.y_vel = 0  # how fast we are moving our player in both direction
        self.mask = None
        self.direction = "left"
        self.animation_count = 0  # to change animation frames
        self.fall_count = 0  # counter that increases every frame the player is falling.
        self.jump_count = 0
        self.hit = False
        self.hit_count = 0

    def make_hit(self):
        self.hit = True


    def jump(self):
        self.y_vel = -self.GRAVITY * 8
        self.jump_count += 1
        if self.jump_count == 1:
            self.fall_count = 0

    def move(self, dx, dy):
        self.rect.x += dx

        self.rect.y += dy

    def move_left(self, vel):
        self.x_vel = -vel
        if self.direction != "left":
            self.direction = "left"
            self.animation_count = 0

    def move_right(self, vel):
        self.x_vel = vel
        if self.direction != "right":
            self.direction = "right"
            self.animation_count = 0

    def landed(self):
        self.fall_count = 0
        self.y_vel = 0
        self.jump_count = 0

    def hit_head(self):
        self.count = 0
        self.y_vel *= -1

    def update_sprite(self):
        sprite_sheet = "idle"
        if self.hit:
            sprite_sheet = "hit"
        elif self.y_vel < 0:
            if self.jump_count == 1:
                sprite_sheet = "jump"
            elif self.jump_count == 2:
                sprite_sheet = "double_jump"
        elif self.y_vel > self.GRAVITY * 2:
            sprite_sheet = "fall"
        elif self.x_vel != 0:
            sprite_sheet = "run"
        sprite_sheet_name = sprite_sheet + "_" + self.direction
        sprites = self.SPRITES[sprite_sheet_name]
        sprite_index = (self.animation_count // self.Animation_delay) % len(sprites)  # %len keeps animation in loop
        self.sprite = sprites[sprite_index]
        self.animation_count += 1
        self.update()

    # before collision we need to introduce something called mask
    # mask :will only care about non transparent pixels so we can detect real collisions more precisely
    def update(self):
        # self.rect = self.sprite.get_rect(topleft=(self.rect.x, self.rect.y))
        # self.mask = pygame.mask.from_surface(self.sprite)
        x, y = self.rect.topleft
        self.rect.size = self.sprite.get_size()
        self.rect.topleft = (x, y)
        self.mask = pygame.mask.from_surface(self.sprite)

    def loop(self, fps):
        self.y_vel += min(1, (
                self.fall_count / fps * self.GRAVITY))  # (self.fall_count / fps * self.GRAVITY) how many seconds the player is falling
        self.move(self.x_vel, self.y_vel)
        if self.hit:
            self.hit_count += 1
        if self.hit_count > fps * 2:
            self.hit = False
            self.hit_count = 0
        self.fall_count += 1
        self.update_sprite()

    def draw(self, window, offset_x):
        window.blit(self.sprite, (self.rect.x - offset_x, self.rect.y))


import pygame.sprite


class Fire(Object):

    def __init__(self, x, y, width, height):
        super().__init__(x, y, width, height, "Fire")
        self.fire = load_sprite_sheets("Traps", "Fire", width, height, False)
        self.image = self.fire["off"][0]
        self.mask = pygame.mask.from_surface(self.image)
        self.animation_count = 0
        self.animation_name = "off"

    def on(self):
        self.animation_name = "on"

    def off(self):
        self.animation_name = "off"

    def loop(self):
        sprites = self.fire[self.animation_name]
        sprite_index = (self.animation_count // 3) % len(sprites)  # %len keeps animation in loop
        self.image = sprites[sprite_index]
        self.animation_count += 1
        self.rect = self.image.get_rect(topleft=(self.rect.x, self.rect.y))
        self.mask = pygame.mask.from_surface(self.image)
        if self.animation_count // 3 > len(sprites):
            self.animation_count = 0


class Apple(Object):
    SPRITES = load_sprite_sheets("Items", "Fruits", 32, 32, False)
    Animation_delay = 5

    def __init__(self, x, y):
        super().__init__(x, y, 20, 20, "apple")
        # self.rect = pygame.Rect(x, y, 32, 32)
        # self.mask = None
        # dummy_surface = pygame.Surface((32, 32), pygame.SRCALPHA)
        # self.mask = pygame.mask.from_surface(dummy_surface)
        self.sprite = self.SPRITES["Apple"][0]
        self.rect = self.sprite.get_rect(topleft=(x, y))
        self.mask = pygame.mask.from_surface(self.sprite)
        self.animation_count = 0
        self.sprite = self.SPRITES["Apple"][0]  # start with first frame

    def update(self):
        sprites = self.SPRITES["Apple"]
        sprite_index = (self.animation_count // self.Animation_delay) % len(sprites)
        self.sprite = sprites[sprite_index]
        self.animation_count += 1
        self.rect = self.sprite.get_rect(topleft=(self.rect.x, self.rect.y))
        self.mask = pygame.mask.from_surface(self.sprite)

    def draw(self, window, offset_x):
        window.blit(self.sprite, (self.rect.x - offset_x, self.rect.y))


def main(window):

    clock = pygame.time.Clock()  # make sure game run at a consistent speed
    background, bg_image = get_background("brown.png")
    pygame.display.set_caption("score:")
    block_size = 96
    player = Player(100, 100, 50, 50)
    floor = [Block(i * block_size, HEIGHT - block_size, block_size) for i in range(0, (WIDTH * 2) // block_size)]
    offset_x = 0
    scroll_area_width = 200

    apple = [Apple(300, HEIGHT - block_size * 3 - 50),
             Apple(340, HEIGHT - block_size * 3 - 50), Apple(380, HEIGHT - block_size * 3 - 50),
             Apple(420, HEIGHT - block_size * 3 - 50)
        , Apple(900, HEIGHT - block_size * 4 - 50),
             Apple(1100, HEIGHT - block_size * 4 - 50),
             Apple(1000, HEIGHT - block_size * 5 - 50),
             Apple(500, HEIGHT - block_size - 50),
             Apple(550, HEIGHT - block_size - 100),
             Apple(600, HEIGHT - block_size - 150),
             Apple(650, HEIGHT - block_size - 100),
             Apple(700, HEIGHT - block_size - 50)
             ]

    level_map = [Block(0, HEIGHT - block_size * 2, block_size), Block(0, HEIGHT - block_size * 2 - 96, block_size),
                 Block(0, HEIGHT - block_size * 3 - 96, block_size), Block(0, HEIGHT - block_size * 4 - 96, block_size),
                 Block(0, HEIGHT - block_size * 5 - 96, block_size), Block(0, HEIGHT - block_size * 6 - 96, block_size)
        , Block(600, 300, block_size)]
    levels = [smaller_block(300, HEIGHT - block_size * 3, block_size),
              smaller_block(331, HEIGHT - block_size * 3, block_size),
              smaller_block(362, HEIGHT - block_size * 3, block_size)
        , smaller_block(393, HEIGHT - block_size * 3, block_size),
              smaller_block(424, HEIGHT - block_size * 3, block_size),
              smaller_block(455, HEIGHT - block_size * 3, block_size)
        , smaller_block(900, HEIGHT - block_size * 4, block_size)
        , smaller_block(931, HEIGHT - block_size * 4, block_size)
        , smaller_block(1013, HEIGHT - block_size * 5, block_size),
              smaller_block(1100, HEIGHT - block_size * 4, block_size),
              smaller_block(1131, HEIGHT - block_size * 4, block_size)]
    score = 0
    fire = Fire(611, HEIGHT - block_size - 62, 16, 32)
    fire.on()
    objects = [*floor, *level_map, *levels, *apple, fire]
    run = True
    Finished = False
    while run and not Finished:
        clock.tick(FPS)


        if player.rect.x >= 1400:
            Finished = True
        for app in apple:
            app.update()
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                run = False
                break
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_SPACE and player.jump_count < 2:
                    player.jump()
        player.loop(FPS)
        fire.loop()

        if handle_move(player, objects):
            score-=1
            score=max(0,score)
        pickup_area = player.rect.inflate(-100, 10)  # make rectangle taller by 10px
        for app in apple[:]:
            if pickup_area.colliderect(app.rect):
                apple.remove(app)
                objects.remove(app)
                score += 1

        draw(window, background, bg_image, player, objects, offset_x,score,my_image2)



        if (player.rect.right - offset_x >= WIDTH - scroll_area_width and player.x_vel > 0) or (
                player.rect.left - offset_x <= scroll_area_width
                and player.x_vel < 0):
            offset_x += player.x_vel

    pygame.quit()  # Properly shuts down Pygame components
    quit()  # Fully exits the Python program


if __name__ == "__main__":
    main(window)
