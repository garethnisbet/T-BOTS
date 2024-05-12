import pygame
class GameControllers(object):
    '''Can use PS3, PS4 and generic controllers'''
    def __init__(self, controllertype, controller_index = 0):
        self.joystick = pygame.joystick.Joystick(controller_index)
        self.joystick.init()
        self.joystick_count = pygame.joystick.get_count()
        self.name = joystick.get_name()
        self.axes = joystick.get_numaxes()
        self.hats = joystick.get_numhats()
        self.controllertype = controllertype

    def getButtons(self):
        if self.controllertype = 'Genergic_Type1':
            if self.joystick.get_button(0):
                button = triangle
            else
            self.circle = self.joystick.get_button(1)
            self.cross = self.joystick.get_button(2)
            self.square = self.joystick.get_button(3)

    def getHat(self):
        




#------------------- Initialize the joysticks  ------------------------#
joystick = pygame.joystick.Joystick(0)
joystick.init()
joystick_count = pygame.joystick.get_count()
name = joystick.get_name()
axes = joystick.get_numaxes()
hats = joystick.get_numhats()



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

    # ------------------ Highlight buttons ----------------#
    screen.blit(dpad,posdpad)
    screen.blit(bpad,posbpad)
    screen.blit(stick,(posstickL[0]+axis0*5,posstickL[1]+axis1*5))
    screen.blit(stick,(posstickR[0]+axis2*5,posstickR[1]+axis3*5))
    
    if hat[0] == 1:
        screen.blit(dpadR,posdpad)
    elif hat[0] == -1:
        screen.blit(dpadL,posdpad)
    elif hat[1] == 1:
        screen.blit(dpadU,posdpad)
    elif hat[1] == -1:
        screen.blit(dpadD,posdpad)
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
    elif joystick.get_button(1):
        screen.blit(bpadR,posbpad)
    elif joystick.get_button(2):
        screen.blit(bpadD,posbpad)
    elif joystick.get_button(3):
        screen.blit(bpadL,posbpad)
    else:
        screen.blit(bpad,posbpad)
        
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
    elif joystick.get_button(6):
        screen.blit(L2,posL)
    elif joystick.get_button(5):
        screen.blit(R1,posR)
    elif joystick.get_button(7):
        screen.blit(R2,posR)
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
