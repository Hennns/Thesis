
import pygame

from ColorDefinitions import *
#from Thesis.ColorDefinitions import *

#Make this into pygame rect?
class button:

    def __init__(self,x,y,color,text,font,display,function):
        pygame.init()
        self.width = 110
        self.heigth = 60
        self.x = x
        self.y = y
        self.color = color
        self.text = text
        self.font = font
        self.display = display
        self.function = function

    def draw_button(self):
        pygame.draw.rect(self.display, self.color, (self.x,self.y,self.width,self.heigth))

        #empty string = false, if there is text then display it
        if self.text:
            #draw the text in the middle of the button
            textSurf, textRect = text_objects(self.text, self.font)
            textRect.center = ((self.x+(self.width/2)), (self.y+(self.heigth/2)) )
            self.display.blit(textSurf, textRect)

    def getRect(self):
        return (self.x,self.y,self.width,self.heigth)

    def execute(self):
        self.function(self)


def text_objects(text, font):
    textSurface = font.render(text, True, BLACK)
    return textSurface, textSurface.get_rect()
