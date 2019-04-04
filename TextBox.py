
import string
import pygame
from pygame.locals import *

from ColorDefinitions import *
#from Thesis.ColorDefinitions import *

#https://github.com/Mekire/pygame-textbox
#this file is modified from above source

class TextBox():
    def __init__(self, rect, min, max):
        pygame.init()
        self.rect = pygame.Rect(rect)
        self.buffer = [] #this holds the input
        self.final = None #this is the current input displayed
        self.text_size = 10
        self.ACCEPTED = string.digits
        self.max_buffer_len = 6
        self.min_value = min
        self.max_value = max
        self.accepted_strings = []

        self.rendered = None
        self.render_rect = None
        self.render_area = None

        self.blink = True
        self.blink_timer = 0.0

        defaults = {
                    "name" : "text",
                    "active" : False,
                    "color" : WHITE,
                    "font_color" : BLACK,
                    "outline_color" : BLACK,
                    "outline_width" : 2,
                    "active_color" : BLUE,
                    "font" : pygame.font.Font("freesansbold.ttf", self.text_size),
                    }

        self.__dict__.update(defaults)


    def execute(self):
        self.outline_color = BLACK

        if not self.buffer:
            self.outline_color = RED
            if self.accepted_strings:
                return self.accepted_strings[0]
            return self.min_value
        if self.ACCEPTED == string.digits:

            input = int("".join(self.buffer))
            #if input does not meet requirements reset to previous value
            if self.min_value > input:
                input = self.min_value
                self.outline_color = RED
            if self.max_value < input:
                input = self.max_value
                self.outline_color = RED

        else:

            input = "".join(self.buffer)
            if self.accepted_strings:
                if input not in self.accepted_strings:
                    input = self.accepted_strings[0]
                    self.outline_color = RED
        return input


    def write_to_buffer(self, input):
        if len(self.buffer) < self.max_buffer_len:
            self.buffer.append(input)

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
        if pygame.time.get_ticks() - self.blink_timer > 200:
            self.blink = not self.blink
            self.blink_timer = pygame.time.get_ticks()

    def draw(self, display):
        outline_color = self.active_color if self.active else self.outline_color
        outline = self.rect.inflate(self.outline_width*2, self.outline_width*2)
        display.fill(outline_color, outline)
        display.fill(self.color, self.rect)
        if self.rendered:
            display.blit(self.rendered, self.render_rect, self.render_area)
        if self.blink and self.active:
            curse = self.render_area.copy()
            curse.topleft = self.render_rect.topleft
            display.fill(self.font_color,(curse.right+1,curse.y,2,curse.h))
