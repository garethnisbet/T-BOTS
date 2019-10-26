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
cmdwrite = 0

###################  Connection #############################
oldkps, oldkp, oldtrim, oldgyro, toggle = 0,0,0,0,0
search = False
if search == True:
    print('Searching for devices...')
    print("")
    nearby_devices = bt.discover_devices()
    #Run through all the devices found and list their name
    num = 0
    
    for i in nearby_devices:
	    num+=1
	    print(num , ": " , bt.lookup_name( i ))
    print('Select your device by entering its coresponding number...')
    selection = input("> ") - 1
    print('You have selected - '+bt.lookup_name(nearby_devices[selection]))

    bd_addr = nearby_devices[selection]
else:
    bd_addr = '98:D3:51:FD:81:AC'
    #bd_addr = '98:D3:91:FD:46:C9'
    print('connecting...')
error = 1
port = 1
while error:
    try:
        sock = bt.BluetoothSocket( bt.RFCOMM )
        sock.connect((bd_addr,1))
        sock.settimeout(5)
        error = 0
        print('connected to '+bd_addr)
    except:
        print('Trying again...')
        sock.close()
        error = 1
        sleep(2)
# Define some colors.
BLACK = pygame.Color('black')
WHITE = pygame.Color('white')
GRAY = pygame.Color('gray')


################### Functions  ###########################
def send(sendstr):
    try:
        builtstr = chr(0X02)+sendstr+chr(0X03)
        sock.send(builtstr.encode(encoding='utf-8'))
    except:
        sock.close()
        pygame.display.quit()
        sys.exit()
        pass


# This is a simple class that will help us print to the screen.
# It has nothing to do with the joysticks, just outputting the
# information.
class TextPrint(object):
    def __init__(self):
        self.reset()
        self.font = pygame.font.Font(None, 20)

    def tprint(self, screen, textString):
        textBitmap = self.font.render(textString, True, BLACK)
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

def parse():
    global oldkps
    global oldkp
    global oldtrim
    global oldgyro
    global toggle
    try:
        data = sock.recv(32).decode(encoding='utf-8')
        data = data.split('\x02')
        ministring = data[0]
        splitstr = ministring.split(',')
        oldkps, oldkp, oldtrim, oldgyro = splitstr[0], splitstr[1], splitstr[2], splitstr[3]
        oldgyro = oldgyro[:-2]

        return oldkps, oldkp, oldtrim, float(oldgyro)
    except:
        try:
            return oldkps, oldkp, oldtrim, float(oldgyro)
        except:
            return oldkps, oldkp, oldtrim, 0

##################################################################




pygame.init()

# Set the width and height of the screen (width, height).
screen = pygame.display.set_mode((350, 550))
logo = pygame.image.load(dirpath+'/logo.png')
bg = pygame.image.load(dirpath+'/hex.jpg').convert()


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
            sock.close()
            print('Connection Closed')
    if event.type == KEYDOWN and event.key == K_q:
        sock.close()
        pygame.display.quit()
        sys.exit()
        print('Connection Closed')
    #
    # DRAWING STEP
    #
    # First, clear the screen to white. Don't put other drawing commands
    # above this, or they will be erased with this command.
    screen.blit(bg, [0, 0])

    
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
                
        kps, kp, trim, gyrodata = parse()
        textPrint.tprint(screen, "gyrodata: {}".format(str(gyrodata)))
        textPrint.tprint(screen, "kps: {}".format(str(kps)))
        textPrint.tprint(screen, "kp: {}".format(str(kp)))
        textPrint.tprint(screen, "trim: {}".format(str(trim)))
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
            send(sendstring)
        else:
            sendstring = '200200Z'
            send(sendstring)
        if joystick.get_button(0):
            buttonstring = '200200F' # trim +ve
            send(buttonstring)
        elif joystick.get_button(2):
            buttonstring = '200200E' # trim -ve
            send(buttonstring)

        elif joystick.get_button(1):
            buttonstring = '200200B' # kps +ve
            send(buttonstring)
        elif joystick.get_button(3):
            buttonstring = '200200A' # kps -ve
            send(buttonstring)
        elif joystick.get_button(9):
            buttonstring = '200200T' # kps -ve
            send(buttonstring)



        
    # Go ahead and update the screen with what we've drawn.
    screen.blit(logo,(230,420))
    pygame.display.flip()

    # Limit to 20 frames per second.
    clock.tick(20)

# Close the window and quit.
# If you forget this line, the program will 'hang'
# on exit if running from IDLE.
pygame.quit()
