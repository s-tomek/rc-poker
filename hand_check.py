import copy

class Hand_Check:
    """
    Hand_Check is a class, that includes the function
    get_configuration_and_ranking and functions needed
    for it.
    """

    ranks_from_highest = ["A", "K", "Q", "J", 10, 9, 8, 7, 6, 5, 4, 3, 2]

    def __init__(self):  # TODO should i leave this? can i access the function without init?
        pass

    def get_configuration_and_ranking(self, all_cards):
        """
        return configuration of 5 best cards from given 7 and
        the name of ranking of those cards. The configuration is sorted,
        meaning it begins with the important cards, from highest, then kickers, also
        sorted starting from highest.
         """

        #  order of functions is unchangeable, they only work in that order.
        #  It's kept to not repeat checks
        functions_in_order = [
            self.is_full_house,
            self.is_four_of_a_kind,
            self.is_straight_flush,
            self.is_flush,
            self.is_straight,
            self.is_one_pair,
            self.is_two_pairs,
            self.is_three_of_a_kind
        ]

        # TODO include royal flush, doesnt change anything in comparing hands
        for func in functions_in_order:
            output = func(all_cards)
            #  checking cards functions return None if they don't recognize the configuration
            if output:
                break
        if output is None:
            return self.get_high_card(all_cards)
        return output

    def is_one_pair(self, cards):
        """
        if the given 7 cards don't create one pair configuration it
        returns None, if they create one pair configuration it returns
        a list of 5 card instances creating the configuration and a string: "one pair"
        in a tuple.
        """

        list_of_ranks = self.get_ranks_from_cards(cards)
        rank_dict = self.repeated_rank_dict(list_of_ranks)
        if rank_dict.keys() == {2} and len(rank_dict[2]) == 1:
            remaining_ranks = list(filter(lambda x: x not in rank_dict[2], list_of_ranks))
            remaining_ranks_sorted = self.sort_ranks_from_highest(remaining_ranks)
            conf_of_ranks = rank_dict[2] * 2 + remaining_ranks_sorted[:3]
        else:
            return None
        conf_of_cards = self.get_cards_from_ranks(cards, conf_of_ranks)
        return conf_of_cards, "one pair"

    def is_two_pairs(self, cards):
        """
        if the given 7 cards don't create two pairs configuration it
        returns None, if they create two pairs configuration it returns
        a list of 5 card instances creating the configuration and a string: "two pairs"
        in a tuple.
        """

        # if self.get_five_consecutive_ranks(cards) != None:
        #     return None
        # if self.is_flush(cards) != None:
        #     return None

        list_of_ranks = self.get_ranks_from_cards(cards)
        rank_dict = self.repeated_rank_dict(list_of_ranks)
        if rank_dict.keys() == {2} and len(rank_dict[2]) >= 2:
                rank_dict[2] = self.sort_ranks_from_highest(rank_dict[2])
                conf_of_ranks = [rank_dict[2][0]] * 2 + [rank_dict[2][1]] * 2
        else:
            return None
        remaining_ranks = list(filter(lambda x: x not in rank_dict[2][:2], list_of_ranks))
        remaining_ranks_sorted = self.sort_ranks_from_highest(remaining_ranks)
        conf_of_ranks.append(remaining_ranks_sorted[0])
        conf_of_cards = self.get_cards_from_ranks(cards, conf_of_ranks)
        return conf_of_cards, "two pairs"

    def is_three_of_a_kind(self, cards):
        """
        if the given 7 cards don't create three of a kind configuration it
        returns None, if they create three of a kind configuration it returns
        a list of 5 card instances creating the configuration and a string: "three of a kind"
        in a tuple.
        """

        list_of_ranks = self.get_ranks_from_cards(cards)
        rank_dict = self.repeated_rank_dict(list_of_ranks)
        if rank_dict.keys() == {3}:  # works only after excluding full house
            conf_of_ranks = [rank_dict[3][0]] * 3
        else:
            return None
        remaining_ranks = list(filter(lambda x: x not in rank_dict[3], list_of_ranks))
        remaining_ranks_sorted = self.sort_ranks_from_highest(remaining_ranks)
        conf_of_ranks.extend(remaining_ranks_sorted[:2])
        configuration_of_cards = self.get_cards_from_ranks(cards, conf_of_ranks)
        return configuration_of_cards, "three of a kind"

    def is_straight(self, cards):
        """
        if the given 7 cards don't create the straight configuration it
        returns None, if they create the straight configuration it returns
        a list of 5 card instances creating the configuration and a string: "straight"
        in a tuple.
        """

        configuration_of_cards = self.get_five_consecutive_ranks(cards)
        if configuration_of_cards:
            return configuration_of_cards, "straight"
        else:
            return None

    def get_five_consecutive_ranks(self, cards):
        """
        If five from seven given cards are in consecutive order,
        it returns those five cards. Otherwise, it returns None.
        """

        list_of_ranks = self.get_ranks_from_cards(cards)
        list_of_ranks_wo_rep = list(set(list_of_ranks))
        list_of_ranks_wo_rep_sorted = self.sort_ranks_from_highest(list_of_ranks_wo_rep)
        conf_of_ranks = []
        if len(list_of_ranks_wo_rep_sorted) < 5:
            return None
        #  iterates over the list of ranks without repetition, checks all consecutive
        #  five cards it they're a sublist of all ranks in order.
        for i in range(len(list_of_ranks_wo_rep_sorted) - 4):  # to get number of consecutive fives in a list
            if self.is_sublist(list_of_ranks_wo_rep_sorted[i:i + 5], self.ranks_from_highest):
                conf_of_ranks = list_of_ranks_wo_rep_sorted[i:i + 5]
                break
        if {5, 4, 3, 2, 'A'} - set(list_of_ranks_wo_rep_sorted) == set() and conf_of_ranks == []:
            conf_of_ranks = ["A", 2, 3, 4, 5]
        if not conf_of_ranks:
            return None
        configuration_of_cards = self.get_cards_from_ranks(cards, conf_of_ranks)
        return configuration_of_cards

    def is_flush(self, cards):
        """
        if the given 7 cards don't create the flush configuration it
        returns None, if they create the flush configuration it returns
        a list of 5 card instances creating the configuration and a string: "flush"
        in a tuple.
        """

        configuration_of_cards = self.get_highest_five_cards_in_same_suits(cards)
        if not configuration_of_cards:
            return None
        return configuration_of_cards, "flush"


    def is_full_house(self, cards):
        """
        if the given 7 cards don't create the full house configuration it
        returns None, if they create the full house configuration it returns
        a list of 5 card instances creating the configuration and a string: "full house"
        in a tuple.
        """

        list_of_ranks = self.get_ranks_from_cards(cards)
        rank_dict = self.repeated_rank_dict(list_of_ranks)
        if 3 in rank_dict.keys():
            rank_dict[3] = self.sort_ranks_from_highest(rank_dict[3])
            temp_conf_of_ranks = [rank_dict[3][0]] * 3
        else:
            return None
        #  the pair in configuration can be either a part of a second three of a kind, with
        #  lower rank or a pair, then it's from a higher ranked pair.
        temp_rank_for_pair = []
        try:
            temp_rank_for_pair.append(rank_dict[3][1])
        except:
            pass
        try:
            rank_dict[2] = self.sort_ranks_from_highest(rank_dict[2])
            temp_rank_for_pair.append(rank_dict[2][0])
        except:
            pass
        if not temp_rank_for_pair:
            return None
        rank_for_pair = self.sort_ranks_from_highest(temp_rank_for_pair)[0]
        temp_conf_of_ranks.extend([rank_for_pair] * 2)
        conf_of_cards = self.get_cards_from_ranks(cards, temp_conf_of_ranks)
        return conf_of_cards, "full house"

    def is_four_of_a_kind(self, cards):
        """
        if the given 7 cards don't create the four of a kind configuration it
        returns None, if they create the four of a kind configuration it returns
        a list of 5 card instances creating the configuration and a string: "four of a kind"
        in a tuple.
        """

        list_of_ranks = self.get_ranks_from_cards(cards)
        rank_dict = self.repeated_rank_dict(list_of_ranks)
        if 4 in rank_dict.keys():
            conf_of_ranks = [rank_dict[4][0]] * 4
            list_of_ranks = [r for r in list_of_ranks if r != rank_dict[4][0]]
            list_of_ranks = self.sort_ranks_from_highest(list_of_ranks)
            conf_of_ranks.append(list_of_ranks[0])
        else:
            return None
        conf_of_cards = self.get_cards_from_ranks(cards, conf_of_ranks)
        return conf_of_cards, "four of a kind"

    def is_straight_flush(self, cards):
        """
        if the given 7 cards don't create straight flush configuration it
        returns None, if they create the straight flush configuration it returns
        a list of 5 card instances creating the configuration and a string: "straight flush"
        in a tuple. Note: there's no royal flush specified, but that doesn't change the game play.
        """

        temp_conf_of_cards = self.get_five_consecutive_ranks(cards)
        if not temp_conf_of_cards:
            return None
        conf_of_cards = self.get_highest_five_cards_in_same_suits(temp_conf_of_cards)
        if not conf_of_cards:
            return None
        return conf_of_cards, "straight flush"

    def get_high_card(self, cards):
        """
        Returns sorted top five from given cards. Note: works only after checking for all configurations.
        Unlike other configuration checking functions it doesn't return None under any circumstances.
        """

        list_of_ranks = self.get_ranks_from_cards(cards)
        conf_of_ranks = self.sort_ranks_from_highest(list_of_ranks)[:5]
        conf_of_cards = self.get_cards_from_ranks(cards, conf_of_ranks)
        return conf_of_cards, "high card"

    def get_ranks_from_cards(self, cards):
        return [c.rank for c in cards]

    def get_cards_from_ranks(self, cards, rank_list):
        """
        Returns cards corresponding to given ranks, doesn't work when
        ranks don't suit cards
        """

        temp_rank_list = copy.copy(rank_list)
        temp_cards_list = copy.copy(cards)
        cards_by_rank = []
        for rank in temp_rank_list:
            for card in temp_cards_list:
                if card.rank == rank:
                    cards_by_rank.append(card)
                    temp_cards_list.remove(card)
                    break
        return cards_by_rank

    def sort_ranks_from_highest(self, ranks):

        ranks_sorted = []
        temp_ranks = copy.copy(ranks)
        for rank in self.ranks_from_highest:
            while rank in temp_ranks:
                ranks_sorted.append(rank)
                temp_ranks.remove(rank)
        return ranks_sorted

    def is_sublist(self, sublist, org_list):

        try:
            starting_ix = org_list.index(sublist[0])
            list1 = org_list[starting_ix:starting_ix + len(sublist)]
            if list1 == sublist:
                return True
            else:
                return False
        except IndexError:
            return False

    def get_highest_five_cards_in_same_suits(self, cards):
        """
        Returns highest five cards in same suits if there are
        five or more such cards, otherwise returns None
        """

        suit_list = [card.suits for card in cards]
        most_frequent_suits = max(set(suit_list), key = suit_list.count)
        if suit_list.count(most_frequent_suits) < 5:
            return None
        list_of_ranks = self.get_ranks_from_cards(cards)
        list_of_ranks_sorted = self.sort_ranks_from_highest(list_of_ranks)
        temp_cards_sorted = self.get_cards_from_ranks(cards, list_of_ranks_sorted)
        cards_sorted = [c for c in temp_cards_sorted if c.suits == most_frequent_suits]
        return cards_sorted

    def repeated_rank_dict(self, list_of_ranks):
        """return a dictionary where times of occurence is key and
        list of ranks is value.
        """

        output_dict = {}
        for i in range(2,5):
            rep_list = [r for r in set(list_of_ranks) if list_of_ranks.count(r) == i]
            if rep_list:
                output_dict.update({i: rep_list})
        return output_dict



