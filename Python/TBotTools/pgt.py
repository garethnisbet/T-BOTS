import pygame

class TextPrint(object):
    '''Text positioning class for PyGame'''
    def __init__(self, textcolour, size = 15):
        self.reset()
        self.textcolour = textcolour
        self.fontsize = size
        self.font = pygame.font.Font(None, self.fontsize)

    def tprint(self, screen, textString):
        textBitmap = self.font.render(textString, True, self.textcolour)
        screen.blit(textBitmap, (self.x, self.y))
        self.y += self.line_height
        
    def setlineheight(self, line_height):
        self.line_height = line_height

    def reset(self):
        self.x = 10
        self.y = 10
        self.line_height = 15

    def indent(self):
        self.x += 10
        
    def setfontsize(self,size):
        self.fontsize = size
        self.font = pygame.font.Font(None, self.fontsize)
        
    def unindent(self):
        self.x -= 10
        
    def abspos(self,screen, textString, pos):
        self.x = pos[0]
        self.y = pos[1]
        textBitmap = self.font.render(textString, True, self.textcolour)
        screen.blit(textBitmap, (self.x, self.y))
        self.y += self.line_height
        
    def setColour(self, textcolour):
        self.textcolour = textcolour



class SliderBar(object):
    '''Creates interactive slide bars.'''
    def __init__(self,screen, pos, pos2, length, scale, thickness,
                colour1, colour2, tolerence = []):
        self.screen = screen
        self.pos = pos
        self.pos2 = [pos[0]+int(pos2*length/scale), pos[1]]
        self.length = length
        self.scale = scale
        if thickness % 2 == 0:
            thickness += 1
        self.thickness = thickness
        self.colour1 = colour1
        self.colour2 = colour2
        self.pos_flag = 0
        if tolerence == []:
            self.tolerence = thickness
        else:
            self.tolerence = tolerence

    def set_pos(self,newpos):
        self.pos = newpos
    def set_pos2(self,newpos2):
        self.pos2 = [self.pos[0]+int(newpos2*self.length/self.scale), self.pos[1]]
    def set_length(self,newlength):
        self.lenght = newlength
    def set_thickness(self,newthickness):
        self.thickness = newthickness
    def get_mouse_and_set(self):
        pygame.event.get()
        mx,my = pygame.mouse.get_pos()
        c1, c2, c3 =  pygame.mouse.get_pressed()
        if (
            c1 == 1  and mx > self.pos[0] and mx < self.pos[0]+self.length
            and my > self.pos[1]-self.tolerence and my < self.pos[1]+self.tolerence
           ):
            self.pos2 = [mx, self.pos2[1]]
        pygame.draw.line(self.screen, self.colour1, self.pos, (self.pos[0]+self.length,self.pos[1]), self.thickness)
        pygame.gfxdraw.aacircle(self.screen, self.pos[0],self.pos[1], int(self.thickness/2), self.colour1)
        pygame.gfxdraw.aacircle(self.screen, self.pos[0],self.pos[1], int(self.thickness/2)-1, self.colour1)
        pygame.draw.circle(self.screen, self.colour1, (self.pos[0], self.pos[1]), int(self.thickness/2))
        pygame.gfxdraw.aacircle(self.screen, self.pos[0]+self.length,self.pos[1], int(self.thickness/2)-1, self.colour1)
        pygame.gfxdraw.aacircle(self.screen, self.pos[0]+self.length,self.pos[1], int(self.thickness/2), self.colour1)
        pygame.draw.circle(self.screen, self.colour1, (self.pos[0]+self.length, self.pos[1]), int(self.thickness/2))
        pygame.draw.circle(self.screen, self.colour2, self.pos2, int(self.thickness/1.5))
        if self.pos2[0] <= self.pos[0]+self.tolerence:
            self.pos2[0] =  self.pos[0]
        if self.pos2[0] >= (self.pos[0]+self.length)-self.tolerence:
            self.pos2[0] =  self.pos[0]+self.length
        pygame.gfxdraw.filled_circle(self.screen, self.pos2[0],self.pos2[1], int(self.thickness/1.5)-1, self.colour2)
        pygame.gfxdraw.filled_circle(self.screen, self.pos2[0],self.pos2[1], int(self.thickness/1.5), self.colour2)
        pygame.gfxdraw.aacircle(self.screen, self.pos2[0],self.pos2[1], int(self.thickness/1.5), self.colour2)
        return float((self.pos2[0]-self.pos[0])*self.scale/self.length)

    
    
    
    
    
