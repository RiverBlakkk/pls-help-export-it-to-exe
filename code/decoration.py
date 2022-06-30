import pygame
from settings import SCREEN_HEIGHT, SCREEN_WIDTH
from player import Player
pygame.init()

clock = pygame.time.Clock()
fps = 60

SCREEN = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption('paralax')

bg_images = []
for i in range(1, 3):
    bg_image = pygame.image.load(f'../graphics/paralax/paralax{i}.png').convert_alpha()
    bg_images.append(bg_image)
bg_width = bg_images[0].get_width()

def draw_bg():
    for x in range(2):
        speed = 1
        for i in bg_images:
            SCREEN.blit(i, ((x * bg_width) - scroll_x * speed, 0))
            speed += 0.2




run = True
while run:

    and scroll_x < 1000:
    scroll_x += 5

    clock.tick(fps)

    #draw world
    draw_bg()

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            run = False

    pygame.display.update()