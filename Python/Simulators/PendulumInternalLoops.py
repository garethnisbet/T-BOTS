#-----------------------------------------------------------------------
#                     Import Required Libraries
#-----------------------------------------------------------------------
import numpy as np
import pygame
import pygame.gfxdraw
import sys, os
path_above = os.path.abspath(os.path.join(os.path.dirname( __file__ ), '..'))
sys.path.append(path_above)
from TBotTools import geometry, pgt
from datetime import datetime
#-----------------------------------------------------------------------
#               Setup display and objects for drawing
#-----------------------------------------------------------------------
geom = geometry.geometry()
pygame.init()
screen = pygame.display.set_mode((1000, 700))
pygame.display.set_caption("Pendulum")
clock = pygame.time.Clock()
framerate = 30
origin = [500,180]
arrow = np.array([[1,0],[1,150],[0,152],[-1,150],[-1,0],[1,0]]).astype(float)
arrow = arrow/arrow.max()
scalefactor = 240
sbar = pgt.SliderBar(screen, (100,100), 1, 800, 2.00, 10, (170,170,170),(10,10,10),20)
textPrint = pgt.TextPrint((255,255,255))
textPrint.setfontsize(30)
#-----------------------------------------------------------------------
#                              Constants
#-----------------------------------------------------------------------
g = 9.81
l = 1
alpha = 0
omega = 0
theta = 0.9*np.pi
dt = 1.0/framerate
C = 1
internal_loops  = 10
dt = dt / internal_loops

#-----------------------------------------------------------------------
#                               Main Loop
#-----------------------------------------------------------------------
record = 0
framecount = 1
done = False
while not done:
    screen.fill((90,90,90))
    textPrint.abspos(screen, "{:.2f}m".format(l),(475,50))
    #-------------------------------------------------------------------
    #                           Dynamics
    #-------------------------------------------------------------------
    for ii in list(range(internal_loops)):
        alpha = np.sin(theta)*g/l
        omega += alpha * dt
        omega = omega * C 
        theta += omega * dt
    #-------------------------------------------------------------------
    #                        Transformations
    #------------------------------------------------------------------- 
    arrow1 = np.array([arrow[:,0]*scalefactor/2,(arrow[:,1] * l * scalefactor)]).T
    arrow_rot = np.array(geom.rotxy(theta+np.pi,arrow1))
    #-------------------------------------------------------------------
    #                           Drawing 
    #------------------------------------------------------------------- 
    arrow_tup = tuple(map(tuple, tuple((arrow_rot+origin).astype(int))))
    pygame.gfxdraw.filled_polygon(screen, (arrow_tup), (255,255,255,155))
    pygame.gfxdraw.aapolygon(screen, (arrow_tup), (255,255,255,250))
    pygame.gfxdraw.aapolygon(screen, (arrow_tup), (255,255,255,250))
    pygame.gfxdraw.aacircle(screen, origin[0], origin[1], 5, (255,0,0))
    pygame.gfxdraw.filled_circle(screen, origin[0], origin[1], 5, (255,0,0))
    pygame.gfxdraw.filled_circle(screen, arrow_tup[2][0], arrow_tup[2][1], 15, (0,255,255,250))
    pygame.gfxdraw.aacircle(screen, arrow_tup[2][0], arrow_tup[2][1], 15, (0,255,255,250))
    #-------------------------------------------------------------------
    #                 Keyboard and Mouse Interactions
    #------------------------------------------------------------------- 
    events = pygame.event.get()
    keys = pygame.key.get_pressed()
    c1, c2, c3 =  pygame.mouse.get_pressed()
    mx,my = pygame.mouse.get_pos()
    if c3:
        theta = -np.arctan2(mx-origin[0],my-origin[1])+np.pi
        omega = 0
    if c2:
        origin = [mx,my]
        omega = 0
    if keys[pygame.K_q]:
        done = True
    l = sbar.get_mouse_and_set()+0.001
    pygame.display.flip()
    if keys[pygame.K_s]:
        pygame.image.save(screen, datetime.now().strftime("CapturedImages/%m%d%Y_%H%M%S.png"))
    if keys[pygame.K_1]:
        record = 1
    if keys[pygame.K_2]:
        record = 0
        framecount = 1
    if record == 1:
        pygame.image.save(screen, "CapturedImages/{:04d}.png".format(framecount))
        framecount += 1
    clock.tick(framerate)
pygame.display.quit()
