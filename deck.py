# naming convention:
# a card is represented as a tuple consisting of its suit and rank
# four card suits : clubs - C, hearts - H, diamonds - D, spades - S
# thirteen ranks : corresponding numbers, jack - J, Queen - Q, King - K, Ace - A
from card import Card
from itertools import product
from random import shuffle


class Deck:
    LIST_OF_SUITS = ['C', 'H', 'D', 'S']
    LIST_OF_RANKS = list(range(2, 11)) + ['J', 'Q', 'K', 'A']
    LIST_OF_CARDS = list(product(LIST_OF_SUITS, LIST_OF_RANKS))

    def __init__(self):
        self.current_deck = self.LIST_OF_CARDS
        shuffle(self.current_deck)

    def draw_card(self):
        suits, rank = list(self.current_deck.pop(0))
        card = Card(suits, rank)
        return card

    def shuffle(self):
        self.__init__()

    def get_flop(self):
        return[self.draw_card() for i in range(3)]


