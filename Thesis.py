
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
market_setting_list = []


settings = {
            "rows": 1,
            "columns": 1,
            "space": 10,
            "update interval": 10,
            "visible data points": 2000,
            "speed multiplier": 1,
            "region_mode": True,
            "avoid overlapping agents": 1,
            "graph": "line",
            "wait": True,
            "change settings": False,
            "Allocation Graph Size" : 175,
            "max_preference": 16,
            "min_preference": 0,
            "max_initial_goods": 1000
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

BUTTON_WIDTH = 115
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
    #roundeing error here, when devisision is rounded then the rect does not
    #return the parts that are rounded off.
    #Fix is to return the last row/col and have them be smaller
    height = int(rectangle.height/rows)
    width = int(rectangle.width/columns)

    """
    #possible fix? TODO
    if width*columns < rectangle.width:
        columns += 1
    if height*rows < rectangle.height:
        rows += 1
    """

    r_y = rectangle.y
    r_x = rectangle.x

    r_list = [[0 for x in range(columns)] for y in range(rows)]

    for row in range(rows):
        for c in range(columns):
            r_list[row][c] = pygame.Rect(r_x+(width*c), r_y+(height*row), width-space, height-space)
    return r_list




#Set number of bins (used to do collison calculations faster)
BIN_NUM_ROWS = 30 #30
BIN_NUM_COLUMNS = 45 #7s

BOX_MAP = divide_rect(pygame.Rect(SINGLE_MARKET_BORDER), BIN_NUM_ROWS, BIN_NUM_COLUMNS, 0)

#each row+colum represents a box and contains a list of agents in that box
box_tracker = [([[]] * BIN_NUM_COLUMNS) for row in range(BIN_NUM_COLUMNS)]



# In[3]:
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
    global num_time_steps

    settings["wait"] = True
    button.display.fill(WHITE)
    try:
        load_list = pickle.load(open("save.p","rb"))
        market_list = load_list[0]
        settings = load_list[1]
        time_step_num_tracker = load_list[2]
        utility_tracker = load_list[3]
        num_time_steps = time_step_num_tracker[-1]
    except FileNotFoundError:
        print("saved file not fond")

    return_function(button)

def save_function(button):
    global market_list
    global settings
    global time_step_num_tracker
    global utility_tracker

    dump_list = [market_list, settings, time_step_num_tracker, utility_tracker]
    pickle.dump(dump_list, open("save.p", "wb"))


def preference_function(button):
    global market_settings
    global market_setting_list

    if market_settings["preference"] == "normal":
        market_settings["preference"] = "linear"
    else:
         market_settings["preference"] = "normal"

    market_setting_list[0].buffer = []
    for s in market_settings["preference"]:
        market_setting_list[0].buffer.append(s)


def get_selected_markets(market_list):
    selected = []
    all_markets = []
    for row in range(len(market_list)):
        for column in range(len(market_list[row])):
            all_markets.append(market_list[row][column])
            if market_list[row][column].is_selected:
                selected.append(market_list[row][column])
    if selected:
        return selected
    return all_markets

def settings_function(button):
    global button_list
    global market_list
    global market_setting_list
    global setting_box_list
    global settings
    global BUTTON_SPACE

    settings["change settings"] = not settings["change settings"]
    button.display.fill(WHITE)
    button_list = []
    selected_markets = get_selected_markets(market_list)

    if settings["change settings"]:
        button.text = "Apply"
        return_button = Button.button(BUTTON_X+4*(BUTTON_WIDTH+BUTTON_SPACE),BUTTON_Y,GREEN,"Return",button.font,button.display,return_function, BUTTON_WIDTH, BUTTON_HEIGHT)

        x = market_setting_list[3].rect.x + market_setting_list[3].rect.w + BUTTON_SPACE
        y = market_setting_list[0].rect.y
        preference_button = Button.button(x, y, GREEN,"Next preference",button.font,button.display,preference_function, BUTTON_WIDTH, BUTTON_HEIGHT)

        button_list.append(button)
        button_list.append(return_button)
        button_list.append(preference_button)

        #update box Buffers
        for box in setting_box_list:
            box.buffer = [str(i) for i in str(settings[box.name])]

        for box in market_setting_list:
            new_buffer = ""
            stop = False
            for market in selected_markets:
                if stop:
                    break
                if new_buffer == "":
                    new_buffer = market.settings[box.name]
                else:
                    #need to compare as string, since the string 1 is not the same as the int 1
                    if not (str(new_buffer) == str(market.settings[box.name])):
                        new_buffer = ""
                        stop = True
            box.buffer = [str(i) for i in str(new_buffer)]

    else:
        #Only initialize_markets again if needed
        update_markets = False
        for input_box in setting_box_list:
            input = input_box.execute()
            if input_box.name == "rows" or input_box.name == "columns" or input_box.name == "space":
                if not settings[input_box.name] == input:
                    update_markets = True
            settings[input_box.name] = input
        if update_markets:
            initialize_market()

        #updating settings for selected markets
        for market in selected_markets:
            for input_box in market_setting_list:
                market.settings[input_box.name] = input_box.execute()
                #It's possible to update settings for agents here
                #possible future work to add settings for them
        no_red_boxes = True

        #chack that no box is red
        for input_box in setting_box_list:
            if input_box.outline_color == RED:
                no_red_boxes = False
                break
        for box in market_setting_list:
            if box.outline_color == RED:
                no_red_boxes = False
                break

        if no_red_boxes:
            draw_agents(button.display)
            initialize_button_list(button.display, button.font)
            settings["wait"] = True
        else:
            settings_function(button)


def reset_function(button):
    global settings
    global num_time_steps

    num_time_steps = 0
    settings["wait"] = True
    clear()
    button.display.fill(WHITE)
    initialize_market()

def return_function(button):
    global settings
    global button_list
    global setting_box_list

    settings["change settings"] = False
    initialize_button_list(button.display, button.font)
    button.display.fill(WHITE)
    draw_agents(button.display)

    for box in setting_box_list:
        box.buffer = [str(i) for i in str(settings[box.name])]


def pause_function(button):
    global settings
    settings["wait"] = not settings["wait"]


def step_function(button):
    global settings
    settings["wait"] = True
    button.color = LIME_GREEN
    button.display.fill(WHITE)

    for i in range(settings["speed multiplier"]):
        move_agents()
    draw_agents(button.display)
    #Need to update current utility
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
#It is possible that adding the current box to the list first is faster,
#since the agents will then have a collison earlier in the list
#TODO
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


def get_nearby_boxes(current_r, current_c):
    global BIN_NUM_ROWS
    nearby_boxes = []
    for row in range(-1,2):
        if 0 <= current_r-row < BIN_NUM_ROWS:
            for col in range(-1,2):
                if 0 <= current_c-col < BIN_NUM_COLUMNS and not row == col == 0:
                    nearby_boxes.append((current_r-row,current_c-col))
    return nearby_boxes


#thie needs some clean up!! idea is to use direction of agent to speed up calculations
#finds the new box based on the previous box
def find_new_box(agent):
    global box_tracker
    global BOX_MAP

    r, c = agent.box
    x, y = agent.get_location()


    #Check the old box first, since the agent is most likely there
    if BOX_MAP[r][c].collidepoint(x,y):
        box_tracker[r][c].append(agent)
        return


    #the loop can be unrolled, but that is not any faster (tested with profiler)
    for row, col in get_nearby_boxes(r,c):
        #print(BOX_MAP[row][col])
        if BOX_MAP[row][col].collidepoint(x,y):
            box_tracker[row][col].append(agent)
            agent.box = (row,col)
            return

    #This should never happen, but if it does then set_box again
    #print("could not find new box")
    agent.box = set_box(agent)
    r, c = agent.box
    box_tracker[r][c].append(agent)

# In[5]:


def move_agents():
    global box_tracker
    global market_list
    global num_time_steps
    global utility_tracker
    global time_step_num_tracker
    global setting_box_list

    box_tracker = [([[]] * BIN_NUM_COLUMNS) for row in range(BIN_NUM_ROWS)]
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
                        #only collide with one agent each timestep
                        break
                find_new_box(agent)

            if update:
                market_list[row][column].utility_tracker.append(market_list[row][column].get_utility())
                market_list[row][column].price_tracker.append(market_list[row][column].get_price())
                market_list[row][column].price = 0
                market_list[row][column].num_trades = 0

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
            return True
    return False


def new_agent_in_region(display, region, radius, preference, apples, oranges, overlapp, pref_a, pref_o, min, max):
    global initial_utility
    global num_agents


    for i in range(20):
        agent = Agent.Agent(region, num_agents+1, radius, preference, apples, oranges, min, max)
        agent.box = set_box(agent)

        if not overlapp or not on_top_of_other_agent(agent):
            if pref_a > 0 and pref_o > 0:
                if agent.preference == "normal":
                    a = pref_a / (pref_a+pref_o)
                    agent.pref_apples = a
                    agent.pref_oranges = 1-a
                elif agent.preference == "linear":
                    agent.pref_apples = pref_a
                    agent.pref_oranges = pref_o

            find_new_box(agent)
            agent.draw(display)
            initial_utility += agent.get_utility()
            num_agents += 1

            return agent
    return None


def create_many_agents(display, market_list, settings, num):

    overlapp = settings["avoid overlapping agents"]
    min = settings["min_preference"]
    max = settings["max_preference"]
    max_goods = settings["max_initial_goods"]
    #only create new agent in selected markets
    for market in get_selected_markets(market_list):
        region = market.region
        radius = market.settings["radius"]
        preference = market.settings["preference"]

        pref_a = market.settings["apple preference"]
        pref_o = market.settings["orange preference"]

        for i in range(num):
            apples = market.settings["apples"]
            oranges = market.settings["oranges"]
            if apples < 1:
                apples = random.randint(1, max_goods)
            if oranges < 1:
                oranges = random.randint(1, max_goods)

            agent = new_agent_in_region(display, region, radius, preference, apples, oranges, overlapp, pref_a, pref_o, min, max)
            if agent is not None:
                market.agents.append(agent)


def initialize_button_list(display, font):
    global button_list
    global settings
    button_list = []

    names = ["Start", "Reset!", "Step", "Borders on", "Settings", "Screenshot",
     "Save", "Load", "Next Graph"]
    functions = [pause_function, reset_function, step_function, region_function,
     settings_function, screenshot_function, save_function, load_function, graph_type_function]

    #The input box is at the BUTTON_X spot, so that is skipped (by adding x)
    x = BUTTON_WIDTH + BUTTON_SPACE
    for i in range(len(names)):
        button = Button.button(BUTTON_X+ (i+1)*x, BUTTON_Y, GREEN, names[i], font, display, functions[i], BUTTON_WIDTH, BUTTON_HEIGHT)
        button_list.append(button)

    if not settings["region_mode"]:
        button_list[3].color = RED

def create_input_box(name, rect, default_setting, min, max):
    box = TextBox.TextBox(rect, min, max)
    box.name = name
    try:
        box.buffer = [str(i) for i in str(default_setting[box.name])]
    except KeyError:
        print("no default for setting:", name)
        pass
    return box

def initalize_market_setting_box_list(y_space, x_start, distance_from_text):
    global market_setting_list
    global market_settings
    global settings

    names = ["preference", "radius", "show trade", "apples", "oranges", "apple preference", "orange preference"]
    min = [None, 1, 0, 0, 0, 0, 0]
    max = [None, 15, 1, settings["max_initial_goods"], settings["max_initial_goods"], settings["max_preference"], settings["max_preference"]]

    for i in range(len(names)):
        box = create_input_box(names[i], (x_start, (BUTTON_Y + distance_from_text + (1+i)*(BUTTON_HEIGHT+y_space)), BUTTON_WIDTH, BUTTON_HEIGHT), market_settings, min[i], max[i])
        market_setting_list.append(box)
    market_setting_list[0].ACCEPTED = string.ascii_lowercase
    market_setting_list[0].accepted_strings = ["normal", "linear"]

def initialize_setting_box_list(y_space, x_start, distance_from_text):
    global setting_box_list
    global settings

    names = ["rows", "columns", "space", "update interval", "visible data points", "speed multiplier", "Allocation Graph Size", "avoid overlapping agents"]
    min = [1, 1, 0, 1, 100, 1, 50, 0]
    max = [3, 3, 10, 100, 10000, 100, 10000, 1]


    for i in range(len(names)):
        box = create_input_box(names[i], (x_start, (BUTTON_Y + distance_from_text + (1+i)*(BUTTON_HEIGHT+y_space)), BUTTON_WIDTH, BUTTON_HEIGHT), settings, min[i], max[i])
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



def update_graph(settings, market_list, graph):
    label = []

    if settings["graph"] == "line":
        graph.plot_type = "line"
        graph.title = "Utility over time"
        graph.x_label = "Number of time steps"
        graph.y_label = "Utility"
        for row in range(len(market_list)):
            for column in range(len(market_list[row])):
                label.append(str(row) + str(column))
                graph.plot(time_step_num_tracker, list(market_list[row][column].utility_tracker))

    elif settings["graph"] == "Allocation":
            graph.title = "Allocation of goods for each agent"
            graph.x_label = "Number of Apples"
            graph.y_label = "Number of Oranges"
            graph.plot_type = "scatter"

            for row in range(len(market_list)):
                for column in range(len(market_list[row])):
                    label.append(str(row) + str(column))
                    apples, oranges = get_sets_of_apple_orange(market_list[row][column])
                    graph.plot(apples, oranges)
            graph.make_box(0, (settings["Allocation Graph Size"]))

    elif settings["graph"] == "price":
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

    num_agent_input_box = TextBox.TextBox((BUTTON_X, BUTTON_Y, BUTTON_WIDTH, BUTTON_HEIGHT), 0, 1000)

    x_start = BUTTON_X + 2*(BUTTON_WIDTH+BUTTON_SPACE)
    setting_box_distance = 400
    simulation_text_xpos = x_start - simulation_settings_text.get_width() + BUTTON_WIDTH
    market_text_xpos = x_start + setting_box_distance

    initialize_setting_box_list(5, x_start, 55)
    initalize_market_setting_box_list(5, x_start + setting_box_distance, 55)
    initialize_button_list(display, button_font)
    initialize_market()

    graph = Graph.Graph("Allocation")
    fps = text_font.render(str(int(clock.get_fps())), True, BLACK)
    current_utility = text_font.render("Current Utility: {:0.2f}".format(get_total_utility(market_list)), True, BLACK)

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
                        num_agent_input_box.write_to_buffer(event.unicode)


                #This can be put in a function, repeating code below.
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
                                input_box.write_to_buffer(event.unicode)
                            break
                    #market settings
                    for input_box in market_setting_list:
                        if input_box.active:
                            if event.key in (pygame.K_RETURN, pygame.K_KP_ENTER):
                                input_box.active = False

                            #Delete last input
                            if event.key == pygame.K_BACKSPACE:
                                if input_box.buffer:
                                    input_box.buffer.pop()
                            #only allow valid input for this setting
                            elif event.unicode in input_box.ACCEPTED:
                                input_box.write_to_buffer(event.unicode)
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
                        for input_box in market_setting_list:
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

            for input_box in market_setting_list:
                draw_input_box(input_box, display, button_font)

        else:
            if settings["wait"]:
                button_list[0].color = GREEN
                button_list[0].text = "Start"

            else:
                display.fill(WHITE)
                move_agents()
                draw_agents(display)
                button_list[0].color = RED
                button_list[0].text = "Pause"
                button_list[2].color = GREEN
                #only update fps and utility when not paused
                fps = text_font.render(str(int(clock.get_fps())), True, BLACK)
                current_utility = text_font.render("Current Utility: {:0.2f}".format(get_total_utility(market_list)), True, BLACK)

                if settings["speed multiplier"] > 1:
                    for i in range(settings["speed multiplier"]):
                        move_agents()

            draw_markets(display)

            #draw the input box
            num_agent_input_box.update()
            num_agent_input_box.draw(display)

            #update graph and utility
            time = pygame.time.get_ticks()
            if time >= graph.last_update_time + graph.update_delta:
                graph.last_update_time = time
                update_graph(settings, market_list, graph)


            #draw the graph and utility
            display.blit(graph.get_graph_as_image(), (RIGTH_BORDER,150))
            display.blit(current_utility, (RIGTH_BORDER, 750))

        #draw the buttons
        for b in button_list:
            b.draw_button()

        #draw fps
        display.blit(fps, (WIDTH-fps.get_width()-BUTTON_SPACE, fps.get_height()))

        """
        #draw the box_map
        for row in range(len(BOX_MAP)):
            for column in range(len(BOX_MAP[row])):
                pygame.draw.rect(display, YELLOW, BOX_MAP[row][column], 1)
        """

        #max 60 Frames per second
        clock.tick(60)

        #update the enitre screen
        pygame.display.flip()


    #end of loop exit pygame
    pygame.quit()



if __name__ == "__main__":
    main()
