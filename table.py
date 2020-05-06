from deck import Deck
import random


class Table:


    def __init__(self, players, big_blind, blind_inc):
        """
        Table instance stores variables of an ongoing game, all the modifications are made
        by RoundManager
        """

        self.common_cards = []
        self.all_players = [player for player in players]
        self.active_players = self.all_players
        self.initial_order = self.all_players
        self.not_all_inned_pls = self.all_players
        self.pot = 0
        self.side_pots = {}
        self.big_blind = big_blind  #   TODO make it foolproof? it should be only even numbers, preferably multiplicity of ten
        self.how_often_b_blind_inc = blind_inc
        self.cycle = 0
        self.dealer = self.all_players[random.randint(0, len(self.all_players) - 1)]

    def add_flop(self, source_deck):
        for i in range(3):
            self.add_card(source_deck)

    def add_card(self, source_deck):
        self.common_cards.append(source_deck.draw_card())

    def clear_table(self):
        self.common_cards = []
        self.side_pots = {}

