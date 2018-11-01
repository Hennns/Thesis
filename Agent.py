#http://programarcadegames.com/python_examples/f.php?file=bouncing_balls.py



#from random import uniform
import random
import math
import pygame


AGENT_COLOR=(100,100,100)
AGENT_SPEED=3
AGENT_GOODS_NUM=2
AGENT_RADIUS =20
LIME_GREEN=(50,205,50)
RED = (255,0,0)


class Agent:

    #Initialize variables
    def __init__(self,y_adjustment,display):
        self.display = display
        self.display_width,self.display_heigth= display.get_size()

        self.y_adjustment=y_adjustment
        self.x =random.randrange(AGENT_RADIUS,self.display_width-AGENT_RADIUS)
        self.y =random.randrange(AGENT_RADIUS+self.y_adjustment,self.display_heigth-AGENT_RADIUS)

        angle = random.uniform(0,2*math.pi)
        self.change_x =math.cos(angle)*AGENT_SPEED
        self.change_y =math.sin(angle)*AGENT_SPEED

        self.color = AGENT_COLOR
        self.is_selected=False
        self.goods={} #first value is good number (key), second is preference of that good

        for i in range(AGENT_GOODS_NUM):
            self.goods["good number: "+str(len(self.goods))] =random.randint(0,100)


    def bounce(self,other_agent):
        #calculate how to bounce the agents
        #TODO sqrt is bad, get rid of it
        distance = self.x-other_agent.x, self.y-other_agent.y
        norm=math.sqrt(distance[0]**2+distance[1]**2)
        direction=distance[0]/norm,distance[1]/norm

        #update new direction
        self.change_x=direction[0]*AGENT_SPEED
        self.change_y=direction[1]*AGENT_SPEED

        other_agent.change_x=self.change_x*-1
        other_agent.change_y=self.change_y*-1

    def trade(self,other_agent):
        print("first agent have ",self.goods)
        print("second agent have",other_agent.goods)
        willing_to_trade =bool(random.getrandbits(1))
        if willing_to_trade:
            self.color=LIME_GREEN
            other_agent.color=LIME_GREEN
        else:
            self.color=RED
            other_agent.color=RED


    def move(self):
        self.color=AGENT_COLOR

        # Move the center
        self.x += self.change_x
        self.y += self.change_y

        #Stay in bounds
        if self.y > self.display_heigth - AGENT_RADIUS or self.y < AGENT_RADIUS+self.y_adjustment:
            self.change_y *= -1
            self.y+=self.change_y
        #TODO if?
        elif self.x > self.display_width-AGENT_RADIUS or self.x < AGENT_RADIUS:
            self.change_x *= -1
            self.x+=self.change_x


    def collision(self,other_agent):
        #http://cgp.wikidot.com/circle-to-circle-collision-detection
        dx=self.x-other_agent.x
        dy=self.y-other_agent.y
        r=AGENT_RADIUS+AGENT_RADIUS
        if((dx*dx)+(dy*dy)<r*r):
            return True
        return False


    def draw(self):
        #the x and y cordinates are kept as floats, but to draw they need to be int
        pygame.draw.circle(self.display, self.color, [int(round(self.x)), int(round(self.y))], AGENT_RADIUS)
