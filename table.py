from deck import Deck

class Table:

    def __init__(self, players):   #   TODO    maybe i should put table instance here? (meaning init right away)
        """players should be passed in a list"""

        self.common_cards = []
        self.all_players = [player for player in players]
        self.active_players = self.all_players
        self.initial_order = self.all_players
        self.pot = 0
        self.side_pots = {}
        self.big_blind = 0  #   TODO make it foolproof? it should be only even numbers, preferably multiplicity of ten
        self.cycle = 0
        self.dealer = self.all_players[0]  #  TODO possibly better if random


    def add_flop(self, source_deck):
        for i in range(3):
            self.add_card(source_deck)


    def add_card(self, source_deck):
        new_card = source_deck.draw_card()
        self.common_cards.append(new_card)

    def clear_table(self):
        self.common_cards = []

