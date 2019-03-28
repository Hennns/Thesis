
# In[1]:

import pygame
import pickle
import string
from collections import deque
import datetime
import random

#Make window appear centered
import os
os.environ['SDL_VIDEO_CENTERED'] = '1'

"""
#Do this when running via atom
from Thesis import Agent
from Thesis import TextBox
from Thesis import Button
from Thesis.ColorDefinitions import *

"""
#Do this when running from command line
import Agent
import Button
import TextBox
import Market
import Graph
from ColorDefinitions import *


#Sources
#http://usingpython.com/pygame-intro/
#https://pythonprogramming.net/pygame-python-3-part-1-intro/

#Global things
market_list = [[]]
button_list = []
setting_box_list = []
default_box_list = []


settings = {
            "rows": 1,
            "columns": 1,
            "space": 20,
            "update interval": 10,
            "visible data points": 2000,
            "speed multiplier": 1,
            "region_mode": True,
            "avoid overlapping agents": True,
            "graph": "line",
            "wait": True,
            "change settings": False
            }

market_settings = {
            "radius" : 10,
            "show trade": 0,
            "random_num_goods": True,
            "preference": "normal",
            "apples": 50,
            "oranges": 50,
            "apple preference": 0,
            "orange preference": 0
            }

#possible preferences:
#normal (cobb)
#Perfect Substitutes (linear)


# In[2]:
WIDTH = 1400
HEIGHT = 800
TITLE = "Exchange Economy Simulation"

BUTTON_WIDTH = 110
BUTTON_HEIGHT = 60
BUTTON_X = 20
BUTTON_Y = 20
BUTTON_SPACE = 10

#Border of agents
TOP_BORDER = BUTTON_Y + BUTTON_HEIGHT
BOTTOM_BORDER = HEIGHT + settings["space"]
RIGTH_BORDER = WIDTH - 500
LEFT_BORDER = 0


region_width = RIGTH_BORDER - LEFT_BORDER
region_height = BOTTOM_BORDER - TOP_BORDER
SINGLE_MARKET_BORDER = (LEFT_BORDER, TOP_BORDER, region_width, region_height)

num_agents = 0
num_time_steps = 1
initial_utility = 1



#Documnetation for deque
#https://docs.python.org/2/library/collections.html#collections.deque
utility_tracker = deque(maxlen = settings["visible data points"])
time_step_num_tracker = deque(maxlen = settings["visible data points"])



#devides a pygame.Rect into multiple smaller Rects
def divide_rect(rectangle, rows, columns, space):
    height = int(rectangle.height/rows)
    width = int(rectangle.width/columns)
    r_y = rectangle.y
    r_x = rectangle.x

    r_list = [[0 for x in range(columns)] for y in range(rows)]

    for row in range(rows):
        for c in range(columns):
            r_list[row][c] = pygame.Rect(r_x+(width*c), r_y+(height*row), width-space, height-space)
    return r_list



#Set number of bins (used to do collison calculations faster)
BIN_NUM_ROWS = 45
BIN_NUM_COLUMNS = 45

BOX_MAP = divide_rect(pygame.Rect(LEFT_BORDER, TOP_BORDER, RIGTH_BORDER-LEFT_BORDER, BOTTOM_BORDER-TOP_BORDER), BIN_NUM_ROWS,BIN_NUM_COLUMNS, 0)

#each row+colum represents a box and contains a list of agents in that box
box_tracker = [([[]] * BIN_NUM_COLUMNS) for row in range(BIN_NUM_COLUMNS)]




# In[3]:
#give graph as varaible?
def graph_type_function(button):
    global settings
    if settings["graph"] == "Allocation":
        settings["graph"] = "line"
    elif settings["graph"] == "line":
        settings["graph"] = "price"
    else:
        settings["graph"] = "Allocation"


def load_function(button):
    global market_list
    global settings
    global time_step_num_tracker
    global utility_tracker

    settings["wait"] = True
    button.display.fill(WHITE)
    try:
        load_list = pickle.load(open("save.p","rb"))
        market_list = load_list[0]
        settings = load_list[1]
        time_step_num_tracker = load_list[2]
        utility_tracker = load_list[3]
    except FileNotFoundError:
        print("saved file not fond")

    draw_agents(button.display)

def save_function(button):
    global market_list
    global settings
    global time_step_num_tracker
    global utility_tracker

    dump_list = [market_list, settings, time_step_num_tracker, utility_tracker]
    pickle.dump(dump_list, open("save.p", "wb"))



def get_num_markets_selected(market_list):
    num_markets_selected = 0
    for row in range(len(market_list)):
        for column in range(len(market_list[row])):
            if market_list[row][column].is_selected:
                num_markets_selected += 1
    return num_markets_selected

def settings_function(button):
    global button_list
    global market_list
    global setting_box_list
    global settings

    settings["change settings"] = not settings["change settings"]
    button.display.fill(WHITE)

    button_list = []
    if settings["change settings"]:
        button.text = "Apply"
        return_button = Button.button(BUTTON_X+4*(BUTTON_WIDTH+BUTTON_SPACE),BUTTON_Y,GREEN,"Return",button.font,button.display,return_function, BUTTON_WIDTH, BUTTON_HEIGHT)
        button_list.append(button)
        button_list.append(return_button)

    else:
        update_markets = False
        for input_box in setting_box_list:
            if input_box.name == "rows" or input_box.name == "columns":
                if not settings[input_box.name] == input_box.get_input():
                    update_markets = True
            settings[input_box.name] = input_box.get_input()
        if update_markets:
            initialize_market()

        #MARKET PART
        if get_num_markets_selected(market_list) == 0:
            for row in range(len(market_list)):
                for column in range(len(market_list[row])):
                    for input_box in default_box_list:
                        market_list[row][column].settings[input_box.name] = input_box.get_input()
        #else update only the settings of the selected markets
        else:
            for row in range(len(market_list)):
                for column in range(len(market_list[row])):
                    if market_list[row][column].is_selected:
                        for input_box in default_box_list:
                            market_list[row][column].settings[input_box.name] = input_box.get_input()
                            #It's possible to update settings for agents this way
                            #possible future work


        draw_agents(button.display)
        initialize_button_list(button.display, button.font)
        settings["wait"] = True




def reset_function(button):
    global settings
    settings["wait"] = True
    clear()
    button.display.fill(WHITE)
    initialize_market()

def return_function(button):
    global settings
    global button_list
    global setting_box_list

    settings["change settings"] = False
    button_list = []
    initialize_button_list(button.display, button.font)
    button.display.fill(WHITE)
    draw_agents(button.display)


    for box in setting_box_list:
        try:
            box.buffer = [str(i) for i in str(settings[box.name])]
        except KeyError:
            print("no key for setting_box", box.name)
            print(box)
            continue


def pause_function(button):
    global settings
    settings["wait"] = not settings["wait"]


def step_function(button):
    global settings
    settings["wait"] = True
    button.color = LIME_GREEN
    button.display.fill(WHITE)
    move_agents()
    draw_agents(button.display)
    #draw graphs here
    #TODO

def region_function(button):
    global market_list
    global SINGLE_MARKET_BORDER
    global settings
    settings["region_mode"] = not settings["region_mode"]

    if settings["region_mode"]:
        button.text = "Borders on"
        button.color = GREEN

        for row in range(len(market_list)):
            for column in range(len(market_list[row])):
                for agent in market_list[row][column].agents:
                    agent.region = market_list[row][column].region
    else:
        button.text = "Borders off"
        button.color = RED
        new_region = divide_rect(pygame.Rect(SINGLE_MARKET_BORDER), 1, 1, settings["space"])[0][0]

        for row in range(len(market_list)):
            for column in range(len(market_list[row])):
                for agent in market_list[row][column].agents:
                    agent.region = new_region


#https://www.saltycrane.com/blog/2008/06/how-to-get-current-date-and-time-in/
#Used to get current time
def screenshot_function(button):
    now = datetime.datetime.now()
    current_time = str(now.year) + "-" + str(now.month) + "-" + str(now.day) + " " +str(now.hour) + "h" +str(now.minute)+ "m" +str(now.second) +"s"
    pygame.image.save(button.display,current_time+" screenshot.jpg")



def clear():
    global market_list
    global initial_utility
    global num_agents
    global utility_tracker
    global time_step_num_tracker

    initial_utility = 1
    num_agents = 0
    market_list = [[]]
    utility_tracker.clear()
    time_step_num_tracker.clear()


#If the current box is unknown, finds the correct box
def set_box(agent):
    x,y = agent.get_location()
    for row in range(len(BOX_MAP)):
        for col in range(len(BOX_MAP[row])):
            if BOX_MAP[row][col].collidepoint(x,y):
                return (row,col)

    #This should never happen
    for row in range(len(BOX_MAP)):
        for col in range(len(BOX_MAP[row])):
            print(BOX_MAP[row][col])
    agent.print_info()
    print("box not found")
    return (0,0)

#the ask for forgivness approach tested to be faster than ask for permission
def get_nearby_agents(current_r, current_c):
    global box_tracker
    nearby_agents = []
    for r in range(-1,2):
        for c in range(-1,2):
            try:
                nearby_agents.extend(box_tracker[current_r-r][current_c-c])
            except IndexError:
                continue
    return nearby_agents


def get_nearby_boxes(current_r,current_c):
    global BIN_NUM_ROWS
    nearby_boxes = []
    for row in range(-1,2):
        if 0 <= current_r-row <BIN_NUM_ROWS:
            for col in range(-1,2):
                if 0<=current_c-col <BIN_NUM_COLUMNS and not row==col==0:
                    nearby_boxes.append((current_r-row,current_c-col))
    return nearby_boxes


#thie needs some clean up!! idea is to use direction of agent to speed up calculations
#finds the new box based on the previous box
def find_new_box(agent):
    global box_tracker

    r,c = agent.box
    x,y = agent.get_location()

    #Check the old box first, since the agent is most likely there
    if BOX_MAP[r][c].collidepoint(x,y):
       box_tracker[r][c].append(agent)
       return


    #the loop can be unrolled and speed up here
    for row,col in get_nearby_boxes(r,c):
        if BOX_MAP[row][col].collidepoint(x,y):
            box_tracker[row][col].append(agent)
            agent.box = (row,col)
            #print("new box is ",row,col)
            return
    #This should never happen, but if it does try to set_box again
    print("could not find new box")
    agent.box = set_box(agent)

# In[5]:


def move_agents():
    global box_tracker
    global market_list
    global num_time_steps
    global utility_tracker
    global time_step_num_tracker
    global setting_box_list

    box_tracker= [([[]] * BIN_NUM_COLUMNS) for row in range(BIN_NUM_ROWS)]
    num_time_steps += 1
    update = num_time_steps % settings["update interval"] == 0

    if update:
        utility_tracker.append(get_total_utility(market_list))
        time_step_num_tracker.append(num_time_steps)

    for row in range(len(market_list)):
        for column in range(len(market_list[row])):
            for agent in market_list[row][column].agents:
                r,c = agent.box
                agent.move()
                for other_agent in get_nearby_agents(r,c):
                    if agent.collision(other_agent):
                        agent.bounce(other_agent)
                        market_list[row][column].trade(agent, other_agent)
                        """
                        Seems like this is unneccesarily due to code in market.py
                        #Randomize which agant is on which side in the trade
                        if random.getrandbits(1):
                            market_list[row][column].trade(agent, other_agent)
                        else:
                            market_list[row][column].trade(other_agent, agent)
                        """
                        #only collide with one agent each timesetep
                        break
                find_new_box(agent)
            if update:
                market_list[row][column].utility_tracker.append(market_list[row][column].get_utility())
                market_list[row][column].price_tracker.append(market_list[row][column].get_price())
                market_list[row][column].price = 0
                market_list[row][column].num_trades = 1

def get_total_utility(market_list):
    utility = 0
    for row in range(len(market_list)):
        for column in range(len(market_list[row])):
            utility += market_list[row][column].get_utility()
    return utility

def draw_agents(display):
    for row in range(len(market_list)):
        for column in range(len(market_list[row])):
            for agent in market_list[row][column].agents:
                agent.draw(display)

def draw_markets(display):
    global market_list
    for row in range(len(market_list)):
        for column in range(len(market_list[row])):
            pygame.draw.rect(display, market_list[row][column].color, market_list[row][column].region, 1)


def text_objects(text, font):
    textSurface = font.render(text, True, BLACK)
    return textSurface, textSurface.get_rect()

def on_top_of_other_agent(agent):
    r,c = agent.box
    for other_agent in get_nearby_agents(r, c):
        if agent.collision(other_agent):
            #print("agent on top of other agent at spawn")
            return True
    return False


def new_agent_in_region(display, region, radius, preference, apples, oranges, overlapp, pref_a, pref_o):
    global initial_utility
    global num_agents

    for i in range(20):
        agent = Agent.Agent(region, num_agents+1, radius, preference, apples, oranges)
        agent.box = set_box(agent)

        if not overlapp or not on_top_of_other_agent(agent):
            find_new_box(agent)
            agent.draw(display)
            initial_utility += agent.get_utility()
            num_agents += 1

            if pref_a > 0 and pref_o > 0:
                agent.pref_apples = pref_a
                agent.pref_oranges = pref_o

            return agent
    return None


def create_many_agents(display, market_list, settings, num):

    overlapp = settings["avoid overlapping agents"]
    for row in range(len(market_list)):
        for column in range(len(market_list[row])):
            region = market_list[row][column].region
            radius = market_list[row][column].settings["radius"]
            preference = market_list[row][column].settings["preference"]

            pref_a = market_list[row][column].settings["apple preference"]
            pref_o = market_list[row][column].settings["orange preference"]

            for i in range(num):
                apples = market_list[row][column].settings["apples"]
                oranges = market_list[row][column].settings["oranges"]
                if apples < 1:
                    apples = random.randint(10,100)
                if oranges < 1:
                    oranges = random.randint(10,100)

                agent = new_agent_in_region(display, region, radius, preference, apples, oranges, overlapp, pref_a, pref_o)
                if agent is not None:
                    market_list[row][column].agents.append(agent)
                    if not radius == agent.radius:
                        print("radius should be:",radius)
                        print("radius is ",agent.radius)
                        print("market",row,column)

def initialize_button_list(display, font):
    global button_list

    names = ["Start", "Reset!", "Step", "Borders on", "Settings", "Screenshot",
     "Save", "Load", "Next Graph"]
    functions = [pause_function, reset_function, step_function, region_function,
     settings_function, screenshot_function, save_function, load_function, graph_type_function]

    #The input box is at the BUTTON_X spot, so that is skipped (by adding x)
    x = BUTTON_WIDTH + BUTTON_SPACE
    for i in range(len(names)):
        button = Button.button(BUTTON_X+ (i+1)*x, BUTTON_Y, GREEN, names[i], font, display, functions[i], BUTTON_WIDTH, BUTTON_HEIGHT)
        button_list.append(button)

def create_input_box(name, rect, default_setting):
    box = TextBox.TextBox(rect)
    box.name = name
    try:
        box.buffer = [str(i) for i in str(default_setting[box.name])]
    except KeyError:
        print("no default for setting:", name)
        pass
    return box

def initialize_defaults_box_list(y_space, x_start, distance_from_text):
    global default_box_list
    global market_settings

    names = ["preference", "radius", "show trade", "apples", "oranges", "apple preference", "orange preference"]

    for i in range(len(names)):
        box = create_input_box(names[i], (x_start, (BUTTON_Y + distance_from_text + (1+i)*(BUTTON_HEIGHT+y_space)), BUTTON_WIDTH, BUTTON_HEIGHT), market_settings)
        default_box_list.append(box)
    default_box_list[0].ACCEPTED = string.ascii_lowercase

def initialize_setting_box_list(y_space, x_start, distance_from_text):
    global setting_box_list
    global settings

    names = ["rows", "columns", "space", "update interval", "visible data points", "speed multiplier"]

    for i in range(len(names)):
        box = create_input_box(names[i], (x_start, (BUTTON_Y + distance_from_text + (1+i)*(BUTTON_HEIGHT+y_space)), BUTTON_WIDTH, BUTTON_HEIGHT), settings)
        setting_box_list.append(box)


def initialize_market():
    global market_list
    global settings
    global market_settings
    global utility_tracker
    global time_step_num_tracker

    r = settings["rows"]
    c = settings["columns"]
    s = settings["space"]
    num_data_points = settings["visible data points"]

    agent_regions = divide_rect(pygame.Rect(SINGLE_MARKET_BORDER),r,c,s)
    market_list = [[Market.Market(agent_regions[row][column],BLACK,market_settings, num_data_points) for row in range(r)] for column in range(c)]

    utility_tracker = deque(maxlen = num_data_points)
    time_step_num_tracker = deque(maxlen = num_data_points)

def market_clicked(market, mouse, display, wait):
    for agent in market.agents:
        if agent.is_point_over_agent(mouse):
            agent.is_selected = not agent.is_selected
            #If the simulation is paused the agent need to be re_drawn
            if wait:
                if agent.is_selected:
                    agent.draw(display)
                else:
                    agent.remove_selected_circle(display)
                    draw_agents(display)
            return
    market.is_selected = not market.is_selected
    if market.is_selected:
        market.color = YELLOW
    else:
        market.color = BLACK


def get_sets_of_apple_orange(market):
    apples_list = []
    oranges_list = []

    for agent in market.agents:
        apples_list.append(agent.apples)
        oranges_list.append(agent.oranges)
    return apples_list, oranges_list



def update_graph(key, market_list, graph):
    label = []

    if key == "line":
        graph.plot_type = "line"
        graph.title = "Utility over time"
        graph.x_label = "Number of time steps"
        graph.y_label = "Utility"
        for row in range(len(market_list)):
            for column in range(len(market_list[row])):
                label.append(str(row) + str(column))
                graph.plot(time_step_num_tracker, list(market_list[row][column].utility_tracker))

    elif key == "Allocation":
            graph.title = "Allocation of goods for each agent"
            graph.x_label = "Number of Apples"
            graph.y_label = "Number of Oranges"
            """
            #plot budget line
            a_list = []
            b_list = []
            for i in range(100):
                a_list.append(i)
                b_list.append(100 - i)
            graph.plot_type = "line"
            graph.plot(a_list,b_list)
            label.append("initial budget line")
            """
            graph.plot_type = "scatter"

            for row in range(len(market_list)):
                for column in range(len(market_list[row])):
                    label.append(str(row) + str(column))
                    apples, oranges = get_sets_of_apple_orange(market_list[row][column])
                    graph.plot(apples, oranges)

    elif key == "price":
        graph.plot_type = "scatter"
        graph.title = "Price over time"
        graph.x_label = "Number of time steps"
        graph.y_label = "Price (number of Oranges for 1 Apple)"
        for row in range(len(market_list)):
            for column in range(len(market_list[row])):
                label.append(str(row) + str(column))
                graph.plot(time_step_num_tracker, list(market_list[row][column].price_tracker))

    graph.set_legend(label)
    graph.update_graph()


def draw_input_box(box, display, font):
    box.update()
    box.draw(display)

    textSurf, textRect = text_objects(box.name, font)
    textRect.midright = box.rect.midleft
    textRect.x -= 5
    display.blit(textSurf, textRect)


def main():
    global setting_box_list
    global settings
    global market_list
    global initial_utility


    pygame.init()
    display = pygame.display.set_mode((WIDTH,HEIGHT), pygame.HWSURFACE)
    display.fill(WHITE)
    pygame.display.set_caption(TITLE)
    clock = pygame.time.Clock()

    button_font = pygame.font.SysFont("arial", 20)
    text_font = pygame.font.SysFont("arial", 30)

    simulation_settings_text = text_font.render("Simulation Settings", True, BLACK)
    market_settings_text = text_font.render("Market Settings (affects all markets if none are selected)", True, BLACK)

    num_agent_input_box = TextBox.TextBox((BUTTON_X, BUTTON_Y, BUTTON_WIDTH, BUTTON_HEIGHT))

    x_start = BUTTON_X + 2*(BUTTON_WIDTH+BUTTON_SPACE)
    setting_box_distance = 400
    simulation_text_xpos = x_start - simulation_settings_text.get_width() + BUTTON_WIDTH
    market_text_xpos = x_start + setting_box_distance

    initialize_setting_box_list(5, x_start, 55)
    initialize_defaults_box_list(5, x_start + setting_box_distance, 55)
    initialize_button_list(display, button_font)
    initialize_market()


    graph = Graph.Graph("Allocation")
    #graph.ylim_min = initial_utility

    run = True
    while run:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                run = False
                break
            #A button was pressed
            #https://www.pygame.org/docs/ref/key.html
            elif event.type == pygame.KEYDOWN:

                #Make one new agent by pressing space
                if event.key == pygame.K_SPACE:
                    create_many_agents(display, market_list, settings, 1)

                #pres p to pause/unpause
                elif event.key == pygame.K_p:
                    settings["wait"] = not settings["wait"]

                elif num_agent_input_box.active:
                    if event.key in (pygame.K_RETURN,pygame.K_KP_ENTER):
                        create_many_agents(display, market_list, settings, num_agent_input_box.execute())

                    #Delete last input with backspace
                    elif event.key == pygame.K_BACKSPACE:
                        if num_agent_input_box.buffer:
                            num_agent_input_box.buffer.pop()
                    #if input is valid (only int are) then add it to the end
                    elif event.unicode in num_agent_input_box.ACCEPTED:
                        num_agent_input_box.buffer.append(event.unicode)

                elif settings["change settings"]:
                    #simulation settings
                    for input_box in setting_box_list:
                        if input_box.active:
                            if event.key in (pygame.K_RETURN, pygame.K_KP_ENTER):
                                input_box.active = False
                                #Setting radius too large makes collision detection fail
                                #Probably bc the agents get's bigger than the bins they fall into
                            #Delete last input
                            if event.key == pygame.K_BACKSPACE:
                                if input_box.buffer:
                                    input_box.buffer.pop()
                            #only allow valid input for this setting
                            elif event.unicode in input_box.ACCEPTED:
                                input_box.buffer.append(event.unicode)
                            break
                    #market settings
                    for input_box in default_box_list:
                        if input_box.active:
                            if event.key in (pygame.K_RETURN, pygame.K_KP_ENTER):
                                input_box.active= False

                            #Delete last input
                            if event.key == pygame.K_BACKSPACE:
                                if input_box.buffer:
                                    input_box.buffer.pop()
                            #only allow valid input for this setting
                            elif event.unicode in input_box.ACCEPTED:
                                input_box.buffer.append(event.unicode)
                            break


            #left mouse click
            elif event.type == pygame.MOUSEBUTTONUP and event.button == 1:
                #get mouse position
                mouse = pygame.mouse.get_pos()
                num_agent_input_box.active = num_agent_input_box.rect.collidepoint(mouse)

               #if the mouse is above the input box it is not above anything else
                if not num_agent_input_box.active:
                    #check if the mouse is above a button, if it is execute that button
                    for b in button_list:
                        r = pygame.Rect(b.getRect())
                        if r.collidepoint(mouse):
                            b.execute()
                            break

                    #update which box is active when changing settings
                    if settings["change settings"]:
                        for input_box in default_box_list:
                            input_box.active = input_box.rect.collidepoint(mouse)

                        for input_box in setting_box_list:
                            input_box.active = input_box.rect.collidepoint(mouse)
                    else:
                        #check if the mouse is above an agent
                        for row in range(len(market_list)):
                            for column in range(len(market_list[row])):
                                #check if market is clicked before looping over agents
                                if market_list[row][column].region.collidepoint(mouse):
                                    market_clicked(market_list[row][column], mouse, display, settings["wait"])
                                    break
        #end of event loop

        if settings["change settings"]:
            display.blit(simulation_settings_text, (simulation_text_xpos , 100))
            display.blit(market_settings_text, (market_text_xpos, 100))
            for input_box in setting_box_list:
                draw_input_box(input_box, display, button_font)

            for input_box in default_box_list:
                draw_input_box(input_box, display, button_font)

        else:
            if settings["wait"]:
                #TODO move this
                button_list[0].color = GREEN
                button_list[0].text = "Start"

            else:
                display.fill(WHITE)
                move_agents()
                draw_agents(display)
                button_list[0].color = RED
                button_list[0].text = "Pause"
                button_list[2].color = GREEN

                if settings["speed multiplier"] > 1:
                    for i in range(settings["speed multiplier"]):
                        move_agents()

            draw_markets(display)

            #draw the input box
            num_agent_input_box.update()
            num_agent_input_box.draw(display)

            #draw current utility
            u = text_font.render("Current Utility: {:0.2f}".format(get_total_utility(market_list)), True, BLACK)
            display.blit(u, (RIGTH_BORDER, 750))

            #update graph
            time = pygame.time.get_ticks()
            if time >= graph.last_update_time + graph.update_delta:
                graph.last_update_time = time
                update_graph(settings["graph"], market_list, graph)
            #draw the graph
            display.blit(graph.get_graph_as_image(), (RIGTH_BORDER,150))

        #draw the buttons
        for b in button_list:
            b.draw_button()

        fps = text_font.render(str(int(clock.get_fps())), True, BLACK)
        display.blit(fps, (WIDTH-fps.get_width()-BUTTON_SPACE, fps.get_height()))


        #60 Frames per second
        clock.tick(60)

        #update the enitre screen
        pygame.display.flip()


    #end of loop exit pygame
    pygame.quit()


if __name__ == "__main__":
    main()
