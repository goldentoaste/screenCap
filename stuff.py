import pygame
from time import sleep

pygame.init()
pygame.display.set_caption("My title")

screen = pygame.display.set_mode((640, 480))

background_color = (255, 255, 255)

i = 0
running = True
while running:
    screen.fill(background_color)

    pygame.draw.rect(screen, (255, 0, 0), pygame.Rect(i, i, 40, 30))
    i += 1

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

    pygame.display.flip()
    sleep(0.1)
