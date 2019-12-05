"""
A computer player extends a (human) player with a fixed policy.
"""
from policy import FixedPolicy, RandomPolicy
from player import Player
from collections import defaultdict

class ComputerPlayer(Player):
    def __init__(self, i, game_info):
        super().__init__(i, game_info) # Call parent constructor
        self.type = 'Computer'
        self.policy = RandomPolicy()


    #TODO: add method to extract all state
    #TODO: figure out how to get table/other player info in here
    # Right now, cannot reason about other players, only game state (table) and self
    def extractFeatures():
        table = self.game.table
        state = defaultdict(float)
        
        ###### Features about the player. ######
        hand, draw_pile, discard_pile = (player.hand, 
            player.deck.draw_pile, player.deck.discard_pile)
        
        # Variable for number of each card in hand
        money = 0
        for card in hand:
            key = (card.name, "N in Hand")
            state[key] += 1
            if card.type == CARD_TYPES.TREASURE:
                money += card.treasure_value
        
        # Variable for total money in hand
        state["Total Money In Hand"] = money

        # Variable for card in each position in hand
        for i in range(len(hand)):
            key = ("Card at index", i, hand[i].name)

        ###### Features about the supply. ######
        kingdom = table.kingdom
        
        # Indicator variables for the cards in the kingdom
        for card in kingdom:
            key = (card.name, "In Kingdom?")
            state[key] = 1

        # Variable for number of each card in the supply
        for card in table.keys():
            key = (card.name, "N in Supply")
            state[key] = table.get(card)

        ###### Features about other players. ######

        # Variable for total VP in deck of each player
        return state

    #TODO: fix execute action, action_phase, buy_phase by replacing choose
    def choose(self, choice_set, **kwargs):
        return self.policy.get_next_action(choice_set, None) #TODO: extract current state
