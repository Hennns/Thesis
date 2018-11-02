#http://programarcadegames.com/python_examples/f.php?file=bouncing_balls.py

#from random import uniform
import random
import math
import pygame

AGENT_COLOR=(100,100,100)
AGENT_SPEED=3
AGENT_GOODS_NUM=2
AGENT_RADIUS =20

MAX_NUM_GOODS_TO_TRADE=5
INITIAL_MAX_NUM_GOODS=200
INITIAL_MAX_PREFERENCE=10
INITIAL_MIN_NUM_GOODS=0
INITIAL_MIN_PREFERENCE=1

LIME_GREEN=(50,205,50)
RED = (255,0,0)

SELECTED_WIDTH=2
SELECTED_COLOR=RED

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
        self.goods={}

        #name of good, amount of good and preference of good
        for i in range(AGENT_GOODS_NUM):
            self.goods["good number: "+str(len(self.goods))] =[random.randint(INITIAL_MIN_NUM_GOODS,INITIAL_MAX_NUM_GOODS), random.randint(INITIAL_MIN_PREFERENCE,INITIAL_MAX_PREFERENCE)]
            #preference should be between 0 and 1 maybe


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
        price =self.cobb_douglas_two_goods(other_agent)


        if price is not 0:
            print()
            print("Before trade")
            print("first agent info ",self.goods)
            print("second agent info",other_agent.goods)
            print("first agent utility ",self.get_utility())
            print("other agent utility ",other_agent.get_utility())
            print("The price is",price)

            self.color=LIME_GREEN
            other_agent.color=LIME_GREEN

            if price <0.5:
                self.goods["good number: 0"][0]+=1
                self.goods["good number: 1"][0]-=price

                other_agent.goods["good number: 0"][0]-=1
                other_agent.goods["good number: 1"][0]+=price
            else:
                self.goods["good number: 1"][0]+=1
                self.goods["good number: 0"][0]-=price

                other_agent.goods["good number: 1"][0]-=1
                other_agent.goods["good number: 0"][0]+=price
            print("after trade")
            print("first agent info ",self.goods)
            print("second agent info",other_agent.goods)
            print("first agent utility ",self.get_utility())
            print("other agent utility ",other_agent.get_utility())
        else:
            self.color=RED
            other_agent.color=RED


    def get_utility(self):
        utility=0
        for good in self.goods:
            #utility for a good is number of that good raised to the power of the preference
            #utility+=pow(self.goods[good][0],self.goods[good][1])
            utility+=self.goods[good][0]*self.goods[good][1]
        return utility



#https://github.com/cliffclive/econsim/blob/master/econ_sim/econ_sim/transactions.py
#http://econometheus.blogspot.com/2014/02/measuring-supply-and-demand-in.html
    def cobb_douglas_two_goods(self, other_agent):
#TODO make it work with variable number of goods
        total_goods ={}
        for good in self.goods:
            total_goods[good]= self.goods[good][0]+other_agent.goods[good][0]

        # Useful constants for the following calculations
        alphaX = self.goods["good number: 0"][1] / (self.goods["good number: 0"][1] + self.goods["good number: 1"][1])
        betaX  = self.goods["good number: 1"][1] / (self.goods["good number: 0"][1] + self.goods["good number: 1"][1])
        alphaY = other_agent.goods["good number: 0"][1] / (other_agent.goods["good number: 0"][1] + other_agent.goods["good number: 1"][1])
        betaY  = other_agent.goods["good number: 1"][1] / (other_agent.goods["good number: 0"][1] + other_agent.goods["good number: 1"][1])

        # Equilibrium price of good 1 relative to good 2
        price = (self.goods["good number: 1"][0] * alphaX +other_agent.goods["good number: 1"][0] * alphaY) / (self.goods["good number: 0"][0] * betaX + self.goods["good number: 0"][0] * betaY)

        #allocation_x = self.demand(price)
        #allocation_y = (total_goods["good number: 0"] - allocation_x[0], total_goods["good number: 1"] - allocation_x[1])

        #return (allocation_x, allocation_y, price)
        return price


    def demand(self, price):
        alpha = self.goods["good number: 0"][1] / (self.goods["good number: 0"][1] + self.goods["good number: 1"][1])
        quantity1 = alpha * (price * self.goods["good number: 0"][0] + self.goods["good number: 0"][0]) / price
        quantity2 = price * quantity1 * self.goods["good number: 1"][1] / self.goods["good number: 0"][1]
        return (quantity1, quantity2)

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
        if(dx*dx)+(dy*dy)<r*r:
            return True
        return False

    def is_point_over_agent(self,point):
        x,y=point
        dx=self.x-x
        dy=self.y-y
        r=AGENT_RADIUS*AGENT_RADIUS
        if (dx*dx)+(dy*dy)<r:
            return True
        return False


    def draw(self):
        #the x and y cordinates are kept as floats, but to draw they need to be int

        if self.is_selected:
            pygame.draw.circle(self.display, SELECTED_COLOR, [int(round(self.x)), int(round(self.y))], AGENT_RADIUS+SELECTED_WIDTH)
        pygame.draw.circle(self.display, self.color, [int(round(self.x)), int(round(self.y))], AGENT_RADIUS)
