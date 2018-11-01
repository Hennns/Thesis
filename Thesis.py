
# coding: utf-8

#TODO other code impovments

# In[1]:


import pygame
from pygame.locals import *
import random
import math
import string
from Thesis import Agent
from Thesis import TextBox
from Thesis import Button


#Sources
#http://usingpython.com/pygame-intro/
#https://pythonprogramming.net/pygame-python-3-part-1-intro/

#Global things
clock = pygame.time.Clock()
wait=False
agent_list =[]


# In[2]:

#Constants Box

WIDTH= 500
HEIGHT =500
TITLE="Title"

WHITE = (255,255,255)
BLACK = (0,0,0)
RED = (255,0,0)
GREEN =(0,255,0)
LIME_GREEN=(50,205,50)

BUTTON_WIDTH=100
BUTTON_HEIGHT=60
BUTTON_X=20
BUTTON_Y=20
BUTTON_SPACE=10


ACCEPTED = string.digits


# In[3]:



def go_function(button):
    button.color=LIME_GREEN
    agent_list.append(new_agent(button.Display))

def stop_function(button):
    global wait
    wait=True


# In[4]:

# In[5]:

def text_objects(text, font):
    textSurface = font.render(text, True, BLACK)
    return textSurface, textSurface.get_rect()




def new_agent(display):
    print(type(display))
    print(display.get_size)

    return Agent.Agent(BUTTON_Y+BUTTON_HEIGHT,display)


def main():
    pygame.init()
    Display = pygame.display.set_mode((WIDTH,HEIGHT))
    pygame.display.set_caption(TITLE)

    #Text Font
    smallText = pygame.font.Font("freesansbold.ttf",20)
    largeText = pygame.font.Font("freesansbold.ttf",50)

    text = TextBox.TextBox((BUTTON_X+2*(BUTTON_WIDTH+BUTTON_SPACE),BUTTON_Y,BUTTON_WIDTH,BUTTON_HEIGHT))

    #Make the buttons
    go_button = Button.button(BUTTON_X,BUTTON_Y,GREEN,"GO!",smallText,Display,go_function)
    stop_button = Button.button(BUTTON_X+BUTTON_WIDTH+BUTTON_SPACE,BUTTON_Y,RED,"Stop!",smallText,Display,stop_function)

    #put all the buttons in a list
    button_list =[]
    button_list.append(go_button)
    button_list.append(stop_button)


    def pause():
        paused = True
        global wait
        TextSurf, TextRect = text_objects("Paused", largeText)
        TextRect.center = ((WIDTH/2),(HEIGHT/2))
        Display.blit(TextSurf, TextRect)
        while paused:
            for event in pygame.event.get():

                if event.type == pygame.QUIT:
                    run=False
                    paused=False
                    wait=False
                    #pygame.quit()
                    #quit()
                elif event.type == pygame.KEYDOWN:
                    #https://www.pygame.org/docs/ref/key.html
                    if event.key == pygame.K_g:
                        wait=False
                        paused = False

            #TODO make button to unpause
            pygame.display.update()

    run =True
    global wait
    while run:
        if wait:
            pause()

        for event in pygame.event.get():
            if event.type == QUIT:
                run=False
            elif event.type == pygame.KEYDOWN:
                #Make new agents by pressing space
                if event.key == pygame.K_SPACE:
                    agent_list.append(new_agent(Display))

                #press p to pause game
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
                    elif event.unicode in ACCEPTED:
                        text.buffer.append(event.unicode)
            #left mouse click
            elif event.type == pygame.MOUSEBUTTONUP and event.button==1:
                #get mouse position
                mouse = pygame.mouse.get_pos()

                text.active = text.rect.collidepoint(event.pos)

                #if the mouse is above the input box it is not above anything else
                if not text.active:
                    #check if the mouse is above a button, if it is execute that button
                    for b in button_list:
                        r = pygame.Rect(b.getRect())
                        if r.collidepoint(mouse):
                            b.execute()
                            break


        #list of dictionary of agents that have moved, resets each loop
        moved_agents =[]

        #Make the display white then draw everything
        Display.fill(WHITE)


        #Agent Logic
        for agent in agent_list:
            agent.move()
            #TODO not most efficient way to loop trhough
            for m in moved_agents:
                if(agent.collision(m['agent'])):
                    agent.bounce(m['agent'])
                    agent.trade(m['agent'])
            moved_agents.append({'x':agent.x,'y':agent.y,'agent':agent})
            agent.draw()

        #draw the buttons
        for b in button_list:
            b.draw_button()

        #draw the input box
        text.update()
        text.draw(Display)

        # Limit to 60 frames per second
        clock.tick(60)

        #update the screen
        pygame.display.flip()

    #end of loop we exit
    pygame.quit()
if __name__ == "__main__":
    main()
