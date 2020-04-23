from deck import Deck
from card import Card

class Player:

    def __init__(self, name= None):
        self.name = name
        self.hand = []
        self.personal_money = 0
        self.betted_money = 0
        self.all_in = False

    def draw_hand(self, current_deck):
        self.clear_hand()
        for i in range(2):
            self.hand.append(current_deck.draw_card())

    def clear_hand(self):
        self.hand = []


