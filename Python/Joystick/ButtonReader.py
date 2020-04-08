from time import sleep
import pygame

import pygame.locals as pgl
pygame.joystick.init()
joystick = pygame.joystick.Joystick(0)
joystick.init()
done = False
axes = joystick.get_numaxes()
buttons = joystick.get_numbuttons()
while not done:
    for i in range(axes):
        axis = joystick.get_axis(i)
        print(axis)
        
    for i in range(buttons):
        button = joystick.get_button(i)
        print(button)
