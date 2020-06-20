#!/usr/bin/python
import sys, os
import numpy as np
sys.path.append('/home/gareth/GitHub/T-BOTS/Python')
from TBotTools import pid, geometry, pgt
from time import time
import pygame
import pygame.gfxdraw
import pygame.locals as pgl
from collections import deque
from datetime import datetime
clock = pygame.time.Clock()
dirpath = os.path.dirname(os.path.realpath(__file__))+'/Images'

framerate = 60 # set to 30 for Rasoberry pi
dt = 1.0/framerate 

#-----------------------------------------------------------------------
#                           Physical constants
#-----------------------------------------------------------------------
sf = 1.0
acc_g = 9.81 
l = 0.08 # distance between the centre of gravity of the T-Bot and the axil
R = 0.024 # Radius of wheels
C = 1.0 # Friction
h=l+R # Maximum distance between the centre of gravity and the ground 
#h = 828 # Tallest building
#h = 1.8 
#h = 6

t = 0
alpha = 0
gamma = 0
acc = 0
omega = 0
velocity = 0
distance = 0
theta = np.pi*1.01

height_of_man = 0.1

#T-Bot height in pixels is 216 - Actual height 120 mm = h * 1.5
#stick_man height 342 px - Actual height 2000 mm

scaled = height_of_man/(1.75*h)*342./216.
draw_stick_man = 1

#-----------------------------------------------------------------------
#                          Drawing Geometry
#-----------------------------------------------------------------------

geom = geometry.geometry()

origin = [500,319]
tbot_drawing_offset = [-78,-10]
tbot = np.loadtxt('T-BotSideView.dat')
tbot = np.vstack((tbot,tbot[0,:]))+tbot_drawing_offset # closes the shape and adds an offset

tbot_rot = np.array(geom.rotxy(theta,tbot))   
tbot_tup = tuple(map(tuple, tuple((tbot_rot+origin).astype(int))))





spokes = np.array([[0,1],[0,0],[ 0.8660254, -0.5],[0,0],
                    [-0.8660254, -0.5 ],[0,0]])*45



trackmarksArray = np.array([[0,368],[1000,368]])
track_marks_tup = tuple(map(tuple, tuple((trackmarksArray).astype(int))))

stick_man_data = np.loadtxt('Man.dat')
stick_man = np.vstack((stick_man_data,stick_man_data[0,:]))+tbot_drawing_offset # closes the shape and adds an offset
scaled_stick_man = stick_man*scaled
stick_man=scaled_stick_man-[scaled_stick_man[:,0].min(),scaled_stick_man[:,1].min()]
stick_man_h_centre = (stick_man[:,0].min()+stick_man[:,0].max())/2
stick_man = tuple(map(tuple, tuple((stick_man+[750-stick_man_h_centre,368-stick_man[:,1].max()]).astype(int))))

#-----------------------------------------------------------------------
#                         Initialise Pygame
#-----------------------------------------------------------------------

pygame.init()

# Set the width and height of the screen (width, height).
screen = pygame.display.set_mode((1000, 700))
pygame.display.set_caption("T-Bot Simulator")
# Used to manage how fast the screen updates.
clock = pygame.time.Clock()

#-----------------------------------------------------------------------
#                           Load Images
#-----------------------------------------------------------------------

bg = pygame.image.load(dirpath+'/Simple/Gray.jpg').convert() 
track_image = pygame.image.load(dirpath+'/Simple/line.png')
#
#-----------------------------------------------------------------------


done = False

# -------- Main Program Loop -----------

while not done:
    
    screen.blit(bg,(0,0))
    screen.blit(track_image, (0,360))
    
    #-------------------------------------------------------------------
    #                            The Physics
    #-------------------------------------------------------------------

    g = acc_g * sf

    alpha =  -np.sin(theta)*g/h 

    h_acc = (alpha * R)+acc # Accounts for horizontal acceleration
                            # produced from the rotation of the 
                            # wheels as the T-Bot falls. The gearbox
                            # prevents free rotation of the wheels.

    gamma =  -np.cos(theta)*h_acc/h
    a_acc = alpha-gamma

   # integrate angular acceleration to get angular velocity
    omega += a_acc*dt
    omega = omega*C
    # integrate angular velocity to get angle
    theta += omega*dt

    # integrate dt to get time
    t += dt

    velocity += acc*dt
    distance += velocity*dt

    #-------------------------------------------------------------------
    #                          Draw Stuff
    #-------------------------------------------------------------------

    if draw_stick_man:
        pygame.gfxdraw.filled_polygon(screen, (stick_man), (0, 249, 249, 20))         
        #pygame.gfxdraw.aapolygon(screen, (stick_man), (255, 255, 255, 255))

    origin[0] = 500+int(distance*1674)+int(((theta-np.pi)*np.pi)*25/2)
    origin[0] = np.mod(origin[0],1000)
    tbot_rot = np.array(geom.rotxy(theta,tbot))
    tbot_tup = tuple(map(tuple, tuple((tbot_rot+origin).astype(int))))

    noise = np.random.rand(1)*np.pi/180
    spokes_rot = np.array(geom.rotxy((distance*1674/50)+theta,spokes))
    spokes_tup = tuple(map(tuple, tuple((spokes_rot+origin).astype(int))))

    pygame.gfxdraw.filled_polygon(screen, (tbot_tup), (0, 249, 249, 100))         
    pygame.gfxdraw.aapolygon(screen, (tbot_tup), (255, 255, 255, 255))

    pygame.gfxdraw.aapolygon(screen, (spokes_tup), (255, 255, 255, 255))
    pygame.gfxdraw.aacircle(screen, origin[0], origin[1], 46, (255, 255, 255, 255))
    pygame.gfxdraw.aacircle(screen, origin[0], origin[1], 49, (255, 255, 255, 255))
    
    pygame.draw.lines(screen, (255, 255, 255, 255), False, (track_marks_tup),1)
    

    #-------------------------------------------------------------------
    #                          Get Key Pressed
    #------------------------------------------------------------------- 
          
    for event in pygame.event.get():
        keys = pygame.key.get_pressed()

    if keys[pgl.K_s]:
        theta = np.pi+0.001
        omega = 0
        alpha = 0
            
    if keys[pgl.K_q]:
        done = True

    pygame.display.flip()
    clock.tick(framerate)

pygame.display.quit()
pygame.quit()

print('Connection Closed')

        
