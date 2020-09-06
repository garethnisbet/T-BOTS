#-----------------------------------------------------------------------
#                     Import Required Libraries
#-----------------------------------------------------------------------
import numpy as np
import pygame
import pygame.gfxdraw
from pygame_widgets import TextBox, Slider
import sys, os
path_above = os.path.abspath(os.path.join(os.path.dirname( __file__ ), '..'))
sys.path.append(path_above)
from TBotTools import geometry
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
origin = [500,200]
arrow = np.array([[1,0],[1,150],[0,152],[-1,150],[-1,0],[1,0]])
arrow = arrow/arrow.max()
scalefactor = 220
#-----------------------------------------------------------------------
#                              Constants
#-----------------------------------------------------------------------
g = 9.81
l = 1
alpha = 0
omega = 0
theta = 0.9*np.pi
dt = 1/framerate
C = 0.999
slider = Slider(screen, 100, 100, 800, 20, min=0.0, max=2*l, step=0.01, initial = l)
output = TextBox(screen, 475, 50, 50, 30, borderColour=(0,0,0),borderThickness=1, radius=3, textColour=(0,0,0), fontSize=20)
#-----------------------------------------------------------------------
#                               Main Loop
#-----------------------------------------------------------------------
done = False
while not done:
    screen.fill((90,90,90))
    #-------------------------------------------------------------------
    #                           Dynamics
    #-------------------------------------------------------------------
    alpha = np.sin(theta)*g/l
    omega += alpha * dt
    omega = omega * C 
    theta += omega * dt
    #-------------------------------------------------------------------
    #                        Transformations
    #------------------------------------------------------------------- 
    arrow1 = (arrow * l * scalefactor)
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
    slider.listen(events)
    slider.draw()
    l = slider.getValue()+0.001 # a value of zero will result in a divide by zero error
    output.setText("{:.2f}m".format(slider.getValue()))
    output.draw()
    pygame.display.flip()
    if keys[pygame.K_s]:
        pygame.image.save(screen, datetime.now().strftime("CapturedImages/%m%d%Y_%H%M%S.png"))
    clock.tick(framerate)
pygame.display.quit()
