
import os


class RoundManager:

    def __init__(self, mode):
        self.mode = mode
        self.is_check_allowed = False
        self.betting_round = None
        self.last_raising_pl = None
        self.current_min_bet = 1
        self.winners_dict = {}

    def new_cycle(self, deck, table):
        """
        Starts new cycle, eliminates players, raises blinds, clears table, shuffles deck,
        changes dealer, clears players' hands.
        """

        table.cycle += 1
        table.clear_table()
        deck.shuffle()
        self.winners_dict = {}
        self.raise_blinds(table)
        self.eliminate_broke_players(table)
        if len(table.all_players) == 1:
            self.winner_display(table)
        self.next_dealer(table)
        self.players_in_order(table, new_cycle=True)
        for player in table.all_players:
            player.all_in = False
            player.clear_hand()
            player.draw_hand(deck)

    def pre_flop(self, table):
        """
        pre flop needs a special order, at the end of pre flop order gets back to normal.
        Note that big blind can raise in the end of first betting round even though everyone
        bet the same amount.
        """

        self.betting_round = "pre flop"
        self.players_in_pre_flop_order(table)
        self.add_blinds(table)
        self.is_check_allowed = False
        self.betting(table, pre_flop=True)
        self.money_to_pot(table)
        self.players_in_order(table)

    def flop(self, deck, table):

        self.betting_round = "flop"
        if len(table.active_players) == 1:
            return 0
        self.draw_cards(deck, table)
        if self.proceed_with_all_ins(table):
            return 0
        self.is_check_allowed = True
        self.current_min_bet = 1
        self.betting(table)
        self.money_to_pot(table)

    def turn(self, deck, table):

        self.betting_round = "turn"
        if len(table.active_players) == 1:
            return 0
        self.draw_cards(deck, table)
        if self.proceed_with_all_ins(table):
            return 0
        self.is_check_allowed = True
        self.current_min_bet = 1
        self.betting(table)
        self.money_to_pot(table)

    def river(self, deck, table, best_player, hand_check):

        self.betting_round = "river"
        # in case all but one player folded before river
        if len(table.active_players) == 1:
            self.ending_for_folding(table, best_player, hand_check)
            return 0
        self.is_check_allowed = True
        self.current_min_bet = 1
        self.draw_cards(deck, table)
        if not self.proceed_with_all_ins(table):
            self.betting(table)
        self.money_to_pot(table)
        if len(table.active_players) == 1:
            self.ending_for_folding(table, best_player, hand_check)
        else:
            self.the_winner_takes_it_all(best_player, hand_check, table)
            showing_players = self.whos_showing_cards(table, best_player, hand_check)
            self.display_for_end(table, showing_players=showing_players)
            self.click_to_proceed()

    def ending_for_folding(self, table, best_player, hand_check):
        self.the_winner_takes_it_all(best_player, hand_check, table)
        self.display_for_end(table, after_fold=True)
        self.click_to_proceed()

    def betting(self, table, pre_flop=False): # TODO doesnt work, went to next round without everyone betting the same
        # TODO all but one person played all in
        """
        Allows the players to bet. The function ends when (1) all players checked,
        so everyone bet the same amount, zero, and had an opportunity to make a move,
        (2) Everyone bet the same amount or (3) when all but one player, or all
         players went all in.
        """

        ready_for_next_round = False
        initial_amount_of_p = len(table.not_all_inned_pls)
        count = 0  # counts how many players made their move, everyone has to take action in each round.

        #  before calling the function there have to be at least two active, not all inned players
        #  last raising player is the one that has to show their cards first, if everyone checks,
        #  then it's the one who started final round.
        self.last_raising_pl = table.not_all_inned_pls[0]
        while not ready_for_next_round:
            players_for_one_loop = table.not_all_inned_pls.copy()
            for player in players_for_one_loop:
                # length of active players can become one within a loop
                # if a player folds instead of checking.
                if (self.is_end_of_betting(table) and count >= initial_amount_of_p) or\
                        len(table.active_players) == 1:
                    ready_for_next_round = True
                    break
                count += 1
                self.display_for_player(table, player)
                # special situation when big blind checks at the end of betting round while having bet money
                if pre_flop is True and count == initial_amount_of_p and self.is_end_of_betting(table):
                    self.is_check_allowed = True
                # betting
                decision = self.get_decision()
                self.player_action(table, player, decision)
            if self.proceed_with_all_ins(table) and self.is_end_of_betting(table):
                ready_for_next_round = True

    def money_to_pot(self, table):
        """
        if no all-ins were made this round it transfers money from
        players to pot, in case of all ins it additionally creates side pots,
        which are dictionary key/value pairs where key is the number of side-pot, in order of creation
        and value is a tuple consisting of the side-pot sum and players competing for the side-pot
        """

        # TODO decide whether the last player can over-bet, probably don't let him?
        while [pl for pl in table.active_players if (pl.all_in is True and pl.bet_money)]:
            pl_list_for_side_pots = [pl for pl in table.active_players if pl.bet_money]
            lowest_better = min(pl_list_for_side_pots, key=lambda pl: pl.bet_money)
            lowest_bet = lowest_better.bet_money
            side_pot = table.pot
            table.pot = 0
            for pl in table.all_players:
                if pl.bet_money >= lowest_bet:
                    pl.bet_money -= lowest_bet
                    side_pot += lowest_bet
                else:
                    side_pot += pl.bet_money
                    pl.bet_money = 0
            value = (side_pot, pl_list_for_side_pots)
            table.side_pots.update({len(table.side_pots) + 1: value})
        for player in table.all_players:
            table.pot += player.bet_money
            player.bet_money = 0

    def the_winner_takes_it_all(self, best_player, hand_check, table):
        # TODO it could be less repetitive
        """
        Updates self.winners_dict with winners of the current round and
        distributes money to them.
        winners_dict has players as keys, and three positions in values:
        1: configuration of relevant 5 cards
        2: name of configuration
        3: sum won this round

        If there's just one active player, so the cycle ends prematurely, the
        winners dictionary has an empty list in first position and empty
        string in second.
        """

        # assessing side pot winners and distributing money
        for side_pot_number in table.side_pots.keys():
            side_pot_sum = table.side_pots[side_pot_number][0]
            competing_players = [pl for pl in table.side_pots[side_pot_number][1] if pl in table.active_players]
            side_winners_dict = best_player.get_best_player(hand_check, table.common_cards, *competing_players)
            prize_for_one = self.distribute_money(side_winners_dict, side_pot_sum)
            for winner in side_winners_dict.keys():
                if winner not in self.winners_dict.keys():
                    self.winners_dict.update({winner: [*side_winners_dict[winner], prize_for_one]})
                else:
                    self.winners_dict[winner][2] += prize_for_one
        # main pot part
        if table.pot > 0:
            competing_players = table.not_all_inned_pls
            final_pot_winners_dict = best_player.get_best_player(hand_check, table.common_cards, *competing_players)
            prize_for_one = self.distribute_money(final_pot_winners_dict, table.pot)
            table.pot = 0
            for winner in final_pot_winners_dict.keys():
                if winner not in self.winners_dict.keys():
                    self.winners_dict.update({winner: [*final_pot_winners_dict[winner], prize_for_one]})
                else:
                    self.winners_dict[winner][2] += prize_for_one

    def distribute_money(self, winners_dict, pot):

        if len(winners_dict) > 1:
            prize_for_one = pot // len(winners_dict)
            self.split(winners_dict, pot)
        else:
            prize_for_one = pot
            winner = list(winners_dict.keys())[0]
            winner.personal_money += pot
        return prize_for_one

    def split(self, winners_dict, pot):  # TODO it rounds up the pot, check if it wont cause problems

        winners = list(winners_dict.keys())
        pot = pot - pot % len(winners)
        pot_part = int(pot / len(winners))
        for p in winners:
            p.personal_money += pot_part

    def get_bet(self, player, amount):
        player.personal_money -= amount
        player.bet_money += amount

    def get_decision(self):
        possible_actions = ['c', 'f', 'r']
        if not self.is_check_allowed:
            possible_actions.remove('c')
        decision = None
        while decision not in possible_actions:
            decision = input("Type c(check) f(fold) or r(raise): ")
        return decision

    def player_action(self, table, player, decision):
        """
        Makes changes according to players decision.
        fold: removes player from active list and not all inned list
        check: nothing happens
        raise: asks for input, then if it was equal to the previous bet, nothing happens.
        If it was over the previous bet, it changes the last_raising_pl and current_min_bet.
        Changes players all_in attribute to True if needed. Disallows checking.
        """

        if decision == 'f':
            table.active_players.remove(player)
            table.not_all_inned_pls.remove(player)
        elif decision == 'c':
            pass
        elif decision == 'r':
            amount = 0

            #  rules out respectively a player betting under the minimal bet (set by
            #  the last bet of the previous player) unless it's an all in, then it can
            #  be under the minimal bet. next it includes situation, when all bet
            #  money is equal, but still the player can make a decision, that's only
            #  when big blind can raise at the end betting in pre-flop.
            #  Lastly, the amount cannot be higher than the sum a player owns.
            while ((player.bet_money + amount) < self.current_min_bet and amount != player.personal_money) or \
                  (player.bet_money + amount) <= player.bet_money or \
                    amount > player.personal_money:
                try:
                    amount = int(input("how much do you bet: "))
                except ValueError:
                    pass
            self.get_bet(player, amount)
            if player.bet_money > self.current_min_bet:
                self.last_raising_pl = player
                self.current_min_bet = player.bet_money
            if player.personal_money == 0:
                player.all_in = True
                table.not_all_inned_pls.remove(player)
            self.is_check_allowed = False

    def display_for_player(self, table, player):

        if self.mode == "covered":
            os.system("clear")
            print(f"it's {player.name}'s turn, make sure no one else sees the screen ")
            self.click_to_proceed()
        os.system("clear")
        print(f"cycle : {table.cycle}")
        print(f"betting round : {self.betting_round}\n")
        print(f"pot : {table.pot}")
        for side_pot_nr in list(table.side_pots.keys()):
            print(f"sidepot {side_pot_nr} : {table.side_pots[side_pot_nr][0]}")
        print(f"{player.name.upper()}'S TURN\n")
        repr_of_hand = [[c.suits, c.rank] for c in player.hand]
        print(f"{player.name}'s cards: {repr_of_hand}")
        com_cards = [[c.suits, c.rank] for c in table.common_cards]
        print(f"common cards: {com_cards}\n")
        for pl in [pl for pl in table.initial_order if pl in table.all_players]:
            d = "D" if pl == table.dealer else " "
            activity = "active  " if pl in table.active_players else "inactive"
            print(f"{d} {activity} {pl.name} with {pl.personal_money} bet {pl.bet_money} this round")

    def display_for_end(self, table, showing_players=None, after_fold=False,):
        """
        displays information available to all players at the end
        of the cycle. If after_fold is True, meaning all but one player
        folded, no cards are shown, and only common cards from the round
        the cycle has ended are shown. If after_fold is True, the parameter
        fold_winner is needed, otherwise, showing_players are needed.

        If the game didn't end with folding, the function displays every player
        with their personal money, cards if they need to show them, and did they win
        or lose. If they've won, the prize is displayed.
        """

        if self.mode == "covered":
            os.system("clear")
            print("the following screen is for everyone to see")
            self.click_to_proceed()
        os.system("clear")
        com_cards = [[c.suits, c.rank] for c in table.common_cards]
        print(f"common cards: {com_cards}\n")
        if after_fold is False:
            for pl in [pl for pl in table.initial_order if pl in table.all_players]:
                repr_of_hand = [[c.suits, c.rank] for c in pl.hand]
                print(f"{pl.name} with {pl.personal_money} " +
                      f"with cards: {repr_of_hand if pl in showing_players else '--'} ", end="")
                if pl in self.winners_dict.keys():
                    print(f"has {self.winners_dict[pl][1]} and won {self.winners_dict[pl][2]} this round")
                else:
                    print('lost this round')
        else:
            for pl in table.initial_order:
                print(f"{pl.name} with {pl.personal_money} ", end="")
                if pl in self.winners_dict.keys():
                    print(f'won {self.winners_dict[pl][2]} this round')
                else:
                    print('lost this round')

    def whos_showing_cards(self, table, best_player, hand_check):
        """
        returns a list of players, that should show their cards,
        because they are competing for the main pot and all players
        competing for side pots, if existing

        When competing for the main pot, the last raising player has
        to show cards, and then every next player, if they have a
        better configuration than the last raising player.
        """

        showing_pls = [self.last_raising_pl if self.last_raising_pl in table.active_players else None]
        remaining_to_show = [pl for pl in table.active_players if pl.all_in is False]
        try:
            # Preparing for a very rare situation, when the first player in
            # river round folded, and all other players checked.
            ix = remaining_to_show.index(self.last_raising_pl)
            remaining_to_show = remaining_to_show[ix + 1:] + remaining_to_show[:ix]
        except ValueError:
            pass
        if remaining_to_show:
            for pl in remaining_to_show:
                winners = best_player.get_best_player(hand_check, table.common_cards, *showing_pls, pl)
                if pl in list(winners.keys()):
                    showing_pls.append(pl)
        # all players competing for side pots show cards
        if table.side_pots:
            for value in list(table.side_pots.values()):
                showing_pls.extend(value[1])
        showing_pls = list(set(showing_pls))
        return showing_pls

    def is_end_of_betting(self, table):
        """
        Checks if all active, not all inned players bet equal amounts
        over the amount of highest all in bidder.
        """

        not_all_in_bets = [player.bet_money for player in table.not_all_inned_pls]
        if not_all_in_bets:
            if len(set(not_all_in_bets)) > 1:
                return False
        try:
            highest_all_in = max([pl.bet_money for pl in table.active_players if pl.all_in is True])
            if not_all_in_bets[0] < highest_all_in:
                return False
        # for if highest all in doesnt exist or not all in bets don't exist, respectively.
        except (ValueError, IndexError):
            pass
        return True

    def next_dealer(self, table):
        current_dlrs_ix = table.initial_order.index(table.dealer)
        table.dealer = None
        while table.dealer not in table.all_players:
            current_dlrs_ix += 1
            table.dealer = table.initial_order[current_dlrs_ix % len(table.initial_order)]

    def players_in_order(self, table, new_cycle=False):
        """
        changes 3 lists:
        table_all_players, so the first player in the list is the one coming
        after the new dealer
        table.active players and table.not_all_inned_pls, so the order
        is the same as table.all_players
        """

        current_dealers_index = table.all_players.index(table.dealer)
        table.all_players = table.all_players[current_dealers_index + 1:] +\
            table.all_players[:current_dealers_index + 1]
        if new_cycle is False:
            table.active_players = [pl for pl in table.all_players if pl in table.active_players]
            table.not_all_inned_pls = [pl for pl in table.active_players if pl.all_in is False]
        else:
            table.active_players = table.all_players.copy()
            table.not_all_inned_pls = table.all_players.copy()

    def players_in_pre_flop_order(self, table):
        """
        changes the active_players (already in right order) to pre flop
        order, which is starting from the third player after the dealer.
        If there are only two players left the order in pre flop doesn't change
        """

        if len(table.active_players) > 2:
            table.active_players = table.all_players[2:] + table.all_players[:2]
            table.not_all_inned_pls = [pl for pl in table.active_players if pl.all_in is False]

    def raise_blinds(self, table):

        if table.cycle % table.how_often_b_blind_inc == 0 and table.cycle > 1:
            table.big_blind = table.big_blind * 2
        self.current_min_bet = table.big_blind

    def add_blinds(self, table):

        current_dlrs_ix = table.active_players.index(table.dealer)
        small_blind = table.active_players[(current_dlrs_ix + 1) % len(table.active_players)]
        big_blind = table.active_players[(current_dlrs_ix + 2) % len(table.active_players)]
        self.get_bet(small_blind, int(table.big_blind/2))
        self.get_bet(big_blind, table.big_blind)

    def eliminate_broke_players(self, table):
        table.all_players = [player for player in table.all_players if player.personal_money > 0]

    def proceed_with_all_ins(self, table):
        return len(table.not_all_inned_pls) <= 1

    def draw_cards(self, deck, table):
        if self.betting_round == "flop":
            table.common_cards = deck.get_flop()
        else:
            table.common_cards.append(deck.draw_card())

    def winner_display(self, table):
        os.system("clear")
        print(f"{table.all_players[0].name} won! congrats!".upper())
        self.click_to_proceed()
        exit()

    def click_to_proceed(self):
        input("Click Enter to proceed")
