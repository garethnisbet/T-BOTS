import sys, os
path_above = os.path.abspath(os.path.join(os.path.dirname( __file__ ), '..'))
sys.path.append(path_above)
from TBotTools import geometry
import numpy as np
import pygame
import pygame.gfxdraw
geom = geometry.geometry()
pygame.init()
screen = pygame.display.set_mode((1000, 700))
pygame.display.set_caption("T-Bot Simulator")
clock = pygame.time.Clock()
framerate = 60
framecount = 1
arrow_origin = [500,350]
arrow = np.array([[2,0],[2,150],[7,150],[0,165],[-7,150],[-2,150],[-2,0],[2,0]])
#-----------------------------------------------------------------------
#                              Constants
#-----------------------------------------------------------------------
g = 9.81
l = 1.08
alpha = 0
omega = 0
theta = 0.01
dt = 1/framerate
C = 0.999
#-----------------------------------------------------------------------
#                               Main Loop
#-----------------------------------------------------------------------
done = False
while not done:
    screen.fill((0,0,0))
    #-------------------------------------------------------------------
    #                            Physics
    #-------------------------------------------------------------------
    alpha = np.sin(theta)*g/l
    omega += alpha * dt
    omega = omega * C 
    theta += omega * dt
    #-------------------------------------------------------------------
    arrow_rot = np.array(geom.rotxy(theta+np.pi,arrow))
    arrow_tup = tuple(map(tuple, tuple((arrow_rot+arrow_origin).astype(int))))
    pygame.gfxdraw.filled_polygon(screen, (arrow_tup), (0,255,255,155))
    pygame.gfxdraw.aapolygon(screen, (arrow_tup), (0,255,255,200))
    pygame.event.get()
    keys = pygame.key.get_pressed()
    if keys[pygame.K_q]:
        done = True
    if keys[pygame.K_s]:
        alpha = 0
        omega = 0
        theta = 0.01
    pygame.display.flip()
    clock.tick(framerate)
    #if framecount < 500:    
    #    pygame.image.save(screen, "CapturedImages/{:04d}.png".format(framecount))
    framecount += 1
pygame.display.quit()
