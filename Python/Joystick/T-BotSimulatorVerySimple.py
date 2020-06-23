#!/usr/bin/python
import sys, os
import numpy as np
sys.path.append('/home/pi/GitHub/T-BOTS/Python')
from TBotTools import pid, geometry, pgt
from time import time
import pygame
import pygame.gfxdraw
import pygame.locals as pgl
from datetime import datetime
clock = pygame.time.Clock()
dirpath = os.path.dirname(os.path.realpath(__file__))+'/Images'

framerate = 30 # set to 30 for Rasoberry pi

#-----------------------------------------------------------------------
#                           Physical constants
#-----------------------------------------------------------------------
dt = 1.0/framerate 
sf = 1.0
acc_g = 9.81 
l = 0.045 # distance between the centre of gravity of the T-Bot and the axil
R = 0.024 # Radius of wheels
C = 0.99 # Friction
h=l+R # Maximum distance between the centre of gravity and the ground 
#h = 828 # Tallest building
#h = 5

t = 0
alpha = 0
gamma = 0
acc = 0
omega = 0
velocity = 0
distance = 0
theta = np.pi*1.01

height_of_man = 1.8923 # Me
#height_of_man = 0.1524 # 1:12 Scale (approx. 5-6") Action Figure
height_of_man = 0.0508 # 1:48 Scale (approx. 2") Action Figure

Tbot_scalefactor = 216
Man_scalefactor = (height_of_man/(l*2))*Tbot_scalefactor
wheel_radius = int(R/l*Tbot_scalefactor/2.2)
draw_stick_man = 1

tyre = 4

#-----------------------------------------------------------------------
#                          Drawing Geometry
#-----------------------------------------------------------------------

geom = geometry.geometry()

origin = [500,319]
tbot_drawing_offset = [-78,-10]
tbot = np.loadtxt('T-BotSideView.dat')
tbot = np.vstack((tbot,tbot[0,:]))+tbot_drawing_offset # closes the shape and adds an offset
tbot = tbot/(tbot[:,1].max()-tbot[:,1].min())*Tbot_scalefactor

spokes = np.array([[0,1],[0,0],[ 0.8660254, -0.5],[0,0], [-0.8660254, -0.5 ],[0,0]])*(wheel_radius-tyre)

trackmarksArray = np.array([[0,origin[1]+wheel_radius],[1000,origin[1]+wheel_radius]])
track_marks_tup = tuple(map(tuple, tuple((trackmarksArray).astype(int))))

stick_man_data = np.loadtxt('Man.dat')
stick_man = np.vstack((stick_man_data,stick_man_data[0,:]))+tbot_drawing_offset # closes the shape and adds an offset
stick_man = stick_man/(stick_man[:,1].max()-stick_man[:,1].min())*Man_scalefactor
scaled_stick_man = stick_man
stick_man=stick_man-[stick_man[:,0].min(),stick_man[:,1].min()]
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
    screen.blit(track_image, (0,origin[1]+wheel_radius-8))
    
    #-------------------------------------------------------------------
    #                            The Physics
    #-------------------------------------------------------------------
    if theta >= np.pi/1.845 and theta <= 1.43*np.pi:
    #if theta >= -6*np.pi and theta <= 6*np.pi: # Use to play with swing up
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
    spokes_rot = np.array(geom.rotxy((distance*1674/wheel_radius)+theta,spokes))
    spokes_tup = tuple(map(tuple, tuple((spokes_rot+origin).astype(int))))

    pygame.gfxdraw.filled_polygon(screen, (tbot_tup), (0, 249, 249, 100))         
    pygame.gfxdraw.aapolygon(screen, (tbot_tup), (255, 255, 255, 255))

    pygame.gfxdraw.aapolygon(screen, (spokes_tup), (255, 255, 255, 255))
    pygame.gfxdraw.aacircle(screen, origin[0], origin[1], wheel_radius-tyre, (255, 255, 255, 255))
    pygame.gfxdraw.aacircle(screen, origin[0], origin[1], wheel_radius, (255, 255, 255, 255))
    
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

print('Simulation Closed')

        
