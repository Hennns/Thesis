#the below link used in creating this file
#http://programarcadegames.com/python_examples/f.php?file = bouncing_balls.py

import random
import math
import pygame

from ColorDefinitions import *
#from Thesis.ColorDefinitions import *

SPEED = 2

SELECTED_WIDTH = 1
SELECTED_COLOR = YELLOW

class Agent:

    def update_color(self):
        scaler = self.apples / (self.apples + self.oranges)
        r = 0
        g = int(255 * (1 - scaler))
        b = 255
        self.color = (r, g, b)

    def create_preferences(self):
        if self.preference == "normal":

            #avoid getting 0 as preference for apples
            self.pref_apples = random.random()
            while(not self.pref_apples):
                self.pref_apples = random.random()
            self.pref_oranges = 1 - self.pref_apples

            return
        elif self.preference =="linear":
            self.pref_apples = float(random.randint(self.min_preference, self.max_preference))
            self.pref_oranges = float(random.randint(self.min_preference, self.max_preference))



    #Initialize variables
    def __init__(self, region, ID, radius, preference, apples, oranges, min_preference, max_preference):

        self.region = pygame.Rect(region)
        self.id = ID
        self.color = BLUE
        self.radius = radius
        self.is_selected = False
        self.apples = apples
        self.oranges = oranges
        self.min_preference = max(1, min_preference)
        self.max_preference = max(min_preference, max_preference)

        self.preference = preference
        self.create_preferences()

        self.box = (0,0)

        self.x = random.randrange(self.radius + self.region.left, self.region.right - self.radius)
        self.y = random.randrange(self.radius + self.region.top, self.region.bottom - self.radius)

        angle = random.uniform(0, 2 * math.pi)
        self.change_x = math.cos(angle) * SPEED
        self.change_y = math.sin(angle) * SPEED

        self.update_color()

    def bounce(self, other_agent):
        #calculate how to bounce the agents
        distance = self.x - other_agent.x, self.y - other_agent.y
        norm = math.sqrt(distance[0]**2 + distance[1]**2)

        direction = distance[0]/norm, distance[1]/norm

        #update new direction
        self.change_x = direction[0] * SPEED
        self.change_y = direction[1] * SPEED

        #to the other_agent new direction is the opposite of agent
        other_agent.change_x =- self.change_x
        other_agent.change_y =- self.change_y



    def get_utility(self):
        if self.preference == "normal":
            return self.__get_utility_cobb_douglass()
        elif self.preference == "linear":
            return self.__get_utility_linear()

    def __get_utility_linear(self):
        return self.pref_apples * self.apples + self.pref_oranges*self.oranges

    def __get_utility_cobb_douglass(self):
        return self.apples ** self.pref_apples + self.oranges ** self.pref_oranges



    #Number of oranges willing to trade for 1 apple
    def get_mrs_apples(self):
        if self.preference == "normal":
            try:
                return (self.pref_apples * self.oranges) / (self.pref_oranges * self.apples)
            except ZeroDivisionError:
                return 0
        elif self.preference == "linear":
            return self.pref_apples/self.pref_oranges
        print("mrs apples bug")
        self.print_info()

    #number of apples willing to trade for 1 orange
    def get_mrs_oranges(self):
        if self.preference == "normal":
            return (self.pref_oranges * self.apples) / (self.pref_apples * self.oranges)
        elif self.preference == "linear":
            return self.pref_oranges/self.pref_apples
        print("mrs oranges bug")
        self.print_info()



    def print_info(self):
        print(" agent",self.id," apples:",self.apples ," oranges:",self.oranges)
        print(" agent",self.id," pref_apples:", self.pref_apples ," pref_oranges:",self.pref_oranges)
        print(" agent",self.id," utility ", self.get_utility())
        print("change_x", self.change_x)
        print("change_y", self.change_y)
        print(self.box)

    def move(self):
        self.update_color()

        # Move the center
        self.x += self.change_x
        self.y += self.change_y

        #Stay in bounds
        if self.y > self.region.bottom - self.radius:
            self.change_y = -abs(self.change_y)
            self.y += self.change_y

        elif self.y < self.radius + self.region.top:
            self.change_y = abs(self.change_y)
            self.y += self.change_y

        if self.x > self.region.right - self.radius:
            self.change_x = -abs(self.change_x)
            self.x += self.change_x

        elif self.x < self.radius + self.region.left:
            self.change_x = abs(self.change_x)
            self.x += self.change_x




    #http://cgp.wikidot.com/circle-to-circle-collision-detection
    def collision(self, other_agent):
        dx = self.x - other_agent.x
        dy = self.y - other_agent.y
        r = self.radius + other_agent.radius
        if(dx*dx) + (dy*dy) < r*r:
            #Dont collide when on way back to its market
            if self.returning_to_market():
                return False
            return True
        return False


    def returning_to_market(self):
        return not self.region.collidepoint((self.x, self.y))

    def is_point_over_agent(self, point):
        x,y = point
        dx = self.x - x
        dy = self.y - y
        r = self.radius * self.radius
        if (dx*dx) + (dy*dy) < r:
            return True
        return False

    def get_location(self):
        return self.x, self.y

    def __get_location_as_int(self):
        return (int(round(self.x)), int(round(self.y)))

    def draw(self, display):
        x,y = self.__get_location_as_int()
        if self.is_selected:
            pygame.draw.circle(display, SELECTED_COLOR, (x,y), self.radius+SELECTED_WIDTH)
        pygame.draw.circle(display, self.color, (x,y), self.radius)


    def remove_selected_circle(self, display):
        x,y = self.__get_location_as_int()
        pygame.draw.circle(display,WHITE, (x,y), self.radius+SELECTED_WIDTH)
        self.draw(display)
