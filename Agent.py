#http://programarcadegames.com/python_examples/f.php?file=bouncing_balls.py

import random
import math
import pygame

from ColorDefinitions import *
#from Thesis.ColorDefinitions import *

SPEED=3
NUM_GOODS=2


INITIAL_MAX_NUM_GOODS=128
INITIAL_MAX_PREFERENCE=16
INITIAL_MIN_NUM_GOODS=2
INITIAL_MIN_PREFERENCE=2



SELECTED_WIDTH=2
SELECTED_COLOR=YELLOW

#change color as endowments change
class Agent:

    def update_color(self):
        scaler=self.goods["good number: 0"][0]/(self.goods["good number: 0"][0]+self.goods["good number: 1"][0])
        r=0
        g=int(255*(max(0,1-scaler)))
        b=255
        self.color=(r,g,b)


    def create_goods(self):
        #name of good, amount of good and preference of good
        for i in range(NUM_GOODS):
            self.goods["good number: "+str(len(self.goods))] =[
            random.randint(INITIAL_MIN_NUM_GOODS/2,INITIAL_MAX_NUM_GOODS/2)*2,
            random.randint(INITIAL_MIN_PREFERENCE/2,INITIAL_MAX_PREFERENCE/2)*2
            ]


    #Initialize variables
    def __init__(self,region,display,ID,radius):
        self.display = display
        self.region = pygame.Rect(region)
        self.id = ID

        self.color = BLUE
        self.radius =radius
        self.is_selected = False
        self.goods = {}
        self.box = (0,0)


        #self.__dict__.update(settings)

        self.x = random.randrange(self.radius+self.region.left,self.region.right-self.radius)
        self.y = random.randrange(self.radius+self.region.top,self.region.bottom-self.radius)
        self.on_edge_x = False
        self.on_edge_y = False

        angle = random.uniform(0,2*math.pi)
        self.change_x = math.cos(angle)*SPEED
        self.change_y = math.sin(angle)*SPEED


        self.create_goods()
        self.update_color()

    def bounce(self,other_agent):
        #calculate how to bounce the agents
        distance = self.x-other_agent.x, self.y-other_agent.y
        norm=math.sqrt(distance[0]**2+distance[1]**2)
        #possibility for fast inverse sqrt

        direction=distance[0]/norm,distance[1]/norm

        #update new direction
        self.change_x=direction[0]*SPEED
        self.change_y=direction[1]*SPEED


        other_agent.change_x=-self.change_x
        other_agent.change_y=-self.change_y

        self.move_away_from_edge()
        other_agent.move_away_from_edge()


    def move_away_from_edge(self):
        if self.on_edge_x:
            self.change_x = -self.change_x

        if self.on_edge_y:
            self.change_y = -self.change_y


    def trade(self,other_agent,num_goods_to_trade,show_trade):
        #print()
        #self.print_info()
        #other_agent.print_info()

        traded = self.margin_trade(other_agent,num_goods_to_trade)
        if show_trade:
            if traded:
                self.color=LIME_GREEN
                other_agent.color=LIME_GREEN
                #self.print_info()
                #other_agent.print_info()
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
            #print("bigger mrs")
            #print("compensation is",compensation)
            self.goods["good number: 0"][0]+=num_goods_to_trade
            other_agent.goods["good number: 0"][0]-=num_goods_to_trade

            self.goods["good number: 1"][0]-=compensation
            other_agent.goods["good number: 1"][0]+=compensation
        else:
            compensation=other_agent.marginal_rate_of_substitution_reverse()
            compensation=compensation*num_goods_to_trade
            if self.goods["good number: 0"][0]-compensation <0 or other_agent.goods["good number: 1"][0]-num_goods_to_trade <0:
                return False

            #print("smaller mrs")
            #print("compensation is",compensation)

            self.goods["good number: 0"][0]-=compensation
            other_agent.goods["good number: 0"][0]+=compensation

            self.goods["good number: 1"][0]+=num_goods_to_trade
            other_agent.goods["good number: 1"][0]-=num_goods_to_trade

        return True

    #Currently not in use
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
        self.update_color()
        self.on_edge_x=False
        self.on_edge_y=False

        # Move the center
        self.x += self.change_x
        self.y += self.change_y

        #Stay in bounds
        if self.y > self.region.bottom - self.radius or self.y < self.radius+self.region.top:
            self.change_y = -self.change_y
            self.y += self.change_y
            self.on_edge_y=True

        elif self.x > self.region.right-self.radius or self.x < self.radius+self.region.left:
            self.change_x = -self.change_x
            self.x += self.change_x
            self.on_edge_x=True


    def collision(self,other_agent):
        #http://cgp.wikidot.com/circle-to-circle-collision-detection
        dx=self.x-other_agent.x
        dy=self.y-other_agent.y
        r=self.radius+self.radius
        if(dx*dx)+(dy*dy)<r*r:
            return True
        return False

    def is_point_over_agent(self,point):
        x,y=point
        dx=self.x-x
        dy=self.y-y
        r=self.radius*self.radius
        if (dx*dx)+(dy*dy)<r:
            return True
        return False

    def get_location(self):
        return (int(round(self.x)),int(round(self.y)))



    def draw(self):
        x,y=self.get_location()
        if self.is_selected:
            pygame.draw.circle(self.display, SELECTED_COLOR, (x,y), self.radius+SELECTED_WIDTH)
        pygame.draw.circle(self.display, self.color, (x,y), self.radius)


    def remove_selected_circle(self):
        x,y=self.get_location()
        pygame.draw.circle(self.display,WHITE, (x,y), self.radius+SELECTED_WIDTH)
        self.draw()
