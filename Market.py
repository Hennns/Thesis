
from ColorDefinitions import *
from sympy import Symbol, solve

class Market:


    def __init__(self,region,color):
        self.color = color
        self.is_selected = False
        self.region = region
        self.price = 0
        self.price_oranges = 0
        self.num_trades = 1
        self.agents = []


    def get_price(self):
        if self.num_trades >1:
            self.num_trades-1
        return self.price/self.num_trades


    def trade(self,agent,other_agent,num_goods_to_trade,show_trade):

        before_trade_utility_agent = agent.get_utility_cobb_douglass()
        before_trade_utility_other_agent = other_agent.get_utility_cobb_douglass()


        traded = self.cobb_douglass_trade(agent,other_agent)



        if agent.get_utility_cobb_douglass() <before_trade_utility_agent:
            print("MATH ERROR, agent")
            print("after",agent.get_utility_cobb_douglass())
            print("before",before_trade_utility_agent)

        if other_agent.get_utility_cobb_douglass() <before_trade_utility_other_agent:
            print("MATH ERROR, other agent")
            print("after",other_agent.get_utility_cobb_douglass())

        if show_trade:
            if traded:
                agent.color=LIME_GREEN
                other_agent.color=LIME_GREEN
                #self.print_info()
                #other_agent.print_info()
            else:
                agent.color=RED
                other_agent.color=RED


    #always trade 1 apple
    def cobb_douglass_trade(self, agent, other_agent):
        mrs_agent = self.get_mrs_apples(agent)
        mrs_other_agent = self.get_mrs_apples(other_agent)


        #Agent want apples more than other agent
        #if self.get_mrs_apples(agent) > self.get_mrs_oranges(other_agent):
        if mrs_agent > mrs_other_agent:
            return self.trade_apple_for_oranges(agent, other_agent)
        if mrs_agent == mrs_other_agent:
            return False

        #other_agent want apples more than agent
        return self.trade_apple_for_oranges(other_agent, agent)



    #cobb_douglass
    def trade_apple_for_oranges(self, agent, other_agent):
        #Can't trade of the other agent cannot give away 1 apple
        if other_agent.apples < 1:
            return False

        price = 0
        agent_old_utility = agent.get_utility_cobb_douglass()
        other_agent_old_utillity = other_agent.get_utility_cobb_douglass()
        other_agent.apples -= 1
        agent.apples += 1

        def reset():
            other_agent.apples += 1
            agent.apples -= 1
            other_agent.oranges -= price

        #Use do-while loop???
        while other_agent.get_utility_cobb_douglass() < other_agent_old_utillity:
            price += 1
            other_agent.oranges += 1
            if agent.oranges -price < 0:
                #agent does not have enough oranges to trade
                reset()
                return False

        agent.oranges -= price


        if agent_old_utility < agent.get_utility_cobb_douglass():
            self.price += price
            self.num_trades += 1
            return True
        #There is no price where both agents are no worse of
        agent.oranges += price
        reset()
        return False

#Is try except the best approach here?

    #Number of oranges willing to trade for 1 apple
    def get_mrs_apples(self,agent):
        try:
            return (agent.pref_apples * agent.oranges) / (agent.pref_oranges * agent.apples)
        except ZeroDivisionError:
            #print("Can't devide by 0")
            #agent.print_info()
            return 0

    #number of apples willing to trade for 1 orange
    def get_mrs_oranges(self,agent):
        try:
            return (agent.pref_oranges * agent.apples) /(agent.pref_apples * agent.oranges)
        except ZeroDivisionError:
            #print("Can't devide by 0")
            #agent.print_info()
            return 0


    def get_utility(self):
        utility = 0
        for agent in self.agents:
            utility += agent.get_utility_cobb_douglass()
        return utility
