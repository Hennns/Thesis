
# In[1]:

import pygame
import random
import math

from scipy import spatial


#Do this when running via atom
from Thesis import Agent
from Thesis import TextBox
from Thesis import Button
"""

#Do this when running from command line
import Agent
import Button
import TextBox
"""

#Sources
#http://usingpython.com/pygame-intro/
#https://pythonprogramming.net/pygame-python-3-part-1-intro/

#Global things
wait=True
agent_list =[]
utility_tracker=[]
initial_utility=0

# In[2]:
WIDTH= 600
HEIGHT =600
TITLE="Title"

WHITE = (255,255,255)
BLACK = (0,0,0)
RED = (255,0,0)
GREEN =(0,255,0)
LIME_GREEN=(50,205,50)
LIGTH_GREY = (211,211,211)

BUTTON_WIDTH=100
BUTTON_HEIGHT=60
BUTTON_X=20
BUTTON_Y=20
BUTTON_SPACE=10


# In[3]:


def reset_function(button):
    global agent_list
    global utility_tracker
    agent_list =[]
    utility_tracker=[]
    button.Display.fill(WHITE)


def pause_function(button):
    global wait
    wait = not wait


def step_function(button):
    global wait
    wait =True
    button.color=LIME_GREEN
    button.Display.fill(WHITE)
    move_agents()
    draw_agents()


def graph_function(button):
    global wait
    wait =True
    button.Display.fill(WHITE)
    pygame.draw.lines(button.Display, RED, False, utility_tracker, 1)
    print(utility_tracker)
    pygame.display.flip()


# In[4]:

# In[5]:

def move_agents():
    #list of dictionary of agents
    moved_agents =[]
#    cordinates=[]


    #Agent Logic
    for agent in agent_list:
        agent.move()
#            if len(cordinates) >0:
                #https://docs.scipy.org/doc/scipy/reference/generated/scipy.spatial.KDTree.query.html#scipy.spatial.KDTree.query
#                tree=spatial.KDTree(cordinates)
#                distance, index = tree.query((agent.x,agent.y),k=1,distance_upper_bound=Agent.AGENT_RADIUS*2)
#                if not math.isinf(distance):
#                    agent.bounce(moved_agents[index]['agent'])
#                    agent.trade(moved_agents[index]['agent'])

            #TODO likely not most efficient way to loop
            #KDTree is maybe faster if done rigth
        for m in moved_agents:
            if agent.collision(m['agent']):
                agent.bounce(m['agent'])
                if random.getrandbits(1):
                    m['agent'].trade(agent)
                agent.trade(m['agent'])
                #print_total_utility()
                break
        moved_agents.append({'x':agent.x,'y':agent.y,'agent':agent})
#            cordinates.append((agent.x,agent.y))
    utility_tracker.append((len(utility_tracker),HEIGHT-(get_utility()/initial_utility)*100))


def get_utility():
    utility=0
    for agent in agent_list:
        utility+=agent.get_utility()
    return utility

def draw_agents():
    for agent in agent_list:
        agent.draw()


def text_objects(text, font):
    textSurface = font.render(text, True, BLACK)
    return textSurface, textSurface.get_rect()



def new_agent(display):
    global initial_utility
    agent=Agent.Agent(BUTTON_Y+BUTTON_HEIGHT,display,len(agent_list))
    agent.draw()

    initial_utility+=agent.get_utility()
    return agent



def print_total_utility():
    global_utility=0
    for agent in agent_list:
        global_utility+=agent.get_utility()
    print(global_utility)


def main():
    pygame.init()
    Display = pygame.display.set_mode((WIDTH,HEIGHT),pygame.HWSURFACE)
    #Display = pygame.display.set_mode((1920,1080),pygame.HWSURFACE|pygame.FULLSCREEN)
    Display.fill(WHITE)
    pygame.display.set_caption(TITLE)
    clock = pygame.time.Clock()

    #Text Font
    smallText = pygame.font.Font("freesansbold.ttf",20)

    text = TextBox.TextBox((BUTTON_X+2*(BUTTON_WIDTH+BUTTON_SPACE),BUTTON_Y,BUTTON_WIDTH,BUTTON_HEIGHT))

    #Make the buttons
    reset_button = Button.button(BUTTON_X+BUTTON_WIDTH+BUTTON_SPACE,BUTTON_Y,LIGTH_GREY,"Reset!",smallText,Display,reset_function)
    pause_button =Button.button(BUTTON_X,BUTTON_Y,GREEN,"Start",smallText,Display,pause_function)
    step_button = Button.button(BUTTON_X+3*(BUTTON_WIDTH+BUTTON_SPACE),BUTTON_Y,GREEN,"Step",smallText,Display,step_function)
    graph_button = Button.button(BUTTON_X+4*(BUTTON_WIDTH+BUTTON_SPACE),BUTTON_Y,GREEN,"Graph",smallText,Display,graph_function)

    #put all the buttons in a list
    button_list =[]
    button_list.append(reset_button)
    button_list.append(pause_button)
    button_list.append(step_button)
    button_list.append(graph_button)

    run =True
    global wait


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
