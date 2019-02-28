#http://programarcadegames.com/python_examples/f.php?file = bouncing_balls.py

import random
import math
import pygame

from ColorDefinitions import *
#from Thesis.ColorDefinitions import *

SPEED = 3


INITIAL_MAX_NUM_GOODS = 256
INITIAL_MAX_PREFERENCE = 16
INITIAL_MIN_NUM_GOODS = 128
INITIAL_MIN_PREFERENCE = 2



SELECTED_WIDTH = 2
SELECTED_COLOR = YELLOW

class Agent:

    def update_color(self):
        scaler = self.apples/(self.apples+self.oranges)
        r = 0
        g = int(255*(1-scaler))
        b = 255
        self.color = (r,g,b)

    def create_preferences(self):
        if self.preference == "normal":
            self.pref_apples = float(random.randint(1,9)) / 10
            self.pref_oranges = 1-self.pref_apples
            return
        elif self.preference =="linear":
            self.pref_apples = float(random.randint(INITIAL_MIN_PREFERENCE,INITIAL_MAX_PREFERENCE))
            self.pref_oranges = float(random.randint(INITIAL_MIN_PREFERENCE,INITIAL_MAX_PREFERENCE))

    #Initialize variables
    def __init__(self,region,ID,radius,preference):

        self.region = pygame.Rect(region)
        self.id = ID
        self.color = BLUE
        self.radius = radius
        self.is_selected = False
        self.apples = 100
        self.oranges = 100

        self.preference = preference
        self.create_preferences()


        self.box = (0,0)

        self.x = random.randrange(self.radius+self.region.left,self.region.right-self.radius)
        self.y = random.randrange(self.radius+self.region.top,self.region.bottom-self.radius)
        self.on_edge_x = False
        self.on_edge_y = False

        angle = random.uniform(0,2*math.pi)
        self.change_x = math.cos(angle)*SPEED
        self.change_y = math.sin(angle)*SPEED

        self.update_color()

    def bounce(self,other_agent):
        #calculate how to bounce the agents
        distance = self.x-other_agent.x, self.y - other_agent.y
        norm= math.sqrt(distance[0]**2 + distance[1]**2)
        #possibility for fast inverse sqrt

        direction = distance[0]/norm,distance[1]/norm

        #update new direction
        self.change_x = direction[0]*SPEED
        self.change_y = direction[1]*SPEED


        other_agent.change_x =- self.change_x
        other_agent.change_y =- self.change_y

        #self.move_away_from_edge()
        #other_agent.move_away_from_edge()


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
                self.color = LIME_GREEN
                other_agent.color = LIME_GREEN
                #self.print_info()
                #other_agent.print_info()
            else:
                self.color = RED
                other_agent.color = RED






    def marginal_rate_of_substitution(self):
        return self.pref_apples/self.pref_oranges

    def marginal_rate_of_substitution_reverse(self):
        return self.pref_oranges/self.pref_apples



    def get_utility(self):
        if self.preference == "normal":
            return self.__get_utility_cobb_douglass()
        elif self.preference == "linear":
            return self.__get_utility_linear()

    #linear, this can be a single return statement
    def __get_utility_linear(self):
        utility = 0
        utility += self.pref_apples*self.apples + self.pref_oranges*self.oranges
        return utility

    def __get_utility_cobb_douglass(self):
        #if isinstance( self.apples ** self.pref_apples + self.oranges ** self.pref_oranges, complex):
        #    self.print_info()
        return self.apples ** self.pref_apples + self.oranges ** self.pref_oranges



    #Number of oranges willing to trade for 1 apple
    def get_mrs_apples(self):
        if self.preference == "normal":
            return (self.pref_apples * self.oranges) / (self.pref_oranges * self.apples)
        elif self.preference == "linear":
            return self.pref_apples/self.pref_oranges
        print("mrs apples bug")
        self.print_info()

    #number of apples willing to trade for 1 orange
    def get_mrs_oranges(self):
        if self.preference == "normal":
            return (self.pref_oranges * self.apples) /(self.pref_apples * self.oranges)
        elif self.preference == "linear":
            return self.pref_oranges/self.pref_apples
        print("mrs oranges bug")
        self.print_info()



    def print_info(self):
        print(" agent",self.id," apples:",self.apples ," oranges:",self.oranges)
        print(" agent",self.id," pref_apples:",self.pref_apples ," pref_oranges:",self.pref_oranges)
        print(" agent",self.id," utility ",self.get_utility_cobb_douglass())

    def move(self):
        self.update_color()
        self.on_edge_x = False
        self.on_edge_y = False

        # Move the center
        self.x += self.change_x
        self.y += self.change_y

        #Stay in bounds
        if self.y > self.region.bottom - self.radius:
            self.change_y = -abs(self.change_y)
            self.y += self.change_y
            self.on_edge_y = True

        elif self.y < self.radius+self.region.top:
            self.change_y = abs(self.change_y)
            self.y += self.change_y
            self.on_edge_y = True

        if self.x > self.region.right-self.radius:
            self.change_x = -abs(self.change_x)
            self.x += self.change_x
            self.on_edge_x = True

        elif self.x < self.radius+self.region.left:
            self.change_x = abs(self.change_x)
            self.x += self.change_x
            self.on_edge_x = True




    #Dont collide when on way back to its market
    def collision(self,other_agent):

        #http://cgp.wikidot.com/circle-to-circle-collision-detection
        dx = self.x - other_agent.x
        dy = self.y - other_agent.y
        r = self.radius + other_agent.radius
        if(dx*dx) + (dy*dy) < r*r:
            if self.returning_to_market():
                return False
            return True
        return False



    def returning_to_market(self):
        return not self.region.collidepoint((self.x,self.y))

    def is_point_over_agent(self,point):
        x,y = point
        dx = self.x-x
        dy = self.y-y
        r = self.radius*self.radius
        if (dx*dx)+(dy*dy)<r:
            return True
        return False

    def get_location(self):
        return (int(round(self.x)),int(round(self.y)))



    def draw(self,display):
        x,y = self.get_location()
        if self.is_selected:
            pygame.draw.circle(display, SELECTED_COLOR, (x,y), self.radius+SELECTED_WIDTH)
        pygame.draw.circle(display, self.color, (x,y), self.radius)


    def remove_selected_circle(self,display):
        x,y = self.get_location()
        pygame.draw.circle(display,WHITE, (x,y), self.radius+SELECTED_WIDTH)
        self.draw()
