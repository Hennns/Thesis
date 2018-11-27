
# In[1]:


"""TODO:
cobb duglas utility
"""


import pygame
import random
import numpy as np
from collections import deque

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
from ColorDefinitions import *



#Sources
#http://usingpython.com/pygame-intro/
#https://pythonprogramming.net/pygame-python-3-part-1-intro/

#Global things
wait = True
agent_list = []


# In[2]:
WIDTH= 1200
HEIGHT =800
TITLE="Title"
INFO_WIDTH=400

BUTTON_WIDTH = 100
BUTTON_HEIGHT = 60
BUTTON_X = 20
BUTTON_Y = 20
BUTTON_SPACE = 10

#Border of agents
TOP_BORDER = BUTTON_Y+BUTTON_HEIGHT
BOTTOM_BORDER =HEIGHT
RIGTH_BORDER =WIDTH-INFO_WIDTH
LEFT_BORDER=0

num_goods_to_trade=2

#Documnetation for deque
#https://docs.python.org/2/library/collections.html#collections.deque

utility_tracker = []
utility_grapher = deque(maxlen =INFO_WIDTH)
utility_x_cordinates=list(range(RIGTH_BORDER,WIDTH))
initial_utility = 1


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
BIN_NUM_ROWS=16
BIN_NUM_COLLUMS=16

BOX_MAP=divide_rect(pygame.Rect(LEFT_BORDER,TOP_BORDER,RIGTH_BORDER-LEFT_BORDER,BOTTOM_BORDER-TOP_BORDER),BIN_NUM_ROWS,BIN_NUM_COLLUMS,0)

#each row+collum represents a box and contains a list of agents in that box
box_tracker= [([[]] * BIN_NUM_COLLUMS) for row in range(BIN_NUM_COLLUMS)]



agent_settings = {
                "radius" : 20,
                "perfect_substitutes": True
                }


settings = {
            "show_trade": False,
            "num_rows": 1,
            "num_collums": 1,
            "random_num_goods": True
            }


# In[3]:


def settings_function(button):
    global wait
    wait = True
    button.Display.fill(WHITE)

def reset_function(button):
    global agent_list
    global utility_tracker
    global utility_grapher
    global initial_utility
    initial_utility=1
    agent_list =[]
    utility_tracker=[]
    utility_grapher.clear()
    button.Display.fill(WHITE)


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


#needs to be updated/do something different. no longer needed
def graph_function(button):
    global wait
    wait = True
    button.Display.fill(WHITE)
    pygame.draw.lines(button.Display, RED, False, utility_tracker, 1)
    #print(utility_tracker)
    pygame.display.flip()


# In[4]:

def get_box(agent):
    x,y = agent.get_location()
    for row in range(len(BOX_MAP)):
        for col in range(len(BOX_MAP[row])):
            if BOX_MAP[row][col].collidepoint(x,y):
                return (row,col)
    #This should never happen
    print("box not found")


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

def get_nearby_boxes(current_r,current_c):
    nearby_boxes = []
    for row in range(-1,2):
        if 0<= current_r-row <BIN_NUM_ROWS:
            for col in range(-1,2):
                if 0<=current_c-col <BIN_NUM_COLLUMS and not row==col==0:
                    nearby_boxes.append((current_r-row,current_c-col))
    return nearby_boxes

#Idea: Use direction agent is moving to find the new box?
def find_new_box(agent):
    r,c=agent.box
    x,y=agent.get_location()

    #Check the old box first, since the agent is most likely there
    if BOX_MAP[r][c].collidepoint(x,y):
        box_tracker[r][c].append(agent)
        return

    #Then check other nearby boxes
    for row,col in get_nearby_boxes(r,c):
        if BOX_MAP[row][col].collidepoint(x,y):
            box_tracker[row][col].append(agent)
            agent.box=(row,col)
            return
    #This should never happen
    print("could not find new box")
# In[5]:


def move_agents():
    global box_tracker
    box_tracker= [([[]] * BIN_NUM_COLLUMS) for row in range(BIN_NUM_ROWS)]
    utility_tracker.append((len(utility_tracker)+WIDTH-INFO_WIDTH,HEIGHT-(get_utility()/initial_utility)*100))
    utility_grapher.append(HEIGHT-(get_utility()/initial_utility)*100)
    for agent in agent_list:
        r,c = agent.box

        agent.move()
        for other_agent in get_nearby_agents(r,c):
            if agent.collision(other_agent):
                agent.bounce(other_agent)

                if random.getrandbits(1):
                    other_agent.trade(agent,num_goods_to_trade,settings["show_trade"])
                else:
                    agent.trade(other_agent,num_goods_to_trade,settings["show_trade"])
                #print_total_utility()
                break
        find_new_box(agent)




def get_utility():
    utility=0
    for agent in agent_list:
        utility+=agent.get_utility()
    return utility

def draw_agents():
    for agent in agent_list:
        agent.draw()

def draw_utility_graph(Display):
    if len(utility_grapher)>1:
        line=list(zip(utility_x_cordinates,list(utility_grapher)))
        pygame.draw.lines(Display, RED, False,line, 1)

def text_objects(text, font):
    textSurface = font.render(text, True, BLACK)
    return textSurface, textSurface.get_rect()

def new_agent(Display):

    region_width=RIGTH_BORDER-LEFT_BORDER
    region_height=BOTTOM_BORDER-TOP_BORDER
    region=(LEFT_BORDER,TOP_BORDER,region_width,region_height)


    return new_agent_in_region(Display,region)


def new_agent_in_region(Display,region):
    global initial_utility
    agent=Agent.Agent(region,Display,len(agent_list),agent_settings)
    agent.box=get_box(agent)
    agent.draw()
    initial_utility+=agent.get_utility()

    return agent


def print_total_utility():
    global_utility=0
    for agent in agent_list:
        global_utility+=agent.get_utility()
    print(global_utility)


def main():
    global wait
    pygame.init()
    Display = pygame.display.set_mode((WIDTH,HEIGHT),pygame.HWSURFACE)
    #Display = pygame.display.set_mode((1920,1080),pygame.HWSURFACE|pygame.FULLSCREEN)
    Display.fill(WHITE)
    pygame.display.set_caption(TITLE)
    clock = pygame.time.Clock()

    #Text Font
    smallText = pygame.font.Font("freesansbold.ttf",20)
    text = TextBox.TextBox((BUTTON_X+2*(BUTTON_WIDTH+BUTTON_SPACE),BUTTON_Y,BUTTON_WIDTH,BUTTON_HEIGHT))

    reset_button = Button.button(BUTTON_X+BUTTON_WIDTH+BUTTON_SPACE,BUTTON_Y,LIGTH_GREY,"Reset!",smallText,Display,reset_function)
    pause_button =Button.button(BUTTON_X,BUTTON_Y,GREEN,"Start",smallText,Display,pause_function)
    step_button = Button.button(BUTTON_X+3*(BUTTON_WIDTH+BUTTON_SPACE),BUTTON_Y,GREEN,"Step",smallText,Display,step_function)
    graph_button = Button.button(BUTTON_X+4*(BUTTON_WIDTH+BUTTON_SPACE),BUTTON_Y,GREEN,"Graph",smallText,Display,graph_function)
    settings_button = Button.button(BUTTON_X+5*(BUTTON_WIDTH+BUTTON_SPACE),BUTTON_Y,GREEN,"Settings",smallText,Display,settings_function)

    button_list=[]
    button_list.append(reset_button)
    button_list.append(pause_button)
    button_list.append(step_button)
    button_list.append(graph_button)
    button_list.append(settings_button)



    #Test agents in seperate regions
    num=100
    agent_regions = divide_rect(pygame.Rect(LEFT_BORDER,TOP_BORDER,RIGTH_BORDER-LEFT_BORDER,BOTTOM_BORDER-TOP_BORDER),4,2,20)
    for i in range(num):
        for r in range(len(agent_regions)):
            for c in range(len(agent_regions[r])):
                agent_list.append(new_agent_in_region(Display,agent_regions[r][c]))


    run =True
    while run:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                run=False

            elif event.type == pygame.KEYDOWN:
                if wait:
                    #https://www.pygame.org/docs/ref/key.html
                    #press g to unpause
                    if event.key == pygame.K_g:
                        wait=False

                #Make new agents by pressing space
                if event.key == pygame.K_SPACE:
                    agent_list.append(new_agent(Display))

                #pres p to pause
                elif event.key == pygame.K_p:
                    wait=True

                #check if input box is active
                elif text.active:
                    if event.key in (pygame.K_RETURN,pygame.K_KP_ENTER):
                        for i in range(text.execute()):
                            agent_list.append(new_agent(Display))
                    #Delete last input
                    elif event.key == pygame.K_BACKSPACE:
                        if text.buffer:
                            text.buffer.pop()
                    #if input is valid (only int are) then add it to the end
                    elif event.unicode in text.ACCEPTED:
                        text.buffer.append(event.unicode)
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

                    #check if the mouse is above an agent
                    for agent in agent_list:
                        if agent.is_point_over_agent(mouse):
                            agent.is_selected=not agent.is_selected
                            if wait:
                                if agent.is_selected:
                                    agent.draw()
                                else:
                                    agent.remove_selected_circle()
                                    draw_agents()
                            break



        if wait:
            pause_button.color=GREEN
            pause_button.text="Start"
        else:

            Display.fill(WHITE)

            move_agents()
            draw_agents()
            step_button.color=GREEN
            pause_button.color=RED
            pause_button.text="Pause"
            draw_utility_graph(Display)

        #draw the buttons
        for b in button_list:
            b.draw_button()
        #draw the input box
        text.update()
        text.draw(Display)



        #60 Frames per second
        clock.tick(60)

        #update the screen
        pygame.display.flip()


    #end of loop we exit
    pygame.quit()


if __name__ == "__main__":
    main()
