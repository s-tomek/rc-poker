from deck import Deck
from hand_check import Hand_Check
from player import Player
from best_player import Best_Player
from roundmanager import RoundManager
from table import Table
import os


def main():
    game = Game()
    game.set_parameters()
    components = game.set_game()
    game.play(*components)


class Game:

    def __init__(self):

        self.players = []
        self.starting_sum = 0
        self.big_blind = 0
        self.blind_increase = 0
        self.mode = None

    def set_parameters(self):
        name_list = self.get_players()
        self.get_sum()
        self.get_big_blind()
        self.get_mode()
        self.init_players(name_list)

    def get_players(self):

        os.system("clear")
        print("CHOOSE PLAYERS")
        name_list = []
        for i in range(8):
            name = input("Type in players name, or click Enter to proceed : ")
            if name:
                name_list.append(name)
            else:
                if name_list:
                    break
                else:
                    continue
        return name_list

    def get_sum(self):

        os.system("clear")
        print("CHOOSE STARTING SUM FOR PLAYER (max 100 000):", end="")
        while 1 > self.starting_sum or self.starting_sum > 100000:
            try:
                self.starting_sum = int(input(""))
            except ValueError:
                pass

    def get_big_blind(self):

        os.system("clear")
        while 1 > self.big_blind or self.big_blind > self.starting_sum\
                or self.big_blind % 10 != 0:
            try:
                print("CHOOSE BIG BLIND SUM:", end="")
                self.big_blind = int(input(""))
            except ValueError:
                pass
        while 1 > self.blind_increase or self.blind_increase > 20:
            try:
                print("CHOOSE AFTER HOW MANY ROUNDS THE BLIND INCREASES(max 20):", end="")
                self.blind_increase = int(input(""))
            except ValueError:
                pass

    def get_mode(self):

        os.system("clear")
        possible_decisions = ["t", "c"]
        dec = None
        while dec not in possible_decisions:
            print('TYPE "t" FOR TRANSPARENT MODE AND "c" FOR COVERED MODE:', end="")
            dec = input("")
        if dec == "c":
            self.mode = "covered"
        elif dec == "t":
            self.mode = "transparent"

    def init_players(self, name_list):
        for name in name_list:
            name = Player(name, self.starting_sum)
            self.players.append(name)

    def set_game(self):

        deck = Deck()
        hand_check = Hand_Check()
        best_pl = Best_Player()
        table = Table(self.players, self.big_blind, self.blind_increase)
        r_man = RoundManager(self.mode)
        os.system("clear")
        print("game ready, click Enter to start", end="")
        input("")
        return deck, table, r_man, best_pl, hand_check

    def play(self, deck, table, r_man, best_pl, hand_check):

        for i in range(1000):
            r_man.new_cycle(deck, table)
            r_man.pre_flop(table)
            r_man.flop(deck, table)
            r_man.turn(deck, table)
            r_man.river(deck, table, best_pl, hand_check)


if __name__ == "__main__":
    main()
