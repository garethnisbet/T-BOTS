#!/usr/bin/python
import sys, os
import numpy as np
sys.path.append('/home/pi/GitHub/T-BOTS/Python')
from TBotTools import pid, geometry, pgt
from time import time
import pygame
import pygame.gfxdraw
import pygame.locals as pgl
from collections import deque
from datetime import datetime
clock = pygame.time.Clock()
dirpath = os.path.dirname(os.path.realpath(__file__))+'/Images'

framerate = 30 # set to 30 for Rasoberry pi
dt = 1.0/framerate 

#-----------------------------------------------------------------------
#                           PID Tuning
#-----------------------------------------------------------------------

#------------------------- Tuning for g = g *0.1 -----------------------

#sf = 0.1
#s_kpo, s_kio, s_kdo = 0.050, 0.147, 0.041
#a_kpo, a_kio, a_kdo = 1.898, 0.006, 0.067

#----------------------- Tuning for the Moon ---------------------------

#sf = 0.165
#s_kpo, s_kio, s_kdo = 0.075, 0.94, 0.022
#a_kpo, a_kio, a_kdo = 3.03, 0.0096, 0.067

#------------------------ Tuning for Earth -----------------------------
sf = 1
s_kpo, s_kio, s_kdo = 0.090, 0.256, 0.00
a_kpo, a_kio, a_kdo = 12.651, 0.00, 0.26

#-----------------------------------------------------------------------
sf_original = sf

s_kp, s_ki, s_kd = s_kpo, s_kio, s_kdo
a_kp, a_ki, a_kd = a_kpo, a_kio, a_kdo

speed_pid = pid.pid(s_kp, s_ki, s_kd,[-10,10],[-5,5],dt)
angle_pid = pid.pid(a_kp, a_ki, a_kd,[6, 6],[-1,1],dt)



BLACK = pygame.Color('black')
WHITE = pygame.Color('white')
GRAY = pygame.Color('gray')
RED = pygame.Color('red')
save = 0
show_arrows = 0
draw_stick_man = 1

#-----------------------------------------------------------------------
#                           Physical constants
#-----------------------------------------------------------------------

acc_g = 9.81 
l = 0.045 # distance between the centre of gravity of the T-Bot and the axil
R = 0.024 # Radius of wheels
C = 0.99 # Friction
h=l+R # Maximum distance between the centre of gravity and the ground 
#h = 828 # Tallest building
#h = 5

auto_toggle = 0
auto = 1

#height_of_man = 1.8923 # Me
#height_of_man = 0.1524 # 1:12 Scale (approx. 5-6") Action Figure
height_of_man = 0.0508 # 1:48 Scale (approx. 2") Action Figure

tyre = 4
t = 0
alpha = 0
gamma = 0
acc = 0
omega = 0
velocity = 0
distance = 0
theta = 0.001
targetvelocity = 0

geom = geometry.geometry()
starttime = time()
lasttime = 0
timeflag = 1
draw_stick_man = 1


#-----------------------------------------------------------------------
#                          Drawing Geometry
#-----------------------------------------------------------------------

geom = geometry.geometry()


origin = [500,320]
tbot_drawing_offset = [-78,-10]
Tbot_scalefactor = 216


Man_scalefactor = (height_of_man/h/2)*Tbot_scalefactor
wheel_radius = int(R/l*Tbot_scalefactor/2.2)



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
stick_man = tuple(map(tuple, tuple((stick_man+[750-stick_man_h_centre,origin[1]+wheel_radius-stick_man[:,1].max()]).astype(int))))

speedfactor = 0.6
speedlimit = 65
turnspeedlimit = 70

oldvals = [0,0,0,0]

pygame.init()

# Set the width and height of the screen (width, height).
screen = pygame.display.set_mode((1000, 700))
pygame.display.set_caption("T-Bot Simulator")
# Used to manage how fast the screen updates.
clock = pygame.time.Clock()


# Use convert for the large images. This is the fastest format for blitting
# Background images
bg = pygame.image.load(dirpath+'/Simple/Gray.jpg').convert() 


# Do not use convert for the following images
# Button images
joystick_image = pygame.image.load(dirpath+'/Simple/joystick_only.png')
track_image = pygame.image.load(dirpath+'/Simple/line.png')
dpad = pygame.image.load(dirpath+'/Simple/dpad.png')
dpadU = pygame.image.load(dirpath+'/Simple/dpadU.png')
dpadD = pygame.image.load(dirpath+'/Simple/dpadD.png')
dpadL = pygame.image.load(dirpath+'/Simple/dpadL.png')
dpadR = pygame.image.load(dirpath+'/Simple/dpadR.png')
dpadUR = pygame.image.load(dirpath+'/Simple/dpadUR.png')
dpadDR = pygame.image.load(dirpath+'/Simple/dpadDR.png')
dpadUL = pygame.image.load(dirpath+'/Simple/dpadUL.png')
dpadDL = pygame.image.load(dirpath+'/Simple/dpadDL.png')

bpad = pygame.image.load(dirpath+'/Simple/bpad.png')
bpadU = pygame.image.load(dirpath+'/Simple/bpadU.png')
bpadD = pygame.image.load(dirpath+'/Simple/bpadD.png')
bpadL = pygame.image.load(dirpath+'/Simple/bpadL.png')
bpadR = pygame.image.load(dirpath+'/Simple/bpadR.png')
bpadUR = pygame.image.load(dirpath+'/Simple/bpadUR.png')
bpadDR = pygame.image.load(dirpath+'/Simple/bpadDR.png')
bpadUL = pygame.image.load(dirpath+'/Simple/bpadUL.png')
bpadDL = pygame.image.load(dirpath+'/Simple/bpadDL.png')

stick = pygame.image.load(dirpath+'/Simple/stick.png')

L1 = pygame.image.load(dirpath+'/Simple/L1.png')
L2 = pygame.image.load(dirpath+'/Simple/L2.png')
L1L2 = pygame.image.load(dirpath+'/Simple/L1L2.png')
R1 = pygame.image.load(dirpath+'/Simple/R1.png')
R2 = pygame.image.load(dirpath+'/Simple/R2.png')
R1R2 = pygame.image.load(dirpath+'/Simple/R1R2.png')

hoffset = 244
voffset = 388
posdpad = (102+hoffset, 75+voffset)
posbpad = (327+hoffset, 75+voffset)
posL = (106+hoffset,15+voffset)
posR = (338+hoffset,15+voffset)



arrow = np.array([[2,0],[2,150],[7,150],[0,165],[-7,150],[-2,150],[-2,0],[2,0]])

pos_joystick = (298,420)
posstickL = (164+hoffset, 130+voffset)
posstickR = (287+hoffset, 130+voffset)
# Get ready to print.
textPrint = pgt.TextPrint(pygame.Color('white'))


# Initialize the joystick.
pygame.joystick.init()
joystick = pygame.joystick.Joystick(0) # 0 for first joystick, 1 for the next etc.
joystick.init()
name = joystick.get_name()
axes = joystick.get_numaxes()
hats = joystick.get_numhats()

readdataevent = pygame.USEREVENT+1
pygame.time.set_timer(readdataevent, 60)

framecount = 1
done = False

xdatarange = [760,950]
y_origin = 500
yscale = 100
pts = deque(maxlen=xdatarange[1]-xdatarange[0])
pts2 = deque(maxlen=xdatarange[1]-xdatarange[0])
for ii in range(xdatarange[0],xdatarange[1]):
    pts.appendleft((ii,0))
    pts2.appendleft((ii,0))
iii = 200
aa = np.zeros((len(pts),2))
aa[:,1]=np.array(pts)[:,1]
aa[:,0]=np.array(range(xdatarange[0],xdatarange[1]))

cc = np.zeros((len(pts),2))
cc[:,1]=np.array(pts2)[:,1]
cc[:,0]=np.array(range(xdatarange[0],xdatarange[1]))
bb=np.copy(aa)
dd=np.copy(cc)
# -------- Main Program Loop -----------

while not done:
    g = acc_g * sf
    #screen.fill((0, 0, 0))
    screen.blit(bg,(0,0))
    screen.blit(joystick_image, pos_joystick)
    screen.blit(track_image, (0,origin[1]+wheel_radius-8))


    #-------------------------------------------------------------------
    #                            The Physics
    #-------------------------------------------------------------------

    if theta >= -np.pi/2.2 and theta <= np.pi/2.2:
        
        
        alpha =  np.sin(theta)*g/h

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
        theta = np.arcsin(((R*np.cos(theta_c)+np.sqrt(l**2-(R*np.sin(theta_c))**2))  *np.sin(theta_c))/l) # only good for  -90 > theta_c < 90

        # integrate dt to get time
        t += dt
 
        velocity += acc*dt
        distance += (velocity*dt)
		'''

        #---------------------------------------------------------------


        origin[0] = 500+int(distance*1674)+int(((theta)*np.pi)*25/2)
        origin[0] = np.mod(origin[0],1000)
        tbot_rot = np.array(geom.rotxy(theta+np.pi,tbot))
        tbot_tup = tuple(map(tuple, tuple((tbot_rot+origin).astype(int))))

        noise = np.random.rand(1)*np.pi/180
        spokes_rot = np.array(geom.rotxy((distance*1674/wheel_radius)+theta,spokes))
        spokes_tup = tuple(map(tuple, tuple((spokes_rot+origin).astype(int))))
        
        #---------------------------------------------------------------
        #                       The PID Controller
        #---------------------------------------------------------------
        
        if auto:          
            #settheta = -speed_pid.output(targetvelocity,-velocity,dt)
            # The T-Bot does not have motor encoders so the velocity is is calculated as a function of angle
            settheta = -speed_pid.output(geom.v2ang(h,g,targetvelocity),-geom.v2ang(h,g,velocity),dt)
            acc = -angle_pid.output(settheta,(theta+noise[0]),dt)
            #acc = -angle_pid.output(np.pi-geom.v2ang(h,g,targetvelocity),(theta+noise[0]),dt)
            
        #---------------------------------------------------------------
        
        if show_arrows:
            arrow_rot1 = np.array(geom.rotxy(theta,arrow))
            arrow1_tup = tuple(map(tuple, tuple((arrow_rot1+origin).astype(int))))
            arrow_rot2 = np.array(geom.rotxy(np.pi+settheta,arrow))
            arrow2_tup = tuple(map(tuple, tuple((arrow_rot2+origin).astype(int))))
            arrow_rot3 = np.array(geom.rotxy(np.pi+geom.v2ang(h,g,targetvelocity),arrow))
            arrow3_tup = tuple(map(tuple, tuple((arrow_rot3+origin).astype(int))))         
    else:

        textPrint.abspos(screen, "Press the start button to reset.",(430,180))
        if timeflag:
            lasttime = time()-starttime
            timeflag = 0

    if draw_stick_man:
        pygame.gfxdraw.filled_polygon(screen, (stick_man), (0, 249, 249, 20))         
        #pygame.gfxdraw.aapolygon(screen, (stick_man), (255, 255, 255, 255))

    pygame.gfxdraw.filled_polygon(screen, (tbot_tup), (0, 249, 249, 100))         
    pygame.gfxdraw.aapolygon(screen, (tbot_tup), WHITE)
    pygame.gfxdraw.aapolygon(screen, (spokes_tup), WHITE)
    pygame.gfxdraw.aacircle(screen, origin[0], origin[1], wheel_radius-tyre, WHITE)
    pygame.gfxdraw.aacircle(screen, origin[0], origin[1], wheel_radius, WHITE)
    pygame.draw.lines(screen, WHITE, False, (track_marks_tup),1)
    
    pts.appendleft((iii,theta-np.pi))
    pts2.appendleft((iii,velocity))
    iii+=1
    pygame.draw.lines(screen, (0,255,255), False, ((xdatarange[0],y_origin+0.5*yscale),(xdatarange[1],y_origin+0.5*yscale)),1)
    pygame.draw.lines(screen, (0,255,255), False, ((xdatarange[0],y_origin),(xdatarange[0],y_origin+yscale)),1)
    pygame.draw.lines(screen, (0,255,255), False, ((xdatarange[-1],y_origin),(xdatarange[-1],y_origin+yscale)),1)
    
    if show_arrows:
        pygame.gfxdraw.filled_polygon(screen, (arrow1_tup), (0,255,255,155)) 
        pygame.gfxdraw.aapolygon(screen, (arrow1_tup), (0,255,255,200))        
        pygame.gfxdraw.filled_polygon(screen, (arrow2_tup), (255,255,255,155)) 
        pygame.gfxdraw.aapolygon(screen, (arrow2_tup), (255,255,255,200))
        pygame.gfxdraw.filled_polygon(screen, (arrow3_tup), (255,0,0,155))
        pygame.gfxdraw.aapolygon(screen, (arrow3_tup), (255,0,0,200)) 
    
    if iii > xdatarange[1]:
        iii = xdatarange[0]
    aa[:,1]=np.array(pts)[:,1]
    cc[:,1]=np.array(pts2)[:,1]

    try:  
        bb[:,1] = (yscale/((aa[:,1]-aa[:,1].max()).min())*(aa[:,1]-aa[:,1].max()))+y_origin
        dd[:,1] = (yscale/((cc[:,1]-cc[:,1].max()).min())*(cc[:,1]-cc[:,1].max()))+y_origin
        gdata = tuple(map(tuple, tuple(bb)))
        vdata = tuple(map(tuple, tuple(dd)))
        pygame.draw.lines(screen, WHITE, False, (gdata),1)
        pygame.draw.lines(screen, RED, False, (vdata),1)
        
    except:
        b=1
               
    textPrint.abspos(screen, "{:+.2f}".format(aa[:,1].max()),[xdatarange[0],y_origin-20])
    textPrint.abspos(screen, "{:+.2f}".format(aa[:,1].min()),[xdatarange[0],y_origin+yscale+5])
    textPrint.tprint(screen,'Angle')
    textPrint.setColour(RED)
    textPrint.abspos(screen, "{:+.2f}".format(cc[:,1].max()),[xdatarange[-1],y_origin-20])
    textPrint.abspos(screen, "{:+.2f}".format(cc[:,1].min()),[xdatarange[-1],y_origin+yscale+5])
    textPrint.tprint(screen,'Velocity')
    textPrint.setColour(WHITE)
    
    if pygame.event.get(readdataevent):
        oldvals = [0,0,0,0]
        
    for event in pygame.event.get(): 
        if event.type == pygame.QUIT: # If user clicked close.
            done = True # Flag that we are done so we exit this loop.

    keys = pygame.key.get_pressed()

    if keys[pgl.K_g]:
        sf += 0.01
    elif keys[pgl.K_f]:
        sf -= 0.01
            
    if keys[pgl.K_q]:
        done = True
  
    for i in range(hats):
        hat = joystick.get_hat(i)

    axis0 = joystick.get_axis(0)
    axis1 = joystick.get_axis(1)
    axis2 = joystick.get_axis(2)
    axis3 = joystick.get_axis(3)
 
    if keys[pgl.K_UP]:
        show_arrows = 1
    elif keys[pgl.K_DOWN]:
        show_arrows = 0
    
    if keys[pgl.K_a]:
        auto = 1
    elif keys[pgl.K_m]:
        auto = 0
#
    if auto:
        targetvelocity =  -axis0 * 0.2
    else:
        #acc = axis0
        acc = axis0*2 # swing up
        
    # ------------------ Highlight buttons ----------------#
    screen.blit(dpad,posdpad)
    screen.blit(bpad,posbpad)
    screen.blit(stick,(posstickL[0]+axis0*5,posstickL[1]+axis1*5))
    screen.blit(stick,(posstickR[0]+axis2*5,posstickR[1]+axis3*5))

    if hat[0] == 1:
        screen.blit(dpadR,posdpad)
        s_ki += 0.001
        speed_pid.set_PID(s_kp,s_ki,s_kd)
    elif hat[0] == -1:
        screen.blit(dpadL,posdpad)
        s_ki -= 0.001
        if s_ki < 0:
            s_ki = 0
        speed_pid.set_PID(s_kp,s_ki,s_kd)
    elif hat[1] == 1:
        screen.blit(dpadU,posdpad)
        s_kp += 0.001
        speed_pid.set_PID(s_kp,s_ki,s_kd)
    elif hat[1] == -1:
        screen.blit(dpadD,posdpad)
        s_kp -= 0.001
        if s_kp < 0:
            s_kp = 0
        speed_pid.set_PID(s_kp,s_ki,s_kd)
    else:
        screen.blit(dpad,posdpad)
        
    if (hat[0] == -1) & (hat[1] == 1):
        screen.blit(dpadUL,posdpad)
    elif (hat[0] == 1) & (hat[1] == -1):
        screen.blit(dpadDR,posdpad)
    elif (hat[0] == 1 & hat[1] == 1):
        screen.blit(dpadUR,posdpad)
    elif hat[0] == -1 & hat[1] == -1:
        screen.blit(dpadDL,posdpad)
        
    if joystick.get_button(0):
        screen.blit(bpadU,posbpad)
        a_kp += 0.001
        angle_pid.set_PID(a_kp,a_ki,a_kd)
    elif joystick.get_button(1):
        screen.blit(bpadR,posbpad)
        a_ki += 0.001
        angle_pid.set_PID(a_kp,a_ki,a_kd)      
    elif joystick.get_button(2):
        screen.blit(bpadD,posbpad)
        a_kp -= 0.001
        if a_kp < 0:
            a_kp = 0
        angle_pid.set_PID(a_kp,a_ki,a_kd)
        
    elif joystick.get_button(3):
        screen.blit(bpadL,posbpad)
        a_ki -= 0.001
        if a_ki < 0:
            a_ki = 0
        angle_pid.set_PID(a_kp,a_ki,a_kd)
    else:
        screen.blit(bpad,posbpad)

    if joystick.get_button(8):
        speed_pid.set_PID(s_kpo,s_kio,s_kdo)
        angle_pid.set_PID(a_kpo,a_kio,a_kdo)
        sf = sf_original
        
    elif joystick.get_button(9):
        alpha = 0
        gamma = 0
        acc = 0
        omega = 0
        velocity = 0
        distance = 0
        theta = 0.001
        origin[0] = 500
        speed_pid.clear()
        angle_pid.clear()
        starttime = time()
        timeflag = 1
   
    if joystick.get_button(0) & joystick.get_button(1):
        screen.blit(bpadUR,posbpad)
    elif joystick.get_button(1) & joystick.get_button(2):
        screen.blit(bpadDR,posbpad)
    elif joystick.get_button(2) & joystick.get_button(3):
        screen.blit(bpadDL,posbpad)
    elif joystick.get_button(0) & joystick.get_button(3):
        screen.blit(bpadUL,posbpad)

    if joystick.get_button(4):
        screen.blit(L1,posL)
        s_kd += 0.001
        speed_pid.set_PID(s_kp,s_ki,s_kd)
    elif joystick.get_button(6):
        screen.blit(L2,posL)
        s_kd -= 0.001
        if s_kd < 0:
            s_kd = 0
        speed_pid.set_PID(s_kp,s_ki,s_kd)
    elif joystick.get_button(5):
        screen.blit(R1,posR)
        a_kd += 0.001
        angle_pid.set_PID(a_kp,a_ki,a_kd)
    elif joystick.get_button(7):
        screen.blit(R2,posR)
        a_kd -= 0.001
        if a_kd < 0:
            a_kd = 0
        angle_pid.set_PID(a_kp,a_ki,a_kd)
    else:
        screen.blit(bpad,posbpad)
        
    if joystick.get_button(4) & joystick.get_button(6):
        screen.blit(L1L2,posL)
    elif joystick.get_button(5) & joystick.get_button(7):
        screen.blit(R1R2,posR)
    elif joystick.get_button(4) & joystick.get_button(5):
        screen.blit(L1,posL)
        screen.blit(R1,posR)
    elif joystick.get_button(4) & joystick.get_button(7):
        screen.blit(L1,posL)
        screen.blit(R2,posR)
    elif joystick.get_button(6) & joystick.get_button(5):
        screen.blit(L2,posL)
        screen.blit(R1,posR)
    elif joystick.get_button(6) & joystick.get_button(7):
        screen.blit(L2,posL)
        screen.blit(R2,posR)
        
    if joystick.get_button(4) & joystick.get_button(6) & joystick.get_button(5):
        screen.blit(L1L2,posL)
        screen.blit(R1,posR)
    elif joystick.get_button(4) & joystick.get_button(6) & joystick.get_button(7):
        screen.blit(L1L2,posL)
        screen.blit(R2,posR)
    elif joystick.get_button(4) & joystick.get_button(5) & joystick.get_button(7):
        screen.blit(L1,posL)
        screen.blit(R1R2,posR)
    elif joystick.get_button(5) & joystick.get_button(6) & joystick.get_button(7):
        screen.blit(L2,posL)
        screen.blit(R1R2,posR) 
    
    if joystick.get_button(4) & joystick.get_button(5) & joystick.get_button(6) & joystick.get_button(7):
        screen.blit(L1L2,posL)
        screen.blit(R1R2,posR)

    
    s_kp = speed_pid.get_PID()[0]
    s_ki = speed_pid.get_PID()[1]
    s_kd = speed_pid.get_PID()[2]
    a_kp = angle_pid.get_PID()[0]
    a_ki = angle_pid.get_PID()[1]
    a_kd = angle_pid.get_PID()[2]
    textPrint.setfontsize(22)
    textPrint.setColour(pygame.Color(0,255,255,255))
    textPrint.abspos(screen, "T-Bot Simulator",(10,10))
    textPrint.setColour(WHITE)
    textPrint.setfontsize(16)
    textPrint.tprint(screen, "www.klikrobotics.com")
    textPrint.tprint(screen, " ")

    textPrint.tprint(screen, "T: {:.3f}".format(time()-starttime))
    textPrint.tprint(screen, "Last T: {:.3f}".format(lasttime))        
    textPrint.abspos(screen, "Tuning Parameters",(10,400))
    textPrint.tprint(screen, " ")
    textPrint.tprint(screen, "s_kp: {:.3f}".format(s_kp))
    textPrint.tprint(screen, "s_ki: {:.3f}".format(s_ki))
    textPrint.tprint(screen, "s_kd: {:.3f}".format(s_kd))
    textPrint.tprint(screen, " ")
    textPrint.tprint(screen, "a_kp: {:.3f}".format(a_kp))
    textPrint.tprint(screen, "a_ki: {:.3f}".format(a_ki))
    textPrint.tprint(screen, "a_kd: {:.3f}".format(a_kd))
    textPrint.tprint(screen, " ")
    if auto:
        textPrint.tprint(screen, "Auto - Press m for manual control")
    else:
        textPrint.tprint(screen, "Manual - Press a for automatic control")
    textPrint.tprint(screen,'Press i for information')
    textPrint.abspos(screen, "g: {:.2f}".format((g)),(890,10))
    textPrint.tprint(screen, "theta: {:.2f}".format((theta)*180/np.pi))
    textPrint.tprint(screen, "Alpha: {:.2f}".format(alpha))
    textPrint.tprint(screen, "Gamma: {:.2f}".format(gamma))    
    textPrint.tprint(screen, "Acceleration: {:.2f}".format(acc))
    textPrint.tprint(screen, "Velocity: {:.2f}".format(velocity))
    textPrint.tprint(screen, "Distance: {:.2f}".format(distance))
    
    textPrint.tprint(screen, "{} FPS".format(str(int(clock.get_fps()))))
    
    pygame.display.flip()

    # Limit to 60 frames per second. Set to 30 for Raspberry Pi. It can't run at 60 fps
    clock.tick(framerate)

    if keys[pgl.K_p]:
        waiting = 1
        while waiting:
            for event in pygame.event.get():
                keys = pygame.key.get_pressed()
                if keys[pgl.K_s]:
                    save = 1
                    if save:
                        pygame.image.save(screen, datetime.now().strftime("TutorialImages/%m%d%Y_%H%M%S.png"))
                        save = 0
                if keys[pgl.K_o]:
                    waiting = 0
                if keys[pgl.K_q]:
                    done = True
                    waiting = 0
    if keys[pgl.K_i]:
        waiting = 1
        while waiting:

            for event in pygame.event.get():
                keys = pygame.key.get_pressed()
                screen.blit(bg,(0,0))

                textPrint.setfontsize(22)
                textPrint.setColour(pygame.Color(0,255,255,255))
                textPrint.abspos(screen, "T-Bot Simulator",(10,10))
                textPrint.setColour(WHITE)
                textPrint.setfontsize(16)
                textPrint.tprint(screen, "www.klikrobotics.com")
                textPrint.setfontsize(20)
                textPrint.abspos(screen, "Keyboard",(200,80))
                textPrint.tprint(screen, "")
                textPrint.setfontsize(16)
                textPrint.tprint(screen, "p -> Pause")
                textPrint.tprint(screen, "o -> Resume")
                textPrint.tprint(screen, "s -> Save paused frame")
                textPrint.tprint(screen, "i -> For information")
                textPrint.tprint(screen, "m -> For manual control")
                textPrint.tprint(screen, "a -> For automatic PID control")
                textPrint.tprint(screen, "g -> increase g")
                textPrint.tprint(screen, "f -> decrease g")
                textPrint.tprint(screen, "Up arrow to show arrows")
                textPrint.tprint(screen, "Down arrow to hide arrows")
                textPrint.setfontsize(20)
                textPrint.abspos(screen, "Joystick",(600,80))
                textPrint.tprint(screen, "")
                textPrint.setfontsize(16)
                textPrint.tprint(screen, "Left side of the controller")
                textPrint.tprint(screen, "")
                textPrint.tprint(screen, "Up -> Increase speed proportional gain")
                textPrint.tprint(screen, "Down -> Decrease speed proportional gain")
                textPrint.tprint(screen, "Left -> Increase speed integral gain")
                textPrint.tprint(screen, "Right -> Decrease speed integral gain")
                textPrint.tprint(screen, "L1 -> Increase speed derivitive gain")
                textPrint.tprint(screen, "L2 -> Decrease speed derivitive gain")
                textPrint.tprint(screen, "")
                textPrint.tprint(screen, "Right side of the controller")
                textPrint.tprint(screen, "")
                textPrint.tprint(screen, "Triangle -> Increase angle proportional gain")
                textPrint.tprint(screen, "X -> Decrease angle proportional gain")
                textPrint.tprint(screen, "Square -> Increase angle integral gain")
                textPrint.tprint(screen, "Circle -> Decrease angle integral gain")
                textPrint.tprint(screen, "R1 -> Increase angle derivitive gain")
                textPrint.tprint(screen, "R2 -> Decrease angle derivitive gain")

                textPrint.setfontsize(40)
                textPrint.abspos(screen, "Press o to return to simulator",(290,500))
                
                pygame.display.flip()
                if keys[pgl.K_o]:
                    waiting = 0
                if keys[pgl.K_q]:
                    done = True
                    waiting = 0

pygame.display.quit()
pygame.quit()

print('Simulation Closed')

        
