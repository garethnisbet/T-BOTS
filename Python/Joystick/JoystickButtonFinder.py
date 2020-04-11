#!/usr/bin/python
import sys
sys.path.append('/home/pi/GitHub/T-BOTS/Python')
from TBotTools import tbt, pgt
import pygame
import pygame.locals as pgl

clock = pygame.time.Clock()

pygame.init()

textPrint = pgt.TextPrint(pygame.Color('white'))     

# Set the width and height of the screen (width, height).
screen = pygame.display.set_mode((1000, 800))

pygame.display.set_caption("Joysticks")

# Loop until the user clicks the close button.
done = False

# Used to manage how fast the screen updates.
clock = pygame.time.Clock()

# Initialize the joysticks.
pygame.joystick.init()

# -------- Main Program Loop -----------

while not done:

    screen.fill((0,0,0),(0,0,1000,800))
    # EVENT PROCESSING STEP
    #
    # Possible joystick actions: JOYAXISMOTION, JOYBALLMOTION, JOYBUTTONDOWN,
    # JOYBUTTONUP, JOYHATMOTION
    for event in pygame.event.get(): # User did something.
        if event.type == pygame.QUIT: # If user clicked close.
            done = True # Flag that we are done so we exit this loop.

    if event.type == pgl.KEYDOWN and event.key == pgl.K_q:
        done = True
        
    textPrint.reset()

    # Get count of joysticks.
    joystick_count = pygame.joystick.get_count()

    textPrint.tprint(screen, "Number of joysticks: {}".format(joystick_count))
    textPrint.indent()

    # For each joystick:
    for i in range(joystick_count): # If you have multiple joysticks connected, set this index for the one you want to use.
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

 
   
    pygame.display.flip()


    clock.tick(30)


pygame.quit()
