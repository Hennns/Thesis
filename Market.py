
from ColorDefinitions import *


class Market:


    def __init__(self,region):
        self.region = region
        self.price = 0
        self.num_trades = 1
        self.agents = []


    def get_price(self):
        if self.num_trades >1:
            self.num_trades-1
        return self.price/self.num_trades


    def trade(self,agent,other_agent,num_goods_to_trade,show_trade):
        self.num_trades += 1
        #print()
        #self.print_info()
        #other_agent.print_info()

        traded = self.cobb_douglass_trade(agent,other_agent,num_goods_to_trade)
        if show_trade:
            if traded:
                agent.color=LIME_GREEN
                other_agent.color=LIME_GREEN
                #self.print_info()
                #other_agent.print_info()
            else:
                agent.color=RED
                other_agent.color=RED



    def cobb_douglass_trade(self, agent, other_agent, num_goods_to_trade):
        """
        print(agent.id," is willing to give up ",self.get_mrs_apples(agent),
        " apples for ",self.get_mrs_oranges(agent),"oranges")
        agent.print_info()
        print()


        print(other_agent.id," is willing to give up ",self.get_mrs_apples(other_agent),
        " apples for ",self.get_mrs_oranges(other_agent),"oranges")
        other_agent.print_info()
        """

        price = self.get_mrs_apples(other_agent)

        #Agent want apples more than other agent
        if self.get_mrs_apples(agent) > price:
            price = self.get_mrs_apples(other_agent) * num_goods_to_trade

            #one of the agents does not have enough goods to trade
            if other_agent.apples-num_goods_to_trade <0 or agent.oranges-price <0:
                return False



            agent.apples+=num_goods_to_trade
            other_agent.apples-=num_goods_to_trade

            agent.oranges-=price
            other_agent.oranges+=price

            self.price += price/num_goods_to_trade
            """
            print(agent.id," is willing to give up ",self.get_mrs_apples(agent),
            " apples for ",self.get_mrs_oranges(agent),"oranges")
            agent.print_info()
            print()


            print(other_agent.id," is willing to give up ",self.get_mrs_apples(other_agent),
            " apples for ",self.get_mrs_oranges(other_agent),"oranges")
            other_agent.print_info()
            """
            return True

        elif not price == self.get_mrs_apples(agent):
            price=self.get_mrs_oranges(other_agent) * num_goods_to_trade

            if agent.apples-price <0 or other_agent.oranges-num_goods_to_trade <0:
                return False

            agent.apples-=price
            other_agent.apples+=price

            agent.oranges+=num_goods_to_trade
            other_agent.oranges-=num_goods_to_trade

            self.price += num_goods_to_trade/price
            return True
        return False

    #cobb_douglass
    def get_mrs_apples(self,agent):
        try:
            return agent.pref_apples/agent.pref_oranges * agent.oranges/agent.apples
        except ZeroDivisionError:
            agent.print_info()
    #cobb_douglass
    def get_mrs_oranges(self,agent):
        try:
            return agent.pref_oranges/agent.pref_apples * agent.apples/agent.oranges
        except ZeroDivisionError:
            agent.print_info()
