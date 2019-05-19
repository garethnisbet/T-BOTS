import pygame, sys, pygame.mixer
from pygame.locals import *
import serial
from time import sleep
print('-----------------------------------------------------------------')
print('Controls:\nClick and drag joystick to drive the T-Bot\nUse up, down, left, right arrow keys to drive the T-Bot\nPress w or s to change the speed factor for arrow controls.\nClick on plot or press c to clear plots\nPress q or Esc to quit or Ctrl c in this window\n')
print('-----------------------------------------------------------------\n\n\n')

baudrate = 38400
#port = 'COM5'
port = '/dev/tty.T-Bot-DevB'
sock = serial.Serial(port, baudrate)
#except:
#    print('Failed to connect.')

def send(sendstr):
    try:
        sock.write(sendstr.encode(encoding='utf-8'))
    except:
        sock.close()
        pygame.display.quit()
        sys.exit()

pygame.font.init()
basicfont = pygame.font.SysFont(None, 30)
oldkps, oldkp, oldtrim, oldgyro = str(0),str(0),str(0), str(0)

def parse():
    global oldkps
    global oldkp
    global oldtrim
    global oldgyro
    global toggle
    try:
        data = sock.read(32).decode(encoding='utf-8')
        data = data.split('\x02')
        ministring = data[0]
        splitstr = ministring.split(',')
        oldkps, oldkp, oldtrim, oldgyro = splitstr[0], splitstr[1], splitstr[2], splitstr[3]
        oldgyro = oldgyro[:-2]
        if toggle == 1:
            print('writing...')
            f.write(oldkps+','+oldkp+','+oldtrim+','+oldgyro+'\n')
        return oldkps, oldkp, oldtrim, float(oldgyro)
    except:
        try:
            return oldkps, oldkp, oldtrim, float(oldgyro)
        except:
            return oldkps, oldkp, oldtrim, 0

pygame.init()
clock = pygame.time.Clock()
size = width, height = 1200, 500
screen=pygame.display.set_mode(size)
############   Load art work    #####################
joytop = pygame.image.load('images/joytopglow.png')
joybase = pygame.image.load('images/joybase.png')
minus = pygame.image.load('images/minus.png')
plus = pygame.image.load('images/plus.png')
pluslight = pygame.image.load('images/pluslight.png')
minuslight = pygame.image.load('images/minuslight.png')
gTrim = pygame.image.load('images/Trim.png')
gTrimlight = pygame.image.load('images/Trimlight.png')
record = pygame.image.load('images/record.png')
pause = pygame.image.load('images/pause.png')


button1,button2,button3,button4,button5,button6,button7, button8, button9 , toggle = 0,0,0,0,0,0,0,0,0,0
# initialize variables
x,y = 0,0
colour = (0,0,0,0)
linecolor = 255, 0, 0
plotcolours = [(0, 255, 0),(255, 0, 0),(0, 0, 255),(255, 255, 0),(255, 0, 255), (0,255,255)]
iicolour = 0
textcolour = (255,255, 255)
mx,my = 0,0
mxnew, mynew = 250, 250
oldgyrodata = 0
ii=800
speedfactor = 0.5
pygame.draw.lines(screen, (255,255,255), False, ((800,100), (1160,100), (1160,400),(800,400),(800,100)),1)
f= open('plot.csv','w')
while True: # Continuous Pygame loop,
    pygame.display.update((800,0,1200,500))

    xstr, ystr = '200', '200'
    kps, kp, trim, gyrodata = parse()

    if gyrodata > 298:
        gyrodata = 298
    if gyrodata < 0:
        gyrodata = 0

    pygame.draw.lines(screen, plotcolours[iicolour], False, ((ii,oldgyrodata+101), (ii+1,gyrodata+101)),1)
    oldgyrodata = gyrodata
    kpstext = basicfont.render('KPS '+kps, True, textcolour)
    kptext = basicfont.render('KP ' +kp, True, textcolour)
    trimtext = basicfont.render('TRIM '+trim, True, textcolour)

    speedfactortext = basicfont.render('Speed Factor '+str(speedfactor), True, textcolour)
    mx,my = pygame.mouse.get_pos()
    p2x = mx
    p2y = my
    #print('x '+str(mx)+' y ' +str(my))
    c1, c2, c3 =  pygame.mouse.get_pressed()
    if mx > 480 or mx < 20 or my > 480 or my < 20:
        mx,my = 250,250

    jx = int(((mx-250)*0.43)+200)
    jy = int(((250-my)*0.43)+200)

    if mxnew != mx or mynew != my:   
        sendstring = chr(0X02)+str(jx)+str(jy)+chr(0X03)
        
        if c1==1:
            send(sendstring)
        else:
            send(chr(0X02)+'200200Z'+chr(0X03))         
        mxnew = mx
        mynew = my
    
    for event in pygame.event.get():       
        if event.type == pygame.QUIT:
            pygame.display.quit()
            sys.exit()
        elif event.type == MOUSEBUTTONDOWN:
            kps, kp, trim, gyrodata = parse()
 #           if p2x > 0 and p2x < 500 and p2y > 0 and p2y < 500:
 #               mx, my = 250,250

            if p2x > 680 and p2x < 706 and p2y > 100 and p2y < 123:
                button1 = 1

            if p2x > 680 and p2x < 706 and p2y > 130 and p2y < 153:
                button2 = 1

            if p2x > 680 and p2x < 706 and p2y > 230 and p2y < 253:
                button3 = 1

            if p2x > 680 and p2x < 706 and p2y > 260 and p2y < 283:
                button4 = 1

            if p2x > 580 and p2x < 706 and p2y > 360 and p2y < 383:
                button5 = 1

            if p2x > 680 and p2x < 706 and p2y > 390 and p2y < 413:
                button6 = 1

            if p2x > 720 and p2x < 740 and p2y > 375 and p2y < 395:
                button7 = 1
                
            if p2x > 800 and p2x < 1200 and p2y > 0 and p2y < 400:
                button8 = 1

            if p2x > 1120 and p2x < 1150 and p2y > 420 and p2y < 450:
                button9 = 1
                


        elif event.type == MOUSEBUTTONUP:
            button1 = 0
            button2 = 0
            button3 = 0
            button4 = 0
            button5 = 0
            button6 = 0
            button7 = 0
            button8 = 0
            button9 = 0

            


        if event.type == KEYDOWN and event.key == K_c:
            screen.fill(colour,(800,0,1200,402))
            pygame.draw.lines(screen, (255,255,255), False, ((800,100), (1160,100), (1160,400),(800,400),(800,100)),1)
            iicolour = 0
            ii = 800
        keys = pygame.key.get_pressed()


        if keys[K_RIGHT] and keys[K_UP]:
            send(chr(0X02)+'%03d%03dZ'%(240,200+(speedfactor*100))+chr(0X03))

        elif keys[K_LEFT] and keys[K_UP]:
            send(chr(0X02)+'%03d%03dZ'%(160,200+(speedfactor*100))+chr(0X03))

        elif keys[K_RIGHT] and keys[K_DOWN]:
            send(chr(0X02)+'%03d%03dZ'%(260,200-(speedfactor*100))+chr(0X03))

        elif keys[K_LEFT] and keys[K_DOWN]:
            send(chr(0X02)+'%03d%03dZ'%(140,200-(speedfactor*100))+chr(0X03))


        elif keys[K_DOWN]:
            send(chr(0X02)+'%03d%03dZ'%(200,200-(speedfactor*100))+chr(0X03))

        elif keys[K_UP]:
            send(chr(0X02)+'%03d%03dZ'%(200,200+(speedfactor*100))+chr(0X03))


        elif keys[K_RIGHT]:
            send(chr(0X02)+'260200Z'+chr(0X03))


        elif keys[K_LEFT]:
            send(chr(0X02)+'140200Z'+chr(0X03))

        elif keys[K_w]:
            
            speedfactor +=0.1
            if speedfactor > 1:
                speedfactor = 1.0
            
        elif keys[K_s]:
            speedfactor -=0.1
            if speedfactor < 0.1:
                speedfactor = 0.1
            


        else:
            if c1==0:
                send(chr(0X02)+'200200Z'+chr(0X03))
        


        if event.type == KEYDOWN and event.key == K_ESCAPE:
            sock.close()
            f.close()
            print('Your now disconnected.')
            pygame.display.quit()
            sys.exit()

        elif event.type == KEYDOWN and event.key == K_q:
            sock.close()
            pygame.display.quit()
            f.close()
            print('Your now disconnected.')
            sys.exit()
    
        screen.fill(colour,(0,0,800,500))

        screen.fill(colour,(1116,410,1146,440))
        screen.fill(colour,(800,420,1146,500))
        screen.blit(joybase,(250-230,250-230))
        screen.blit(joytop,(mx-75,my-75))
        screen.blit(plus,(680,100))
        screen.blit(minus,(680,130))
        screen.blit(plus,(680,230))
        screen.blit(minus,(680,260))
        screen.blit(plus,(680,360))
        screen.blit(minus,(680,390))
        screen.blit(gTrim,(720,375))
        



        if button1:
            screen.blit(pluslight,(680-3,100-3))
            buttonstring = chr(0X02)+'200200B'+chr(0X03)
            send(buttonstring)
        if button2:
            screen.blit(minuslight,(680-3,130-3))
            buttonstring2 = chr(0X02)+'200200A'+chr(0X03)
            send(buttonstring2)
        if button3:
            screen.blit(pluslight,(680-3,230-3))
            buttonstring3 = chr(0X02)+'200200D'+chr(0X03)
            send(buttonstring3)
        if button4:
            screen.blit(minuslight,(680-3,260-3))
            buttonstring4 = chr(0X02)+'200200C'+chr(0X03)
            send(buttonstring4)
        if button5:
            screen.blit(pluslight,(680-3,360-3))
            buttonstring5 = chr(0X02)+'200200F'+chr(0X03)
            send(buttonstring5)
        if button6:
            screen.blit(minuslight,(680-3,390-3))
            buttonstring6 = chr(0X02)+'200200E'+chr(0X03)
            send(buttonstring6)
        if button7:
            screen.blit(gTrimlight,(720-2,375-2))
            buttonstring7 = chr(0X02)+'200200T'+chr(0X03)
            send(buttonstring7)
        if button8:
            screen.fill(colour,(800,0,1200,500))
            pygame.draw.lines(screen, (255,255,255), False, ((800,100), (1160,100), (1160,400),(800,400),(800,100)),1)
            iicolour = 0
            ii = 800


        if button9==0 and toggle == 0:
            screen.fill(colour,(1116,410,1146,440))
            screen.blit(record,(1120,420))


        if toggle == 0:
            if button9==1:
                f= open('plot.csv','a')
                screen.fill(colour,(1116,410,1146,440))
                screen.blit(pause,(1120,420))
                toggle = 1
                

        elif toggle == 1:
            if button9==1:
                f.close()
                toggle = 0
        if toggle:
            screen.fill(colour,(1116,410,1146,400))
            screen.blit(pause,(1120,420))
            
        else:
            screen.fill(colour,(1116,410,1146,400))
            screen.blit(record,(1120,420))
            


        screen.blit(kpstext,(560,115))
        screen.blit(kptext,(560,245))
        screen.blit(trimtext,(560,375))
        screen.blit(joytop,(mx-75,my-75))
        screen.blit(speedfactortext,(800,420))
        
        
    ii+=1
    
    if ii > 1159:
        iicolour+=1
        ii = 801
    if iicolour > 5:
        iicolour = 0
    pygame.display.update()
    
