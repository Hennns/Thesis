
from random import random
from collections import deque


from ColorDefinitions import *


class Market:

    def __init__(self, region, color, settings, num_data_points):
        self.color = color
        self.is_selected = False
        self.region = region
        self.price = 0
        self.price_oranges = 0
        self.num_trades = 1
        self.agents = []
        self.settings = settings.copy()
        #need to use copy since settings is just the defualts settings and we
        #do not want to change defaults when changeing the settings in a market
        self.utility_tracker = deque(maxlen = num_data_points)
        self.price_tracker = deque(maxlen = num_data_points)

    def get_price(self):
        if self.num_trades > 1:
            self.num_trades - 1
        return self.price / self.num_trades


    def trade(self, agent, other_agent):
        show_trade = self.settings["show trade"]

        before_trade_utility_agent = agent.get_utility()
        before_trade_utility_other_agent = other_agent.get_utility()

        traded = self.attempt_trade(agent, other_agent)

        #This can be removed! TODO
        if agent.get_utility() <before_trade_utility_agent:
            print("MATH ERROR, agent")
            print("after", agent.get_utility())
            print("before", before_trade_utility_agent)

        if other_agent.get_utility() <before_trade_utility_other_agent:
            print("MATH ERROR, other agent")
            print("after", other_agent.get_utility())
        #remove for speed up!! TODO

        if show_trade:
            if traded:
                agent.color = LIME_GREEN
                other_agent.color = LIME_GREEN
            else:
                agent.color = RED
                other_agent.color = RED


    #always trade 1 apple
    def attempt_trade(self, agent, other_agent):
        mrs_agent = agent.get_mrs_apples()
        mrs_other_agent = other_agent.get_mrs_apples()


        #Agent want apples more than other agent
        if mrs_agent > mrs_other_agent:
            if random() < 0.5:
                return self.trade_apple_for_oranges(agent, other_agent)
            return self.trade_orange_for_apple(other_agent, agent)
        if mrs_agent == mrs_other_agent:
            return False

        #other_agent want apples more than agent
        if random() < 0.5:
            return self.trade_apple_for_oranges(other_agent, agent)
        return self.trade_orange_for_apple(agent, other_agent)


    #trade 1 apple for the lowest number of oranges
    def trade_apple_for_oranges(self, agent, other_agent):
        #Can't trade of the other agent cannot give away 1 apple
        if other_agent.apples < 1:
            return False

        price = 0
        agent_old_utility = agent.get_utility()
        other_agent_old_utillity = other_agent.get_utility()
        other_agent.apples -= 1
        agent.apples += 1

        def reset():
            other_agent.apples += 1
            agent.apples -= 1
            other_agent.oranges -= price

        while other_agent.get_utility() < other_agent_old_utillity:
            price += 1
            other_agent.oranges += 1
            if agent.oranges -price < 0:
                #agent does not have enough oranges to trade
                reset()
                return False
        agent.oranges -= price

        if agent_old_utility < agent.get_utility():
            self.price += price
            self.num_trades += 1
            return True
        #There is no price where both agents are no worse of
        agent.oranges += price
        reset()
        return False




    #opposite of above function
    #trade 1 orange for the lowest number of apples
    def trade_orange_for_apple(self, agent, other_agent):
        #Can't trade of the other agent cannot give away 1 orange
        if other_agent.oranges < 1:
            return False

        price = 0
        agent_old_utility = agent.get_utility()
        other_agent_old_utillity = other_agent.get_utility()
        other_agent.oranges -= 1
        agent.oranges += 1

        def reset():
            other_agent.oranges += 1
            agent.oranges -= 1
            other_agent.apples -= price

        while other_agent.get_utility() < other_agent_old_utillity:
            price += 1
            other_agent.apples += 1
            if agent.apples -price < 0:
                #agent does not have enough apples to trade
                reset()
                return False
        agent.apples -= price

        if agent_old_utility < agent.get_utility():
            self.price += price
            self.num_trades += 1
            return True
        #There is no price where both agents are no worse of
        agent.apples += price
        reset()
        return False




    def get_utility(self):
        utility = 0
        for agent in self.agents:
            utility += agent.get_utility()
        return utility
