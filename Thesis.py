
# In[1]:

import pygame
import random
import numpy as np
import pickle
import cProfile
#https://docs.python.org/2/library/profile.html
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
from ColorDefinitions import *


#Sources
#http://usingpython.com/pygame-intro/
#https://pythonprogramming.net/pygame-python-3-part-1-intro/

#Global things
market_list = [[]]
button_list = []
setting_box_list= []
default_box_list = []
wait = True
change_simulation_settings = False
change_market_settings = False

#move region_mode into settings? TODO
region_mode = True

settings = {

            "rows": 1,
            "columns": 1,
            "space": 20,

            }

defaults = {
            "radius" : 10,
            "perfect_substitutes": 0,
            "show trade": 0,
            "random_num_goods": True,
            "cobb_douglass": 1
            }


# In[2]:
WIDTH= 1200
HEIGHT =800
TITLE="Title"
INFO_WIDTH=400

BUTTON_WIDTH = 110
BUTTON_HEIGHT = 60
BUTTON_X = 20
BUTTON_Y = 20
BUTTON_SPACE = 10

#Border of agents
TOP_BORDER = BUTTON_Y+BUTTON_HEIGHT
BOTTOM_BORDER = HEIGHT
RIGTH_BORDER = WIDTH-INFO_WIDTH
LEFT_BORDER = 0


region_width = RIGTH_BORDER-LEFT_BORDER
region_height = BOTTOM_BORDER-TOP_BORDER
SINGLE_MARKET_BORDER = (LEFT_BORDER,TOP_BORDER,region_width,region_height)



num_goods_to_trade = 1
num_agents = 0

#Documnetation for deque
#https://docs.python.org/2/library/collections.html#collections.deque

utility_tracker = []
utility_grapher = deque(maxlen=INFO_WIDTH)
utility_x_cordinates = list(range(RIGTH_BORDER,WIDTH))
initial_utility = 1

pr = cProfile.Profile()

#split a pygame.Rect into many smaller pygame.Rect
def divide_rect(rectangle,rows,columns,space):
    height=rectangle.height/rows
    width=rectangle.width/columns

    r_list=[[0 for x in range(columns)] for y in range(rows)]
    for row in range(rows):
        for c in range(columns):
            r=rectangle.copy()
            r.y+=int(row*height)
            r.x+=int(c*width)
            r.width=width-space
            r.height=height-space
            r_list[row][c]=r
    return r_list

#Set number of bins (used to do collison calculations faster)
BIN_NUM_ROWS=20
BIN_NUM_COLUMNS=20

BOX_MAP=divide_rect(pygame.Rect(LEFT_BORDER,TOP_BORDER,RIGTH_BORDER-LEFT_BORDER,BOTTOM_BORDER-TOP_BORDER),BIN_NUM_ROWS,BIN_NUM_COLUMNS,0)

#each row+colum represents a box and contains a list of agents in that box
box_tracker= [([[]] * BIN_NUM_COLUMNS) for row in range(BIN_NUM_COLUMNS)]




# In[3]:
def save_function(button):
    pass

def market_settings_function(button):
    global change_market_settings
    global button_list
    global market_list
    global default_box_list

    change_market_settings = not change_market_settings
    button.Display.fill(WHITE)

    button_list=[]
    if change_market_settings:
        button.text = "Apply"
        button.x = BUTTON_X+5*(BUTTON_WIDTH+BUTTON_SPACE)
        return_button = Button.button(BUTTON_X+4*(BUTTON_WIDTH+BUTTON_SPACE),BUTTON_Y,GREEN,"Return",button.font,button.Display,return_function)
        button_list.append(button)
        button_list.append(return_button)

    else:
        num_markets_selected = 0
        draw_agents()
        initalize_button_list(button.Display)

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
                        market_list[row][column].settings[input_box.name]=input_box.get_input_as_int()
        #else update only the settings of the selected markets
        else:
            for row in range(len(market_list)):
                for column in range(len(market_list[row])):
                    if market_list[row][column].is_selected:
                        for input_box in default_box_list:
                            #print("updating settings in market",row,column)
                            market_list[row][column].settings[input_box.name]=input_box.get_input_as_int()


def settings_function(button):
    global change_simulation_settings
    global button_list
    global market_list
    global setting_box_list

    change_simulation_settings = not change_simulation_settings
    button.Display.fill(WHITE)

    button_list=[]
    if change_simulation_settings:
        button.text = "Apply"
        return_button = Button.button(BUTTON_X+4*(BUTTON_WIDTH+BUTTON_SPACE),BUTTON_Y,GREEN,"Return",button.font,button.Display,return_function)
        button_list.append(button)
        button_list.append(return_button)


    else:
        draw_agents()
        initalize_button_list(button.Display)


        print("updating simulation settings")
        for input_box in setting_box_list:
            settings[input_box.name]=input_box.get_input_as_int()
        #update markets, if row/columns have changed
        #todo for now this is temporarily and it will clear all market data
        initialize_market()

def reset_function(button):
    clear()
    button.Display.fill(WHITE)
    initialize_market()

def return_function(button):
    global change_simulation_settings
    global change_market_settings
    global button_list
    global setting_box_list

    change_simulation_settings = False
    change_market_settings = False
    button_list=[]
    initalize_button_list(button.Display)
    button.Display.fill(WHITE)
    draw_agents()
    draw_utility_graph(button.Display)

    #what does this do? should i add the same for market_settings??
    for box in setting_box_list:
        try:
            box.buffer = [str(i) for i in str(settings[box.name])]
        except KeyError:
            print("no key for setting_box",box.name)
            print(box)
            continue


def pause_function(button):
    global wait
    wait = not wait


def step_function(button):
    global wait
    wait = True
    button.color=LIME_GREEN
    button.Display.fill(WHITE)
    move_agents()
    draw_agents()
    draw_utility_graph(button.Display)


def region_function(button):
    global region_mode
    global market_list
    global SINGLE_MARKET_BORDER
    global settings
    region_mode = not region_mode

    if region_mode:
        #TODO
        button.text = "borders on"
        button.color = GREEN

        for row in range(len(market_list)):
            for column in range(len(market_list[row])):
                for agent in market_list[row][column].agents:
                    agent.region = market_list[row][column].region


    else:
        button.text = "borders off"
        button.color = RED

        #Do borders by market? would use less memory compared to by agents
        new_region = divide_rect(pygame.Rect(SINGLE_MARKET_BORDER),1,1,settings["space"])[0][0]
        #new_region = pygame.Rect(SINGLE_MARKET_BORDER)

        for row in range(len(market_list)):
            for column in range(len(market_list[row])):
                for agent in market_list[row][column].agents:
                    agent.region = new_region

                #market_list[row][column].region = SINGLE_MARKET_BORDER



#https://www.saltycrane.com/blog/2008/06/how-to-get-current-date-and-time-in/
#Used to get current time
def screenshot_function(button):
    now=datetime.datetime.now()
    current_time = str(now.year) + "-" + str(now.month) + "-" + str(now.day) + " " +str(now.hour) + "h" +str(now.minute)+ "m" +str(now.second) +"s"
    pygame.image.save(button.Display,current_time+" screenshot.jpg")



def clear():
    #global agent_list
    global market_list
    global utility_tracker
    global utility_grapher
    global initial_utility
    global num_agents
    initial_utility = 1
    num_agents = 1
    agent_list =[]
    utility_tracker=[]
    utility_grapher.clear()
    market_list = [[]]

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

#This can use markets to only search in the current market if regions are on
#speed up this function!
def get_nearby_agents(current_r,current_c):
    global box_tracker
    nearby_agents = []
    for r in range(-1,2):
        for c in range(-1,2):
            try:
                nearby_agents.extend(box_tracker[current_r-r][current_c-c])
            except IndexError:
                continue
    return nearby_agents


#can use same logic as function above
def get_nearby_boxes(current_r,current_c):
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


    #Then check other nearby boxes
    #the loop can be unrolled here
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
    global pr
    global box_tracker
    global market_list

    pr.enable()

    box_tracker= [([[]] * BIN_NUM_COLUMNS) for row in range(BIN_NUM_ROWS)]
    utility_tracker.append((len(utility_tracker)+WIDTH-INFO_WIDTH,HEIGHT-(get_utility()/initial_utility)*100))
    utility_grapher.append(HEIGHT-(get_utility()/initial_utility)*100)


    i=0
    for row in range(len(market_list)):
        for column in range(len(market_list[row])):
            market_list[row][column].price = 0
            market_list[row][column].num_trades = 1
            show_trade = market_list[row][column].settings["show trade"]
            for agent in market_list[row][column].agents:
                r,c = agent.box
                agent.move()
                #agent.print_info()
                for other_agent in get_nearby_agents(r,c):
                    if agent.collision(other_agent):
                        agent.bounce(other_agent)

                        if random.getrandbits(1):
                            #other_agent.trade(agent,num_goods_to_trade,settings["show trade"])
                            market_list[row][column].trade(agent, other_agent, num_goods_to_trade,show_trade)
                        else:
                            market_list[row][column].trade(other_agent, agent, num_goods_to_trade,show_trade)
                            #agent.trade(other_agent,num_goods_to_trade,settings["show trade"])
                        #print_total_utility()
                        break
                find_new_box(agent)
            i+=1
            #print("Market number",i)
            #print("Price: ",market_list[row][column].get_price())
            #print("")
    pr.disable()

def get_utility():
    global market_list
    utility=0
    for row in range(len(market_list)):
        for column in range(len(market_list[row])):
            utility += market_list[row][column].get_utility()
    return utility

def draw_agents():
    for row in range(len(market_list)):
        for column in range(len(market_list[row])):
            for agent in market_list[row][column].agents:
                agent.draw()

def draw_markets(Display):
    global market_list
    for row in range(len(market_list)):
        for column in range(len(market_list[row])):
            pygame.draw.rect(Display, market_list[row][column].color, market_list[row][column].region, 1)

def draw_utility_graph(Display):
    if len(utility_grapher)>1:
        line=list(zip(utility_x_cordinates,list(utility_grapher)))
        pygame.draw.lines(Display, RED, False,line, 1)

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


def new_agent_in_region(Display,region,radius):
    global initial_utility
    global num_agents

    for i in range(20):
        agent=Agent.Agent(region,Display,num_agents+1,radius)
        agent.box = set_box(agent)

        if not on_top_of_other_agent(agent):
            find_new_box(agent)
            agent.draw()
            initial_utility += agent.get_utility_cobb_douglass()
            num_agents += 1


        #draw the agent on top if it cannot be place other ways?
        #make that a setting?
            return agent

    return None


def create_many_agents(Display, num):
    global num_agents
    global market_list


    for row in range(len(market_list)):
        for column in range(len(market_list[row])):
            region = market_list[row][column].region
            radius = market_list[row][column].settings["radius"]
            for i in range(num):
                agent = new_agent_in_region(Display,region,radius)
                if agent is not None:
                    market_list[row][column].agents.append(agent)
                    if not radius == agent.radius:
                        print("radius should be:",radius)
                        print("radius is ",agent.radius)
                        print("market",row,column)


    print(num_agents," number agents")

def print_total_utility():
    global_utility = 0
    for agent in agent_list:
        global_utility += agent.get_utility()
    print(global_utility)

## TODO:
#make a create button function
def initalize_button_list(Display):
    global button_list

    small_text = pygame.font.Font("freesansbold.ttf",20)
    pause_button = Button.button(BUTTON_X,BUTTON_Y,GREEN,"Start",small_text,Display,pause_function)
    reset_button = Button.button(BUTTON_X+(BUTTON_WIDTH+BUTTON_SPACE),BUTTON_Y,LIGTH_GREY,"Reset!",small_text,Display,reset_function)
    #The input box is at the BUTTON_X+2*(BUTTON_WIDTH+BUTTON_SPACE) spot
    step_button = Button.button(BUTTON_X+3*(BUTTON_WIDTH+BUTTON_SPACE),BUTTON_Y,GREEN,"Step",small_text,Display,step_function)
    region_button = Button.button(BUTTON_X+4*(BUTTON_WIDTH+BUTTON_SPACE),BUTTON_Y,GREEN,"Region on",small_text,Display,region_function)
    settings_button = Button.button(BUTTON_X+5*(BUTTON_WIDTH+BUTTON_SPACE),BUTTON_Y,GREEN,"Settings",small_text,Display,settings_function)
    screenshot_button = Button.button(BUTTON_X+6*(BUTTON_WIDTH+BUTTON_SPACE),BUTTON_Y,GREEN,"Screenshot",small_text,Display,screenshot_function)
    save_button = Button.button(BUTTON_X+7*(BUTTON_WIDTH+BUTTON_SPACE),BUTTON_Y,GREEN,"Save",small_text,Display,save_function)
    market_settings_button = Button.button(BUTTON_X+8*(BUTTON_WIDTH+BUTTON_SPACE),BUTTON_Y,GREEN,"M Settings",small_text,Display,market_settings_function)

    button_list.append(reset_button)
    button_list.append(pause_button)
    button_list.append(step_button)
    button_list.append(region_button)
    button_list.append(settings_button)
    button_list.append(screenshot_button)
    button_list.append(save_button)
    button_list.append(market_settings_button)

def create_input_box(name,rect,default_setting):

    box = TextBox.TextBox(rect)
    box.name = name
    try:
        box.buffer = [str(i) for i in str(default_setting[box.name])]
    except KeyError:
        print("no key for setting box")
        pass

    return box

def initialize_defaults_box_list():
    global default_box_list
    global defaults

    set_radius = create_input_box("radius",(BUTTON_X+2*(BUTTON_WIDTH+BUTTON_SPACE),BUTTON_Y+BUTTON_HEIGHT,BUTTON_WIDTH,BUTTON_HEIGHT),defaults)
    set_trade = create_input_box("show trade",(BUTTON_X+2*(BUTTON_WIDTH+BUTTON_SPACE),BUTTON_Y+2*BUTTON_HEIGHT,BUTTON_WIDTH,BUTTON_HEIGHT),defaults)
    set_utiltty_function = create_input_box("cobb_douglass",(BUTTON_X+2*(BUTTON_WIDTH+BUTTON_SPACE),BUTTON_Y+3*BUTTON_HEIGHT,BUTTON_WIDTH,BUTTON_HEIGHT),defaults)

    default_box_list.append(set_radius)
    default_box_list.append(set_trade)
    default_box_list.append(set_utiltty_function)

def initialize_setting_box_list():
    global setting_box_list
    global settings

    set_rows = create_input_box("rows",(BUTTON_X+2*(BUTTON_WIDTH+BUTTON_SPACE),BUTTON_Y+BUTTON_HEIGHT,BUTTON_WIDTH,BUTTON_HEIGHT),settings)
    set_columns = create_input_box("columns",(BUTTON_X+2*(BUTTON_WIDTH+BUTTON_SPACE),BUTTON_Y+2*BUTTON_HEIGHT,BUTTON_WIDTH,BUTTON_HEIGHT),settings)

    setting_box_list.append(set_columns)
    setting_box_list.append(set_rows)


def initialize_market():
    global market_list
    global settings
    global defaults

    r=settings["rows"]
    c=settings["columns"]
    s=settings["space"]
    agent_regions = divide_rect(pygame.Rect(SINGLE_MARKET_BORDER),r,c,s)
    market_list = [[Market.Market(agent_regions[row][column],BLACK,defaults) for row in range(r)] for column in range(c)]

def market_clicked(market, mouse):
    global wait

    for agent in market.agents:
        if agent.is_point_over_agent(mouse):
            agent.is_selected = not agent.is_selected
            #If the simulation is paused the agents need to be re_drawn
            if wait:
                if agent.is_selected:
                    agent.draw()
                else:
                    agent.remove_selected_circle()
                    draw_agents()
            return
    market.is_selected = not market.is_selected
    if market.is_selected:
        market.color = YELLOW
    else:
        market.color = BLACK

def main():
    global wait
    global change_simulation_settings
    global change_market_settings
    global setting_box_list
    global region_mode #Don't need this to be a global variable
    global market_list

    pygame.init()
    Display = pygame.display.set_mode((WIDTH,HEIGHT),pygame.HWSURFACE)
    Display.fill(WHITE)
    pygame.display.set_caption(TITLE)
    clock = pygame.time.Clock()
    font = pygame.font.Font(None, 30)

    text = TextBox.TextBox((BUTTON_X+2*(BUTTON_WIDTH+BUTTON_SPACE),BUTTON_Y,BUTTON_WIDTH,BUTTON_HEIGHT))

    initialize_market()
    initialize_setting_box_list()
    initialize_defaults_box_list()
    initalize_button_list(Display)


    run = True
    while run:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                run=False
            #https://www.pygame.org/docs/ref/key.html
            elif event.type == pygame.KEYDOWN:

                #Make one new agent by pressing space
                if event.key == pygame.K_SPACE:
                    create_many_agents(Display,1)

                #pres p to pause/unpause
                elif event.key == pygame.K_p:
                    wait=not wait

                #check if input box is active
                elif text.active:
                    if event.key in (pygame.K_RETURN,pygame.K_KP_ENTER):
                        create_many_agents(Display,text.execute())

                    #Delete last input
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

                #if the mouse is above the input box it is not above anything else
                elif not text.active:
                    #check if the mouse is above an agent
                    for row in range(len(market_list)):
                        for column in range(len(market_list[row])):
                            #check if market is clicked before looping over agents
                            if market_list[row][column].region.collidepoint(mouse):
                                market_clicked(market_list[row][column], mouse)
                                break

        if change_simulation_settings:
            for input_box in setting_box_list:
                input_box.update()
                input_box.draw(Display)

                textSurf, textRect = text_objects(input_box.name, pygame.font.Font("freesansbold.ttf",20))
                textRect.midright = input_box.rect.midleft
                textRect.x -= 5
                Display.blit(textSurf, textRect)

        elif change_market_settings:
            for input_box in default_box_list:
                input_box.update()
                input_box.draw(Display)

                textSurf, textRect = text_objects(input_box.name, pygame.font.Font("freesansbold.ttf",20))
                textRect.midright = input_box.rect.midleft
                textRect.x -= 5
                Display.blit(textSurf, textRect)
        else:
            if wait:
                button_list[1].color = GREEN
                button_list[1].text = "Start"

            else:
                Display.fill(WHITE)
                move_agents()
                draw_agents()
                button_list[1].color = RED
                button_list[1].text = "Pause"
                button_list[2].color = GREEN
                draw_utility_graph(Display)

            draw_markets(Display)

            #draw the input box
            text.update()
            text.draw(Display)

        #draw the buttons
        for b in button_list:
            b.draw_button()



        fps = font.render(str(int(clock.get_fps())), True, BLACK)
        Display.blit(fps, (WIDTH-fps.get_width()-BUTTON_SPACE, fps.get_height()))

        x = 100
        for row in range(len(market_list)):
            for column in range(len(market_list[row])):
                u = font.render(str(market_list[row][column].price),True,BLACK)
                Display.blit(u,(850,x))
                x += 50


        u = font.render(("Current Utility: "+str(get_utility())),True,BLACK)
        Display.blit(u,(1000,750))

        #60 Frames per second
        clock.tick(60)

        #update the screen
        pygame.display.flip()



    pr.print_stats(sort='time')
    #end of loop we exit
    pygame.quit()


if __name__ == "__main__":

    main()
