import deck
from table import Table
from card import Card
import os

class RoundManager:

    def __init__(self):
        self.is_check_allowed = False
        self.betting_round = None
        self.last_raising_pl = None


    def new_cycle(self, deck, table):
        self.eliminate_broke_players(table)
        table.side_pots = {}
        deck.shuffle()
        table.cycle += 1
        if table.cycle > 1:  #  TODO not important, refactor? refactor if dealer is randomly chosen at firsts
            self.next_dealer(table)
        table.clear_table()
        table.active_players = table.all_players
        self.players_in_order(table)
        for player in table.all_players:
            player.all_in = False
            player.clear_hand()
            player.draw_hand(deck)
        # testing
        p1 = table.all_players[0]
        p2 = table.all_players[1]
        c1 = Card("D","J")
        c2 = Card("S",10)
        p1.hand = [c1,c2]
        p2.hand = [c1,c2]


    def pre_flop(self, table):

        self.players_in_pre_flop_order(table)
        self.add_blinds(table)
        self.is_check_allowed = False
        self.betting_round = "pre flop"
        self.betting(table, minimal_bet=table.big_blind, preflop=True)
        self.money_to_pot(table)
        self.players_in_order(table)

    def flop(self, deck, table):
        if len(table.active_players) == 1:
            return 0
        self.betting_round = "flop"
        if not self.proceed_with_all_ins(deck, table):
            self.is_check_allowed = True
            table.common_cards = deck.get_flop()
            self.betting(table)
        self.money_to_pot(table)
        print(table.side_pots)

    def turn(self, deck, table):
        if len(table.active_players) == 1:
            return 0
        self.betting_round = "turn"
        if not self.proceed_with_all_ins(deck, table):
            self.is_check_allowed = True
            table.common_cards.append(deck.draw_card())
            self.betting(table)
        self.money_to_pot(table)


    def river(self, deck, best_player, hand_check, table):
        if len(table.active_players) == 1:
            fold_winner = table.active_players[0]
            self.the_winner_takes_it_all(best_player, hand_check, table)  # in case all but one player folded before river
            self.display_for_end(fold_winner, table, after_fold=True)
            self.click_to_proceed()
            return 0
        self.betting_round = "river"
        self.is_check_allowed = True
        if not self.proceed_with_all_ins(deck, table):
            table.common_cards.append(deck.draw_card())
            self.betting(table)
        self.money_to_pot(table)
        if len(table.active_players) == 1:
            fold_winner = table.active_players[0]
            self.display_for_end(fold_winner, table, after_fold=True)  # in case all but one player folded during river
        winners = self.the_winner_takes_it_all(best_player, hand_check, table)  # side effect: the pot is transferred to winners
        showing_players = self.whos_showing_cards(table, best_player, hand_check)
        self.display_for_end(winners, table, showing_players=showing_players)
        self.click_to_proceed()

    def betting(self, table, minimal_bet = None, preflop=False):
        ready_for_next_round = False
        initial_amount_of_p = len(table.active_players)
        count = 0  # counts how many players made their move, everyone has to take action in each round.
        if not minimal_bet:  # present when it's pre-flop because of the big blind
            minimal_bet = 1
        self.last_raising_pl = [pl for pl in table.active_players if pl.all_in == False][0]
        while not ready_for_next_round:
            players_for_one_loop = table.active_players.copy()  #  TODO learn for yourself, can you change the list while iterating over it
            for player in players_for_one_loop:
                if len([pl for pl in table.active_players if pl.all_in == False]) == 1 and self.is_end_of_betting(table):  #TODO it shouldn't be ready for next round!!
                    ready_for_next_round = True
                    # self.last_raising_pl = player  # TODO should it be here?
                    break
                count += 1
                if player.all_in is False:
                    self.display_for_player(table, player)
                    if preflop == True and count == initial_amount_of_p and self.is_end_of_betting(table):
                        self.is_check_allowed = True
                    print(f"count : {count}")
                    decision = self.get_decision()
                    self.player_action(table, player, decision, minimal_bet)
                    if player.betted_money > minimal_bet: #   TODO refactor?
                        minimal_bet = player.betted_money
                    # print(f"count: {count} init pl: {initial_amount_of_p}")
                if self.is_end_of_betting(table) and count >= initial_amount_of_p:  #second condition is set to allow all players check and in pre flop it allows big blind to bet
                    ready_for_next_round = True
                    break

    def money_to_pot(self, table):
        """if no all-ins were made this round it transfers money from
        players to pot, in case of all ins it additionally creates side pots,
        which are dictionary key/value pairs where key is the number of sidepot, in order of creation
        and value is a tuple consisting of the sidepot sum and players entitled for the sidepot"""
        #
        # if [pl for pl in table.active_players if (pl.all_in == True and pl.betted_money != 0)] == []:
        #     for player in table.all_players:
        #         table.pot += player.betted_money
        #         player.betted_money = 0
        # else:
        # in case of all-ins in this round, this part creates side pots
              # works! TODO decide to let or not let the last player overbet, probably dont let him?
        while [pl for pl in table.active_players if (pl.all_in == True and pl.betted_money != 0)] != []:
            # print("creating sidepot")
            pl_list_for_side_pots = [pl for pl in table.active_players if pl.betted_money > 0]
            lowest_better = min(pl_list_for_side_pots, key=lambda pl: pl.betted_money)
            lowest_bet = lowest_better.betted_money
            side_pot = 0
            side_pot += table.pot
            table.pot = 0
            for pl in table.all_players:
                if pl.betted_money >= lowest_bet:
                    pl.betted_money -= lowest_bet
                    side_pot += lowest_bet
                else:
                    side_pot += pl.betted_money
                    pl.betted_money = 0
            value = (side_pot, pl_list_for_side_pots)
            # print({len(table.side_pots) + 1 : value})
            #  table.pot += side_pot
            table.side_pots.update({len(table.side_pots) + 1 : value})
            # pl_list_for_side_pots = [pl for pl in pl_list_for_side_pots if pl.betted_money > 0]
        for player in table.all_players:
            table.pot += player.betted_money
            player.betted_money = 0



    def the_winner_takes_it_all(self, best_player, hand_check, table,):
        """takes the table instance, best player and needed for best player
        hand check. Firstly, it asseses if a split is needed, then
        moves money from table.pot to player.personal_money.
        returns winners as dictionary, the same as best_player function, unless  # TODO return winners as list? cause sometimes its from multiple hand checks
        everyone folded, then it returns 0"""  #  TODO maybe refactor? should it return 0?
        # if after_fold == True:
        #     fold_winner.personal_money += table.pot  # TODO change so it takes side pots into account
        #     table.pot = 0
        #     return 0  # TODO sometimes afterfold but still competes with all ins
        #  should transfer sidepots one by one (only to active players!) and then the remaining pot to just active, but not all inned players
        winners_dict = {}
        if table.side_pots:
            for side_pot_number in table.side_pots.keys():
                side_pot_sum = table.side_pots[side_pot_number][0]
                competing_players = [pl for pl in table.side_pots[side_pot_number][1] if pl in table.active_players]
                side_winners_dict = best_player.get_best_player(hand_check, table.common_cards, *competing_players)
                for pl in list(side_winners_dict.keys()):
                    print(f"{pl.name} shares sidepot {side_pot_number} of {side_pot_sum}")
                self.distribute_money(table, side_winners_dict, side_pot_sum)
                winners_dict.update(side_winners_dict)
        if table.pot > 0:
            competing_players = [pl for pl in table.active_players if pl.all_in == False]
            after_all_in_winners_dict = best_player.get_best_player(hand_check, table.common_cards, *competing_players)
            self.distribute_money(table, after_all_in_winners_dict, table.pot)
            table.pot = 0
            winners_dict.update(after_all_in_winners_dict)
        return winners_dict





        # winners_dict = best_player.get_best_player(hand_check,table.common_cards, *table.active_players)
        # if len(winners_dict) > 1:
        #     self.split(table, winners_dict)
        # else:
        #     winner = list(winners_dict.keys())[0]
        #     winner.personal_money += table.pot
        #     table.pot = 0
        # table.pot = 0  # TODO leave remaining one or two on the table?
        # return winners_dict

    def distribute_money(self,table, winners_dict, pot):
        if len(winners_dict) > 1:
            self.split(table, winners_dict, pot)
        else:
            winner = list(winners_dict.keys())[0]
            winner.personal_money += pot

    def split(self, table, winners_dict, pot):  # TODO it rounds up the pot, so it splits to integers
        winners = list(winners_dict.keys())
        pot = pot - pot % len(winners)
        pot_part = int(pot / len(winners))
        for p in winners:
            p.personal_money += pot_part


    def get_bet(self, player, amount):
        player.personal_money -= amount
        player.betted_money += amount

    def get_decision(self):
        possible_actions = ['c', 'f', 'r']
        if not self.is_check_allowed:
            possible_actions.remove('c')
        decision = None
        while decision not in possible_actions:
            decision = input("Type c(check) f(fold) or r(raise): ")
        return decision

    def player_action(self, table, player, decision, minimal_bet):
        if decision == 'f':
            # print(f"removed player: {player.name}")
            table.active_players.remove(player)
        elif decision == 'c':
            pass
        elif decision == 'r':  #  TODO  (done, but requires testing) include all in
            amount = 0
            #  rules out repectively a player betting under the minimal bet (set by the last bet of the previous player)
            #  unless it's an all in, then it can be under the minimal bet. next it includes situation, when all betted
            #  money is equal, but still the player can make a decision, that's only when big blind can raise at the end
            #  betting in pre-flop. Lastly, the amount cannot be higher than the sum a player owns.

            #TODO line below, amount != personal money escapes some instances so you can bet under the minimal bet
            while ((player.betted_money + amount) < minimal_bet and amount != player.personal_money) or \
                  (player.betted_money + amount) <= player.betted_money or \
                   amount > player.personal_money:
                amount = int(input("how much do you bet: "))
            self.get_bet(player, amount)
            if player.betted_money > self.last_raising_pl.betted_money:
                self.last_raising_pl = player
            if player.personal_money == 0:  # TODO should a player after all in be the highest raiser
                player.all_in = True
            self.is_check_allowed = False

    def display_for_player(self, table, player):  #TODO use print("...", end="") to print in the same line if needed

        # for p in table.all_players:
        #     print(f"{p.name}'s index: {table.all_players.index(p)}")

        os.system("clear")
        print(f"cycle : {table.cycle}")
        print(f"betting round : {self.betting_round}")
        print(f"\npot : {table.pot}")
        if table.side_pots:
            for side_pot_nr in list(table.side_pots.keys()):
                print(f"sidepot {side_pot_nr} : {table.side_pots[side_pot_nr][0]}")
        print(f"{player.name}'s turn\n")
        list2 = []
        for card in player.hand:
            list2.append([card.suits, card.rank])
        print(f"{player.name}'s cards: {list2}")
        list1 = []
        for card in table.common_cards:
            list1.append([card.suits, card.rank])
        print(f"common cards: {list1}\n")
        for p in table.initial_order:
            if p == table.dealer:
                d = "D"
            else:
                d = " "
            if p in table.all_players:
                if p in table.active_players:  #TODO refactor to not repeat code
                    print(f"{d} active   {p.name} with {p.personal_money} betted {p.betted_money} this round")
                else:
                    print(f"{d} inactive {p.name} with {p.personal_money} betted {p.betted_money} this round")


    def display_for_end(self, winners, table, showing_players=None, after_fold=False): # TODO test for two winners, should work
        """displays information available to all players at the end
        of the cycle. If after_fold is True, meaning all but one player
        folded, no cards are shown, and only common cards from the round
        the cycle has ended are shown. If after_fold is True, the parameter
        winners is a single Player instance instead of a dictionary of winners with confiurations"""

        os.system("clear")
        list0 = []
        for pl in showing_players:
            list0.append(pl.name)
        print(list0)
        list1 = []
        for card in table.common_cards:
            list1.append([card.suits, card.rank])
        print(f"common cards: {list1}")
        if after_fold == False:
            for p in table.initial_order:  #  TODO has to be changed to: whos_showing_cards, also suitable for multiple sidepots
                if p in table.active_players:
                    list2 = []
                    for card in p.hand:
                        list2.append([card.suits, card.rank])
                    print(f"{p.name} with {p.personal_money} with cards: {list2 if p in showing_players else '--'} " +\
                            f"{f'has {winners[p][1]} and won this round' if p in winners.keys() else 'lost this round'}")
                elif p in table.all_players:
                    print(f"{p.name} with {p.personal_money} with cards: -- lost this round")
        if after_fold == True:
            for p in table.initial_order:
                if p == winners: # in this case winners is a Player instance and not a dictionary
                    print(f"{p.name} with {p.personal_money} won this round")
                else:
                    print(f"{p.name} with {p.personal_money} lost this round")


    def whos_showing_cards(self, table, best_player, hand_check ):  #TODO a player showed cards even though he wasnt among the winners!
        """return a list of players, that should show their cards,
        because they are competing for the main pot and all players competing
        for side pots, if applicable"""

        showing_pls = [self.last_raising_pl]
        remaining_to_show = [pl for pl in table.active_players if pl.all_in is False]
        print("rem to show:")
        for pl in remaining_to_show:
            print(pl.name)
        print(f"last raising: {self.last_raising_pl.name}")
        try:
            ix = remaining_to_show.index(self.last_raising_pl)  # last raising should never be folded or be all in, by definition unless the first betting player folds and the rest checks
            remaining_to_show = remaining_to_show[ix + 1:] + remaining_to_show[:ix]
        except ValueError:
            pass
        if remaining_to_show != []:
            for pl in remaining_to_show:
                winners = best_player.get_best_player(hand_check, table.common_cards, *showing_pls, pl)
                if pl in list(winners.keys()):
                    showing_pls.append(pl)
        if table.side_pots:
            for value in list(table.side_pots.values()):
               showing_pls.extend(value[1])
        showing_pls = list(set(showing_pls))
        return showing_pls




    def is_end_of_betting(self, table):  #TODO prepare for all players all in with the same amount
        not_all_in_bets = [player.betted_money for player in table.active_players if player.all_in == False]
        if len(set(not_all_in_bets)) > 1:
            return False
        for player in table.active_players:
            if player.all_in == True and player.betted_money > not_all_in_bets[0]:
                return False
        return True
        # for player in table.active_players:
        #     if player.all_in == False:
        #         if table.active_players[0].betted_money != player.betted_money:
        #         # print(f"{table.active_players[0].name}'s bet is different than {player.name}'s bet")
        #             return False
        #         # print(f"{table.active_players[0].name}'s bet is same as {player.name}'s bet")
        #     elif player.all_in == True:

        # print("all bets same")
        # return True

    def next_dealer(self, table):
        current_dealers_index = table.initial_order.index(table.dealer)
        table.dealer = None
        while table.dealer not in table.all_players:
            if current_dealers_index == len(table.initial_order) - 1:
                current_dealers_index = 0
            else:
                current_dealers_index += 1
            table.dealer = table.initial_order[current_dealers_index]

    def players_in_order(self, table,):
        """changes list of table.active players and table.all_players
        in order  ending with the dealer. This function is used after the
        function next_dealer to update the order of players"""

        current_dealers_index = table.all_players.index(table.dealer)
        table.all_players = table.all_players[current_dealers_index + 1:] + table.all_players[:current_dealers_index + 1]
        table.active_players = [pl for pl in table.all_players if pl in table.active_players]

    def players_in_pre_flop_order(self, table):
        """changes the active_players to preflop
        order that is starting from the third player after the dealer
        if there are only two players left the order in preflop doesn't change"""

        self.players_in_order(table)
        if len(table.active_players) > 2:
            table.active_players = table.all_players[2:] + table.all_players[:2]

    def add_blinds(self, table):
        current_dealers_index = table.active_players.index(table.dealer)
        if current_dealers_index < len(table.active_players) - 2:
            small_blind = table.active_players[current_dealers_index +1]
            big_blind = table.active_players[current_dealers_index + 2]
        elif current_dealers_index == len(table.active_players) - 2:
            small_blind = table.active_players[current_dealers_index + 1]
            big_blind = table.active_players[0]
        elif current_dealers_index == len(table.active_players) - 1:
            small_blind = table.active_players[0]
            big_blind = table.active_players[1]
        self.get_bet(small_blind, int(table.big_blind/2))
        self.get_bet(big_blind, table.big_blind)

    def eliminate_broke_players(self, table):
        table.all_players = [player for player in table.all_players if player.personal_money > 0]

    def proceed_with_all_ins(self, deck, table):
        """as a side effect it draws cards, TODO maybe refactor?
        returns True if all but one player did all-ins"""

        if len([player for player in table.active_players if player.all_in == False]) == 1:
            if self.betting_round == "flop":
                table.common_cards = deck.get_flop()
            else:
                table.common_cards.append(deck.draw_card())
            return True
        return False

    def click_to_proceed(self):
        input("Click Enter to proceed")
