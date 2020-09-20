#!/usr/bin/python
import sys, os
import numpy as np
currentpath = os.path.abspath(os.path.join(os.path.dirname( __file__ ), '..'))
sys.path.append(currentpath)
from TBotTools import geometry, pgt, pid
import pygame
import pygame.gfxdraw
import pygame.locals as pgl
clock = pygame.time.Clock()
dirpath = currentpath+'/Simulators/Images/'
framerate = 60 # set to 30 for Rasoberry pi
#-----------------------------------------------------------------------
#                           Physical constants
#-----------------------------------------------------------------------
dt = 1.0/framerate 
sf = 1.0
acc_g = 9.81 
l = 0.045 # distance between the centre of gravity of the T-Bot and the axil
R = 0.024 # Radius of wheels
C = 0.99  # Friction
h=l+R     # Maximum distance between the centre of gravity and the ground 
t = 0
alpha = 0
gamma = 0
acc = 0
omega = 0
velocity = 0
distance = 0
theta = 0.05
height_of_man = 1.8923 # My height
#height_of_man = 0.1524 # 1:12 Scale (approx. 5-6") Action Figure
height_of_man = 0.0508 # 1:48 Scale (approx. 2") Action Figure
Tbot_scalefactor = 216
height_of_TBot_body = 120E-3
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

#-----------------------------------------------------------------------
#                          Initialise Pygame
#-----------------------------------------------------------------------
pygame.init()
textPrint = pgt.TextPrint(pygame.Color('white'))
textPrint.setfontsize(18)
# Set the width and height of the screen (width, height).
screen = pygame.display.set_mode((1000, 700))
pygame.display.set_caption("T-Bot Simulator")
# Used to manage how fast the screen updates.
clock = pygame.time.Clock()
#-----------------------------------------------------------------------
#                           Load Images
#-----------------------------------------------------------------------
bg = pygame.image.load(dirpath+'/Gray.jpg').convert() 
track_image = pygame.image.load(dirpath+'line.png')
#-----------------------------------------------------------------------
record = 0
framecount = 1
done = False
# ---------------------- Main Program Loop -----------------------------
while not done:
    g = acc_g * sf
    screen.blit(bg,(0,0))
    screen.blit(track_image, (0,origin[1]+wheel_radius-8))
    #-------------------------------------------------------------------
    #                            The Physics
    #-------------------------------------------------------------------
    #if theta >= -np.pi/2.2 and theta <= np.pi/2.2:
    if theta >= -5*np.pi and theta <= 5*np.pi:        
        alpha =  np.sin(theta)*g/h
        h_acc = (alpha * R)+acc # Accounts for horizontal acceleration
                                # produced from the rotation of the 
                                # wheels as the T-Bot falls. The gearbox
                                # prevents free rotation of the wheels.
        gamma =  np.cos(theta)*h_acc/h
        a_acc = alpha-gamma
        # integrate angular acceleration to get angular velocity
        omega += a_acc*dt
        omega = omega*C
        # integrate angular velocity to get angle
        theta += omega*dt
        # integrate dt to get time
        t += dt
        velocity += acc*dt
        distance += (velocity*dt)
        '''
        theta_c = np.arctan2(l*np.sin(theta),l*np.cos(theta)+R)
        h_c = np.sqrt((l*np.sin(theta))**2+(l*np.cos(theta)+R)**2)
        alpha =  np.sin(theta_c)*g/h_c
        h_acc = (alpha * R)+acc # Accounts for horizontal acceleration
                                # produced from the rotation of the 
                                # wheels as the T-Bot falls. The gearbox
                                # prevents free rotation of the wheels.
        gamma =  np.cos(theta)*h_acc/l
        a_acc = alpha-gamma
        # integrate angular acceleration to get angular velocity
        omega += a_acc*dt
        omega = omega*C
        # integrate angular velocity to get angle
        theta_c += omega*dt
        theta = np.arcsin(((R*np.cos(theta_c)+np.sqrt(l**2-(R*np.sin(theta_c))**2))*np.sin(theta_c))/l)
        # integrate dt to get time
        t += dt
        velocity += acc*dt
        distance += (velocity*dt)
        '''
    #-------------------------------------------------------------------
    #                          Draw Stuff
    #-------------------------------------------------------------------
    if abs(theta) > np.pi/2:
        textPrint.abspos(screen, "Press the s key to reset.",(430,580))
    mm2px = Tbot_scalefactor/height_of_TBot_body
    origin[0] = 500+int(distance*mm2px)+int(((theta)*np.pi)*wheel_radius/4)       
    origin[0] = np.mod(origin[0],1000)
    tbot_rot = np.array(geom.rotxy(theta+np.pi,tbot))
    tbot_tup = tuple(map(tuple, tuple((tbot_rot+origin).astype(int))))
    noise = np.random.rand(1)*np.pi/180
    spokes_rot = np.array(geom.rotxy((distance*mm2px/wheel_radius)+theta,spokes))
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
        theta = 0.05
        omega = 0
        alpha = 0
        velocity = 0
    if keys[pgl.K_q]:
        done = True
    if keys[pygame.K_r]:
        record = 1
    if keys[pygame.K_c]:
        record = 0
        framecount = 1
    if record == 1:
        pygame.image.save(screen, "CapturedImages/{:04d}.png".format(framecount))
        framecount += 1
    if keys[pygame.K_p]:
        waiting = 1
        pressed = 1
        while waiting:
            for event in pygame.event.get():
                keys = pygame.key.get_pressed()
                if pressed:
                    textPrint.abspos(screen, "Press o to return to simulator",(420,500))
                pressed = 0
            if keys[pygame.K_o]:
                waiting = 0
            elif keys[pygame.K_q]:
                waiting = 0
                done = 1
            pygame.display.flip()
    pygame.display.flip()
    clock.tick(framerate)
pygame.display.quit()
pygame.quit()
print('Simulation Closed')
