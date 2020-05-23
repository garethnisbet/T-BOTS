import pygame

class TextPrint(object):
    '''Text positioning class for PyGame'''
    def __init__(self, textcolour):
        self.reset()
        self.textcolour = textcolour
        self.font = pygame.font.Font(None, 15)

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
