
# In[1]:

import pygame
import string
import pickle
from collections import deque
import datetime

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
wait = True
change_simulation_settings = False
change_market_settings = False
button_font = None

#move region_mode into settings? TODO
region_mode = True

settings = {
            "rows": 1,
            "columns": 1,
            "space": 20,
            "update interval": 10,
            "visible data points": 2000,
            "speed multiplier": 1
            }

defaults = {
            "radius" : 10,
            "show trade": 0,
            "random_num_goods": True,
            "preference": "normal"
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
raw_utility_grapher = deque(maxlen = settings["visible data points"])
raw_utility_grapher_x = deque(maxlen = settings["visible data points"])



#devides a pygame.Rect into multiple smaller Rects
def divide_rect(rectangle,rows,columns,space):
    height = int(rectangle.height/rows)
    width = int(rectangle.width/columns)
    r_y = rectangle.y
    r_x = rectangle.x

    r_list = [[0 for x in range(columns)] for y in range(rows)]

    for row in range(rows):
        for c in range(columns):
            r_list[row][c] = pygame.Rect(r_x+(width*c),r_y+(height*row),width-space,height-space)
    return r_list



#Set number of bins (used to do collison calculations faster)
BIN_NUM_ROWS = 45
BIN_NUM_COLUMNS = 45

BOX_MAP = divide_rect(pygame.Rect(LEFT_BORDER,TOP_BORDER,RIGTH_BORDER-LEFT_BORDER,BOTTOM_BORDER-TOP_BORDER),BIN_NUM_ROWS,BIN_NUM_COLUMNS,0)

#each row+colum represents a box and contains a list of agents in that box
box_tracker = [([[]] * BIN_NUM_COLUMNS) for row in range(BIN_NUM_COLUMNS)]




# In[3]:
#give graph as varaible!
def graph_type_function(button):
    if button.text == "scatter":
        button.text = "line"
    elif button.text == "line":
        button.text = "price"

    else:
        button.text = "scatter"



#add ability to load other data too, like settings
def load_function(button):
    global market_list
    global wait
    wait = True
    button.display.fill(WHITE)
    try:
        market_list = pickle.load(open("save.p","rb"))
    except FileNotFoundError:
        print("saved file not fond")

    draw_agents(button.display)

def save_function(button):
    global market_list
    pickle.dump(market_list, open("save.p","wb"))



def market_settings_function(button):
    global change_market_settings
    global button_list
    global market_list
    global default_box_list

    change_market_settings = not change_market_settings
    button.display.fill(WHITE)

    button_list=[]
    if change_market_settings:
        button.text = "Apply"
        button.x = BUTTON_X+5*(BUTTON_WIDTH+BUTTON_SPACE)
        return_button = Button.button(BUTTON_X+4*(BUTTON_WIDTH+BUTTON_SPACE),BUTTON_Y,GREEN,"Return",button.font,button.display,return_function)
        button_list.append(button)
        button_list.append(return_button)

    else:
        num_markets_selected = 0
        draw_agents(button.display)
        initalize_button_list(button.display)

        for row in range(len(market_list)):
            for column in range(len(market_list[row])):
                if market_list[row][column].is_selected:
                    num_markets_selected += 1
        #If no market is selected then we update the settings of every market
        #Can this be a true/false value? should it be? TODO
        if num_markets_selected == 0:
            for row in range(len(market_list)):
                for column in range(len(market_list[row])):
                    for input_box in default_box_list:
                        #print("updating settings in market",row,column)
                        market_list[row][column].settings[input_box.name] = input_box.get_input()
                        #same as below
                        #if market_list[row][column].settings[input_box.name] == market_list[row][column].settings["preference"]:
                        #    for agent in market_list[row][column].agents:
                        #        agent.preference = market_list[row][column].settings["preference"]

        #else update only the settings of the selected markets
        else:
            for row in range(len(market_list)):
                for column in range(len(market_list[row])):
                    if market_list[row][column].is_selected:
                        for input_box in default_box_list:
                            #print("updating settings in market",row,column)
                            market_list[row][column].settings[input_box.name] = input_box.get_input()
                            #It's possible to update settings for agents this way
                            #but preference cannot be changed on the fly (unless utility is reset)
                            #if market_list[row][column].settings[input_box.name] == market_list[row][column].settings["preference"]:
                            #    for agent in market_list[row][column].agents:
                            #        agent.preference = market_list[row][column].settings["preference"]
                            #    print("updated market",row,column)



def settings_function(button):
    global change_simulation_settings
    global button_list
    global market_list
    global setting_box_list
    global wait

    change_simulation_settings = not change_simulation_settings
    button.display.fill(WHITE)

    button_list=[]
    if change_simulation_settings:
        button.text = "Apply"
        return_button = Button.button(BUTTON_X+4*(BUTTON_WIDTH+BUTTON_SPACE),BUTTON_Y,GREEN,"Return",button.font,button.display,return_function)
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
        draw_agents(button.display)
        initalize_button_list(button.display)
        wait = True

def reset_function(button):
    clear()
    button.display.fill(WHITE)
    initialize_market()

def return_function(button):
    global change_simulation_settings
    global change_market_settings
    global button_list
    global setting_box_list

    change_simulation_settings = False
    change_market_settings = False
    button_list=[]
    initalize_button_list(button.display)
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
    global wait
    wait = not wait


def step_function(button):
    global wait
    wait = True
    button.color = LIME_GREEN
    button.display.fill(WHITE)
    move_agents()
    draw_agents(button.display)
    #draw graphs here
    #TODO

def region_function(button):
    global region_mode
    global market_list
    global SINGLE_MARKET_BORDER
    global settings
    region_mode = not region_mode

    if region_mode:
        button.text = "Borders on"
        button.color = GREEN

        for row in range(len(market_list)):
            for column in range(len(market_list[row])):
                for agent in market_list[row][column].agents:
                    agent.region = market_list[row][column].region
    else:
        button.text = "Borders off"
        button.color = RED
        new_region = divide_rect(pygame.Rect(SINGLE_MARKET_BORDER),1,1,settings["space"])[0][0]

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
    global raw_utility_grapher
    global raw_utility_grapher_x

    initial_utility = 1
    num_agents = 0
    market_list = [[]]
    raw_utility_grapher.clear()
    raw_utility_grapher_x.clear()


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
    print(x)
    print(y)
    print("box not found")

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
        if 0<= current_r-row <BIN_NUM_ROWS:
            for col in range(-1,2):
                if 0<=current_c-col <BIN_NUM_COLUMNS and not row==col==0:
                    nearby_boxes.append((current_r-row,current_c-col))
    return nearby_boxes


#thie needs some clean up!! idea is to use direction of agent to speed up calculations
#finds the new box based on the previous box
def find_new_box(agent):
    global box_tracker

    r,c=agent.box
    x,y=agent.get_location()

    #Check the old box first, since the agent is most likely there
    if BOX_MAP[r][c].collidepoint(x,y):
       box_tracker[r][c].append(agent)
       return


    #the loop can be unrolled and speed up here
    for row,col in get_nearby_boxes(r,c):
        if BOX_MAP[row][col].collidepoint(x,y):
            box_tracker[row][col].append(agent)
            agent.box=(row,col)
            #print("new box is ",row,col)
            return
    #This should never happen
    print("could not find new box")
# In[5]:


def move_agents():
    global box_tracker
    global market_list
    global num_time_steps
    global raw_utility_grapher
    global raw_utility_grapher_x
    global setting_box_list

    box_tracker= [([[]] * BIN_NUM_COLUMNS) for row in range(BIN_NUM_ROWS)]
    num_time_steps += 1
    update = num_time_steps % settings["update interval"] == 0

    if update:
        raw_utility_grapher.append(get_total_utility(market_list))
        raw_utility_grapher_x.append(num_time_steps)

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

#market_list does not need to be global for this function!!
def get_total_utility(market_list):
    utility=0
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
    for other_agent in get_nearby_agents(r,c):
        if agent.collision(other_agent):
            #print("agent on top of other agent at spawn")
            return True
    return False


def new_agent_in_region(display,region,radius,preference):
    global initial_utility
    global num_agents

    for i in range(20):
        agent=Agent.Agent(region,num_agents+1,radius,preference)
        agent.box = set_box(agent)

        if not on_top_of_other_agent(agent):
            find_new_box(agent)
            agent.draw(display)
            initial_utility += agent.get_utility()
            num_agents += 1

            return agent

    return None


def create_many_agents(display, num, graph):
    global num_agents
    global market_list
    global initial_utility

    for row in range(len(market_list)):
        for column in range(len(market_list[row])):
            region = market_list[row][column].region
            radius = market_list[row][column].settings["radius"]
            preference = market_list[row][column].settings["preference"]
            for i in range(num):
                agent = new_agent_in_region(display,region,radius,preference)
                if agent is not None:
                    market_list[row][column].agents.append(agent)
                    if not radius == agent.radius:
                        print("radius should be:",radius)
                        print("radius is ",agent.radius)
                        print("market",row,column)

    graph.ylim_min = initial_utility
    print(num_agents," number agents")

def initalize_button_list(display):
    global button_list
    global button_font

    names = ["Start", "Reset!", "Step", "Borders on", "Settings", "Screenshot",
     "Save", "M Settings", "Load", "scatter"]
    functions = [pause_function, reset_function, step_function, region_function,
     settings_function, screenshot_function, save_function, market_settings_function, load_function, graph_type_function]

    #The input box is at the BUTTON_X spot, so that is skipped by adding x
    x = BUTTON_WIDTH + BUTTON_SPACE
    for i in range(len(names)):
        button = Button.button(BUTTON_X+ (i+1)*x, BUTTON_Y, GREEN, names[i], button_font, display, functions[i])
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

def initialize_defaults_box_list():
    global default_box_list
    global defaults

    y_space = 5
    names = ["radius", "show trade", "preference"]
    x = BUTTON_X + 2*(BUTTON_WIDTH+BUTTON_SPACE)
    for i in range(len(names)):
        box = create_input_box(names[i], (x, BUTTON_Y + (1+i)*(BUTTON_HEIGHT+y_space), BUTTON_WIDTH, BUTTON_HEIGHT), defaults)
        default_box_list.append(box)
    default_box_list[-1].ACCEPTED = string.ascii_lowercase

def initialize_setting_box_list():
    global setting_box_list
    global settings

    y_space = 5
    names = ["rows", "columns", "space", "update interval", "visible data points", "speed multiplier"]
    x = BUTTON_X + 2*(BUTTON_WIDTH+BUTTON_SPACE)
    for i in range(len(names)):
        box = create_input_box(names[i], (x, BUTTON_Y + (1+i)*(BUTTON_HEIGHT+y_space), BUTTON_WIDTH, BUTTON_HEIGHT), settings)
        setting_box_list.append(box)


def initialize_market():
    global market_list
    global settings
    global defaults
    global raw_utility_grapher
    global raw_utility_grapher_x

    r = settings["rows"]
    c = settings["columns"]
    s = settings["space"]
    num_data_points = settings["visible data points"]

    agent_regions = divide_rect(pygame.Rect(SINGLE_MARKET_BORDER),r,c,s)
    market_list = [[Market.Market(agent_regions[row][column],BLACK,defaults, num_data_points) for row in range(r)] for column in range(c)]

    raw_utility_grapher = deque(maxlen = num_data_points)
    raw_utility_grapher_x = deque(maxlen = num_data_points)

def market_clicked(market, mouse, display):
    global wait

    for agent in market.agents:
        if agent.is_point_over_agent(mouse):
            agent.is_selected = not agent.is_selected
            #If the simulation is paused the agents need to be re_drawn
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
                graph.plot(raw_utility_grapher_x, list(market_list[row][column].utility_tracker))

    elif key == "scatter":
            graph.title = "Allocation of goods for each agent"
            graph.x_label = "Number of Apples"
            graph.y_label = "Number of Oranges"
            #plot budget line
            a_list = []
            b_list = []
            for i in range(100):
                a_list.append(i)
                b_list.append(100 - i)
            graph.plot_type = "line"
            graph.plot(a_list,b_list)
            label.append("initial budget line")
            graph.plot_type = "scatter"

            for row in range(len(market_list)):
                for column in range(len(market_list[row])):
                    label.append(str(row) + str(column))
                    apples, oranges = get_sets_of_apple_orange(market_list[row][column])
                    graph.plot(apples, oranges)

    elif key == "price":
        graph.plot_type = "scatter" #scatter or line??? Ask Mayer
        graph.title = "Price over time"
        graph.x_label = "Number of time steps"
        graph.y_label = "Price for [apple/orange]"
        for row in range(len(market_list)):
            for column in range(len(market_list[row])):
                label.append(str(row) + str(column))
                graph.plot(raw_utility_grapher_x, list(market_list[row][column].price_tracker))

    graph.set_legend(label)
    graph.update_graph()


def main():
    global wait
    global change_simulation_settings
    global change_market_settings
    global setting_box_list
    global region_mode #Don't need this to be a global variable
    global market_list
    global initial_utility
    global button_font

    pygame.init()
    display = pygame.display.set_mode((WIDTH,HEIGHT),pygame.HWSURFACE)
    display.fill(WHITE)
    pygame.display.set_caption(TITLE)
    clock = pygame.time.Clock()
    font = pygame.font.Font(None, 30)
    button_font = pygame.font.Font("freesansbold.ttf",20)

    #rename?
    text = TextBox.TextBox((BUTTON_X,BUTTON_Y,BUTTON_WIDTH,BUTTON_HEIGHT))

    initialize_market()
    initialize_setting_box_list()
    initialize_defaults_box_list()
    initalize_button_list(display)

    graph = Graph.Graph("scatter")


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
                    create_many_agents(display,1,graph)

                #pres p to pause/unpause
                elif event.key == pygame.K_p:
                    wait = not wait

                #check if input box (text) is active
                elif text.active:
                    if event.key in (pygame.K_RETURN,pygame.K_KP_ENTER):
                        create_many_agents(display,text.execute(),graph)

                    #Delete last input with backspace
                    elif event.key == pygame.K_BACKSPACE:
                        if text.buffer:
                            text.buffer.pop()
                    #if input is valid (only int are) then add it to the end
                    elif event.unicode in text.ACCEPTED:
                        text.buffer.append(event.unicode)

                elif change_simulation_settings:
                    for input_box in setting_box_list:
                        if input_box.active:
                            if event.key in (pygame.K_RETURN,pygame.K_KP_ENTER):
                                input_box.active= False
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
                elif change_market_settings:
                    for input_box in default_box_list:
                        if input_box.active:
                            if event.key in (pygame.K_RETURN,pygame.K_KP_ENTER):
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
            elif event.type == pygame.MOUSEBUTTONUP and event.button==1:
                #get mouse position
                mouse = pygame.mouse.get_pos()
                text.active = text.rect.collidepoint(mouse)

               #if the mouse is above the input box it is not above anything else
                if not text.active:
                    #check if the mouse is above a button, if it is execute that button
                    for b in button_list:
                        r = pygame.Rect(b.getRect())
                        if r.collidepoint(mouse):
                            b.execute()
                            break

                    #if chaninging simulation settings, update if a input box is active
                    if change_market_settings:
                        for input_box in default_box_list:
                            input_box.active = input_box.rect.collidepoint(mouse)
                    #if chaninging market settings, update if a input box is active
                    elif change_simulation_settings:
                        for input_box in setting_box_list:
                            input_box.active = input_box.rect.collidepoint(mouse)
                    else:
                        #check if the mouse is above an agent
                        for row in range(len(market_list)):
                            for column in range(len(market_list[row])):
                                #check if market is clicked before looping over agents
                                if market_list[row][column].region.collidepoint(mouse):
                                    market_clicked(market_list[row][column], mouse, display)
                                    break
        #end of event loop

        if change_simulation_settings:
            for input_box in setting_box_list:
                input_box.update()
                input_box.draw(display)

                textSurf, textRect = text_objects(input_box.name, button_font)
                textRect.midright = input_box.rect.midleft
                textRect.x -= 5
                display.blit(textSurf, textRect)

        elif change_market_settings:
            for input_box in default_box_list:
                input_box.update()
                input_box.draw(display)

                textSurf, textRect = text_objects(input_box.name, button_font)
                textRect.midright = input_box.rect.midleft
                textRect.x -= 5
                display.blit(textSurf, textRect)
        else:
            if wait:
                #TODO move this to the wait button
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
            text.update()
            text.draw(display)

            #draw current utility
            u = font.render("Current Utility: {:0.2f}".format(get_total_utility(market_list)), True, BLACK)
            display.blit(u,(RIGTH_BORDER, 750))

            #update graph
            time = pygame.time.get_ticks()
            if time >= graph.last_update_time + graph.update_delta:
                graph.last_update_time = time
                update_graph(button_list[-1].text, market_list, graph)
            #draw the graph
            display.blit(graph.get_graph_as_image(), (RIGTH_BORDER,150))

        #draw the buttons
        for b in button_list:
            b.draw_button()

        fps = font.render(str(int(clock.get_fps())), True, BLACK)
        display.blit(fps, (WIDTH-fps.get_width()-BUTTON_SPACE, fps.get_height()))


        #60 Frames per second
        clock.tick(60)

        #update the enitre screen
        pygame.display.flip()



    #end of loop we exit
    pygame.quit()


if __name__ == "__main__":
    main()
