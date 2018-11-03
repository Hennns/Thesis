import string
import pygame
from pygame.locals import *


#https://github.com/Mekire/pygame-textbox
#modified from above source

class TextBox():
    def __init__(self,rect):
        pygame.init()
        self.rect = pygame.Rect(rect)
        self.buffer = [] #this holds the input
        self.final = None #this is the current input displayed
        self.text_size =10
        self.ACCEPTED= string.digits

        self.rendered = None
        self.render_rect = None
        self.render_area = None

        self.blink = True
        self.blink_timer = 0.0

        defaults = {
                    "active" : False,
                    "color" : pygame.Color("white"),
                    "font_color" : pygame.Color("black"),
                    "outline_color" : pygame.Color("black"),
                    "outline_width" : 2,
                    "active_color" : pygame.Color("blue"),
                    "font" : pygame.font.Font("freesansbold.ttf",self.text_size),
                    }

        self.__dict__.update(defaults)


    def execute(self):
        if not self.buffer:
            return 0
        input = int("".join(self.buffer))
        self.buffer = []
        return input

    def update(self):
        new = "".join(self.buffer)
        if new != self.final:
            self.final = new
            self.rendered = self.font.render(self.final, True, self.font_color)
            self.render_rect = self.rendered.get_rect(x=self.rect.x+2,centery=self.rect.centery)
            if self.render_rect.width > self.rect.width-6:
                offset = self.render_rect.width-(self.rect.width-6)
                self.render_area = pygame.Rect(offset,0,self.rect.width-6,self.render_rect.height)
            else:
                self.render_area = self.rendered.get_rect(topleft=(0,0))
        if pygame.time.get_ticks()-self.blink_timer > 200:
            self.blink = not self.blink
            self.blink_timer = pygame.time.get_ticks()

    def draw(self,surface):
        outline_color = self.active_color if self.active else self.outline_color
        outline = self.rect.inflate(self.outline_width*2,self.outline_width*2)
        surface.fill(outline_color,outline)
        surface.fill(self.color,self.rect)
        if self.rendered:
            surface.blit(self.rendered,self.render_rect,self.render_area)
        if self.blink and self.active:
            curse = self.render_area.copy()
            curse.topleft = self.render_rect.topleft
            surface.fill(self.font_color,(curse.right+1,curse.y,2,curse.h))
