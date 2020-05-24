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
