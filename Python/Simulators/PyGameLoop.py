import numpy as np
import pygame
import pygame.gfxdraw
pygame.init()
screen = pygame.display.set_mode((1000, 700))
pygame.display.set_caption("Pygame Loop")
clock = pygame.time.Clock()
framerate = 60
arrow_origin = [500,350]
arrow = np.array([[2,0],[2,150],[7,150],[0,165],[-7,150],[-2,150],[-2,0],[2,0]])
#-----------------------------------------------------------------------
#                               Main Loop
#-----------------------------------------------------------------------
done = False
while not done:
    screen.fill((0,0,0))
    arrow_tup = tuple(map(tuple, tuple((arrow+arrow_origin).astype(int))))
    pygame.gfxdraw.filled_polygon(screen, (arrow_tup), (0,255,255,155))
    pygame.gfxdraw.aapolygon(screen, (arrow_tup), (0,255,255,200))
    pygame.event.get()
    keys = pygame.key.get_pressed()
    if keys[pygame.K_q]:
        done = True
    pygame.display.flip()
    clock.tick(framerate)
pygame.display.quit()
