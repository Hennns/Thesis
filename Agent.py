#http://programarcadegames.com/python_examples/f.php?file=bouncing_balls.py

import random
import math
import pygame

#import ColorDefinitions *
from Thesis.ColorDefinitions import *

COLOR=(100,100,100)
SPEED=3
NUM_GOODS=2
RADIUS =20

INITIAL_MAX_NUM_GOODS=50
INITIAL_MAX_PREFERENCE=10
INITIAL_MIN_NUM_GOODS=0
INITIAL_MIN_PREFERENCE=2



SELECTED_WIDTH=2
SELECTED_COLOR=DARK_YELLOW

#change color as endowments change
class Agent:

    #Initialize variables
    def __init__(self,y_adjustment,display,ID):
        self.display = display
        self.display_width,self.display_heigth= display.get_size()

        self.y_adjustment=y_adjustment
        self.x =random.randrange(RADIUS,self.display_width-RADIUS)
        self.y =random.randrange(RADIUS+self.y_adjustment,self.display_heigth-RADIUS)

        angle = random.uniform(0,2*math.pi)
        self.change_x =math.cos(angle)*SPEED
        self.change_y =math.sin(angle)*SPEED

        self.color = COLOR
        self.is_selected=False
        self.id=ID
        self.goods={}

        #name of good, amount of good and preference of good
        for i in range(NUM_GOODS):
            self.goods["good number: "+str(len(self.goods))] =[
            random.randint(INITIAL_MIN_NUM_GOODS/2,INITIAL_MAX_NUM_GOODS/2)*2,
            random.randint(INITIAL_MIN_PREFERENCE/2,INITIAL_MAX_PREFERENCE/2)*2
            ]
            #preference should be between 0 and 1 maybe


    def bounce(self,other_agent):
        #calculate how to bounce the agents
        #TODO sqrt is bad, get rid of it
        distance = self.x-other_agent.x, self.y-other_agent.y
        norm=math.sqrt(distance[0]**2+distance[1]**2)
        #Fast inverse sqrt
        direction=distance[0]/norm,distance[1]/norm

        #update new direction
        self.change_x=direction[0]*SPEED
        self.change_y=direction[1]*SPEED

        other_agent.change_x=self.change_x*-1
        other_agent.change_y=self.change_y*-1



    def trade(self,other_agent,num_goods_to_trade):
        print()
        self.print_info()
        other_agent.print_info()

        if self.margin_trade(other_agent,num_goods_to_trade):
            self.color=LIME_GREEN
            other_agent.color=LIME_GREEN
            self.print_info()
            other_agent.print_info()
        else:
            self.color=RED
            other_agent.color=RED




    #Trade on the margin of the other_agent
    def margin_trade(self,other_agent,num_goods_to_trade):

        if self.marginal_rate_of_substitution() > other_agent.marginal_rate_of_substitution():
            compensation=other_agent.marginal_rate_of_substitution()
            compensation=compensation*num_goods_to_trade
            if other_agent.goods["good number: 0"][0]-num_goods_to_trade <0 or self.goods["good number: 1"][0]-compensation <0:
                return False
            print("bigger mrs")
            print("compensation is",compensation)
            self.goods["good number: 0"][0]+=num_goods_to_trade
            other_agent.goods["good number: 0"][0]-=num_goods_to_trade

            self.goods["good number: 1"][0]-=compensation
            other_agent.goods["good number: 1"][0]+=compensation
        else:
            compensation=other_agent.marginal_rate_of_substitution_reverse()
            compensation=compensation*num_goods_to_trade
            if self.goods["good number: 0"][0]-num_goods_to_trade <0 or other_agent.goods["good number: 1"][0]-compensation <0:
                return False

            print("smaller mrs")
            print("compensation is",compensation)

            self.goods["good number: 0"][0]-=compensation
            other_agent.goods["good number: 0"][0]+=compensation

            self.goods["good number: 1"][0]+=num_goods_to_trade
            other_agent.goods["good number: 1"][0]-=num_goods_to_trade

        return True


    def middle_trade(self,other_agent,num_goods_to_trade):
        if margin_trade(self,other_agent,num_goods_to_trade/2):
            self.color=LIME_GREEN
        else:
            self.color=RED
        if margin_trade(other_agent,self,num_goods_to_trade/2):
            other_agent.color=LIME_GREEN
        else:
            other_agent.color=RED


    def marginal_rate_of_substitution(self):
        return self.goods["good number: 0"][1]/self.goods["good number: 1"][1]

    def marginal_rate_of_substitution_reverse(self):
        return self.goods["good number: 1"][1]/self.goods["good number: 0"][1]


    def get_utility(self):
        utility=0
        for good in self.goods:
            utility+=self.goods[good][0]*self.goods[good][1]
        return utility

    def print_info(self):
        print(" agent",self.id," info ",self.goods)
        print(" agent",self.id," utility ",self.get_utility())

    def move(self):
        self.color=COLOR

        # Move the center
        self.x += self.change_x
        self.y += self.change_y

        #Stay in bounds
        if self.y > self.display_heigth - RADIUS or self.y < RADIUS+self.y_adjustment:
            self.change_y *= -1
            self.y+=self.change_y

        elif self.x > self.display_width-RADIUS or self.x < RADIUS:
            self.change_x *= -1
            self.x+=self.change_x


    def collision(self,other_agent):
        #http://cgp.wikidot.com/circle-to-circle-collision-detection
        dx=self.x-other_agent.x
        dy=self.y-other_agent.y
        r=RADIUS+RADIUS
        if(dx*dx)+(dy*dy)<r*r:
            return True
        return False

    def is_point_over_agent(self,point):
        x,y=point
        dx=self.x-x
        dy=self.y-y
        r=RADIUS*RADIUS
        if (dx*dx)+(dy*dy)<r:
            return True
        return False


    def draw(self):
        #the x and y cordinates are kept as floats, but to draw they need to be int
        if self.is_selected:
            pygame.draw.circle(self.display, SELECTED_COLOR, [int(round(self.x)), int(round(self.y))], RADIUS+SELECTED_WIDTH)
        pygame.draw.circle(self.display, self.color, [int(round(self.x)), int(round(self.y))], RADIUS)

    def remove_selected_circle(self):
        pygame.draw.circle(self.display,WHITE, [int(round(self.x)), int(round(self.y))], RADIUS+SELECTED_WIDTH)
        self.draw()
