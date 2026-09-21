import pygame
pygame.init()
screen = pygame.display.set_mode((0, 0), pygame.FULLSCREEN)
running = True
while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT: running = False
        if event.type == pygame.KEYDOWN: running = False
    screen.fill((0, 0, 0))
    pygame.display.flip()
pygame.quit()

