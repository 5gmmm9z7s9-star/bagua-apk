import pygame
from pygame.locals import *

pygame.init()
info = pygame.display.Info()
WIDTH, HEIGHT = info.current_w, info.current_h
screen = pygame.display.set_mode((WIDTH, HEIGHT), FULLSCREEN)
pygame.display.set_caption("Bagua")

# 你的八卦罗盘绘制函数放这里
def draw_bagua(surface):
    surface.fill((0, 0, 0))
    # TODO: 画圆、卦象、双指逻辑

running = True
while running:
    draw_bagua(screen)
    for event in pygame.event.get():
        if event.type == QUIT or (event.type == KEYDOWN and event.key == K_BACKSPACE):
            running = False
        # 安卓单指/双指触屏事件
        if event.type == MOUSEBUTTONDOWN:
            print("Touch pos:", event.pos)
    pygame.display.flip()

pygame.quit()
