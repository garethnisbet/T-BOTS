#!/usr/bin/python
import pygame, sys, pygame.mixer, os
from pygame.locals import *
from time import sleep, time
import bluetooth as bt
dirpath = os.path.dirname(os.path.realpath(__file__))
timestart = time()
speedfactor = 0.6
speedlimit = 70
turnspeedlimit = 60

oldvals = [0,0,0,0]

sendcount = 0
bd_addr = '98:D3:51:FD:81:AC' 


class bt_connect(object):
    def __init__(self,bt_addr,port):
        self.bt_addr = bt_addr
        self.port = port
    def connect(self,con):
        if con == 1:
            try:
                print('connecting to '+self.bt_addr)
                self.sock = bt.BluetoothSocket( bt.RFCOMM )
                self.sock.connect((self.bt_addr,1))
                self.sock.settimeout(5)
                print('connected to '+self.bt_addr)
                return self.sock.getpeername()
            except:
                print('Connection Failed')
                
        else:
            try:
                print('Closing connection to '+self.bt_addr)
                self.sock.close()
                return 'Disconnected'
            except:
                return 'Not connected'
                
    def connected(self):
        try:
            self.sock.getpeername()
            status = 1
        except:
            status = 0
        return status

    def send_data(self,sendstr,sendtwice):
        try:
            if sendstr == '200200Z':
                if sendtwice <= 2:
                    builtstr = chr(0X02)+sendstr+chr(0X03)
                    self.sock.send(builtstr.encode(encoding='utf-8'))
                    sendtwice += 1                   
            else:
                builtstr = chr(0X02)+sendstr+chr(0X03)
                self.sock.send(builtstr.encode(encoding='utf-8'))
                sendtwice = 0
        except:
            print('Error sending data...')
        return sendtwice

    def get_data(self,oldvalues = [0,0,0,0]):
        try:
            data = self.sock.recv(32).decode(encoding='utf-8')
            data = data.split('\x02')
            ministring = data[0]
            splitstr = ministring.split(',')
        except:
            splitstr = []
        
        if len(splitstr) == 4:
            oldkps, oldkp, oldtrim, oldgyro = splitstr[0], splitstr[1], splitstr[2], splitstr[3]
            oldgyro = oldgyro[:-2]
            oldvalues = [oldkps, oldkp, oldtrim, oldgyro]
            return oldkps, oldkp, oldtrim, float(oldgyro)
        else:
            return oldvalues[0], oldvalues[1],oldvalues[2],oldvalues[3]
            
    def get_name(self):
        try:
            return self.sock.getpeername()
        except:
            return 'Not Connected'



###################  Screen Text Class #############################

class TextPrint(object):
    def __init__(self):
        self.reset()
        self.font = pygame.font.Font(None, 20)

    def tprint(self, screen, textString):
        textBitmap = self.font.render(textString, True, WHITE)
        screen.blit(textBitmap, (self.x, self.y))
        self.y += self.line_height

    def reset(self):
        self.x = 10
        self.y = 10
        self.line_height = 15

    def indent(self):
        self.x += 10

    def unindent(self):
        self.x -= 10


###################  Instantiate BT Class #############################    

btcom = bt_connect(bd_addr,1)
      
        
# Define some colors.
BLACK = pygame.Color('black')
WHITE = pygame.Color('white')
GRAY = pygame.Color('gray')


pygame.init()

# Set the width and height of the screen (width, height).
screen = pygame.display.set_mode((350, 550))
logo = pygame.image.load(dirpath+'/logo.png')
bg = pygame.image.load(dirpath+'/hex.jpg').convert()
bgG = pygame.image.load(dirpath+'/hexG.jpg').convert()


pygame.display.set_caption("T-Bot Joystick Bridge")

# Loop until the user clicks the close button.
done = False

# Used to manage how fast the screen updates.
clock = pygame.time.Clock()

# Initialize the joysticks.
pygame.joystick.init()

# Get ready to print.
textPrint = TextPrint()

# -------- Main Program Loop -----------
while not done:
        
    #
    # EVENT PROCESSING STEP
    #
    # Possible joystick actions: JOYAXISMOTION, JOYBALLMOTION, JOYBUTTONDOWN,
    # JOYBUTTONUP, JOYHATMOTION
    for event in pygame.event.get(): # User did something.
        if event.type == pygame.QUIT: # If user clicked close.
            done = True # Flag that we are done so we exit this loop.
            btcom.connect(0)
            print('Connection Closed')
    if event.type == KEYDOWN and event.key == K_q:
        btcom.connect(0)
        pygame.display.quit()
        sys.exit()
        print('Connection Closed')
        pass
    

    if btcom.connected():
        screen.blit(bg, [0, 0])
    else:
        tries = 0
        while btcom.connected() < 1 and tries < 10:
            print('Connecting ...')
            screen.blit(bgG, [0, 0])
            pygame.display.flip()
            try:
                print('Try '+str(tries+1)+' of 10')
                btcom.connect(0)
                btcom.connect(1)
                tries+=1
            except:
                print('Something went wrong')
                
        if btcom.connected() < 1:
            print('Exiting Program')
            pygame.display.quit()
            sys.exit()
        else:
            tries = 0
            
            

    
    textPrint.reset()

    # Get count of joysticks.
    joystick_count = pygame.joystick.get_count()

    textPrint.tprint(screen, "Number of joysticks: {}".format(joystick_count))
    textPrint.indent()

    # For each joystick:
    for i in range(1):
        joystick = pygame.joystick.Joystick(i)
        joystick.init()

        textPrint.tprint(screen, "Joystick {}".format(i))
        textPrint.indent()

        # Get the name from the OS for the controller/joystick.
        name = joystick.get_name()
        textPrint.tprint(screen, "Joystick name: {}".format(name))

        # Usually axis run in pairs, up/down for one, and left/right for
        # the other.
        axes = joystick.get_numaxes()
        textPrint.tprint(screen, "")
        textPrint.tprint(screen, "Number of axes: {}".format(axes))
        textPrint.indent()

        for i in range(axes):
            axis = joystick.get_axis(i)
            textPrint.tprint(screen, "Axis {} value: {:>6.3f}".format(i, axis))
        axis0 = joystick.get_axis(0)
        axis1 = joystick.get_axis(1)
        axis2 = joystick.get_axis(2)
        axis3 = joystick.get_axis(3)
        textPrint.unindent()
        textPrint.tprint(screen, "")
        buttons = joystick.get_numbuttons()
        textPrint.tprint(screen, "Number of buttons: {}".format(buttons))
        textPrint.indent()

        for i in range(buttons):
            button = joystick.get_button(i)
            textPrint.tprint(screen,
                             "Button {:>2} value: {}".format(i, button))
        textPrint.unindent()

        hats = joystick.get_numhats()
        textPrint.tprint(screen, "")
        textPrint.tprint(screen, "Number of hats: {}".format(hats))
        textPrint.indent()

        # Hat position. All or nothing for direction, not a float like
        # get_axis(). Position is a tuple of int values (x, y).
        for i in range(hats):
            hat = joystick.get_hat(i)
            textPrint.tprint(screen, "Hat {} value: {}".format(i, str(hat)))
            if hat[1] == 1:
                speedfactor += 0.1
            elif hat[1] == -1:
                speedfactor -= 0.1
            elif hat[0] == -1:
                speedlimit -= 5
            elif hat[0] == +1:
                speedlimit += 5
            if speedlimit >= 100:
                speedlimit = 100
            if speedlimit <= 0:
                speedlimit = 0
            if speedfactor >= 5:
                speedfactor = 5
            if speedfactor <= 0:
                speedfactor = 0
                
        textPrint.unindent()
        textPrint.tprint(screen, "")
        textPrint.tprint(screen, "T-Bot Data")
        textPrint.indent()
                
        oldvals = btcom.get_data(oldvals)
        textPrint.tprint(screen, "gyrodata: {}".format(str(oldvals[3])))
        textPrint.tprint(screen, "kps: {}".format(str(oldvals[0])))
        textPrint.tprint(screen, "kp: {}".format(str(oldvals[1])))
        textPrint.tprint(screen, "trim: {}".format(str(oldvals[2])))
        textPrint.tprint(screen, "Speed Factor: {}".format(str(speedfactor)))
        textPrint.tprint(screen, "Speed Limit: {}%".format(str(speedlimit)))

        textPrint.unindent()

    #
    # #############   Send data   #################################
    #
        if abs(axis0)+abs(axis1)+abs(axis2)+abs(axis3) != 0:
            slowfactor = 1+joystick.get_button(7)
            turn = 200+int(((axis0+(axis2*0.5))*speedfactor*100/slowfactor))
            speed = 200-int(((axis1+(axis3*0.5))*speedfactor*100/slowfactor))
            if speed > 200+speedlimit:
                speed = 200+speedlimit
            if speed < 200-speedlimit:
                speed = 200-speedlimit

            if turn > 200+turnspeedlimit:
                turn = 200+turnspeedlimit
            if turn < 200-turnspeedlimit:
                turn = 200-turnspeedlimit
            cmdwrite = 1       
            sendstring = str(turn)+str(speed)+'Z'
            sendcount = btcom.send_data(sendstring,sendcount)
        else:
            sendstring = '200200Z'
            sendcount = btcom.send_data(buttonstring,sendcount)
        if joystick.get_button(0):
            buttonstring = '200200F' # trim +ve
            sendcount = btcom.send_data(buttonstring,sendcount)
        elif joystick.get_button(2):
            buttonstring = '200200E' # trim -ve
            sendcount = btcom.send_data(buttonstring,sendcount)

        elif joystick.get_button(1):
            buttonstring = '200200B' # kps +ve
            sendcount = btcom.send_data(buttonstring,sendcount)
        elif joystick.get_button(3):
            buttonstring = '200200A' # kps -ve
            sendcount = btcom.send_data(buttonstring,sendcount)
        elif joystick.get_button(9):
            buttonstring = '200200T' # kps -ve
            sendcount = btcom.send_data(buttonstring,sendcount)



        
    # Go ahead and update the screen with what we've drawn.
    screen.blit(logo,(230,420))
    pygame.display.flip()

    # Limit to 20 frames per second.
    clock.tick(20)

# Close the window and quit.
# If you forget this line, the program will 'hang'
# on exit if running from IDLE.
pygame.quit()
