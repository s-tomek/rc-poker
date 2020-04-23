import copy

class Hand_Check:


    ranks_from_highest = ["A","K","Q","J",10,9,8,7,6,5,4,3,2]
    ranks_from_highest_ace_as_one = ["K","Q","J",10,9,8,7,6,5,4,3,2,"A"]



    def __init__(self):
        pass



    def get_configuration_and_ranking(self, all_cards):
        """ return configuration of 5 best cards from given 7 and
        the name of ranking of those cards. The configuration is sorted,
        meaning it begins with the important cards, from highest, then kickers, also
        sorted from the highest """

        if self.is_one_pair(all_cards):
            return self.is_one_pair(all_cards)
        elif self.is_two_pairs(all_cards):
            return self.is_two_pairs(all_cards)
        elif self.is_three_of_a_kind(all_cards):
            return self.is_three_of_a_kind(all_cards)
        elif self.is_straight(all_cards):
            return self.is_straight(all_cards)
        elif self.is_flush(all_cards):
            return self.is_flush(all_cards)   # TODO flush not working!!!!
        elif self.is_full_house(all_cards):
            return self.is_full_house(all_cards)
        elif self.is_four_of_a_kind(all_cards):
            return self.is_four_of_a_kind(all_cards)
        elif self.is_straight_flush(all_cards):
            return self.is_straight_flush(all_cards)
            # TODO  at some point include royal flush, doesnt change anything in comparing hands
        else:
            list_of_ranks = self.get_list_from_cards(all_cards, "ranks") #  TODO refactor this, put in another func
            configuration_of_ranks = self.sort_ranks_from_highest(list_of_ranks)[:5]
            configuration_of_cards = self.get_cards_from_list(all_cards, configuration_of_ranks, "ranks")
            return configuration_of_cards, "high card"
        return output


    def is_one_pair(self, cards):
        '''
        if the given 7 cards (possible to input more) not create
        one pair configuration it returns none, if they create one pair configuration
        it returns  a list of 5 card instances creating the configuration and a string: "one pair"
        '''

        if self.is_straight_or_straight_flush(cards) != None:
            return None
        if self.is_flush(cards) != None:
            return None
        list_of_ranks = self.get_list_from_cards(cards, "ranks")
        repeated_cards = self.return_repeated_ranks(list_of_ranks)
        if len(repeated_cards) == 1 and list_of_ranks.count(repeated_cards[0]) == 2:
            configuration_of_ranks = [] #   TODO should i put all local variables at the beginning of function? or in the place of use?
            configuration_of_ranks.extend([repeated_cards[0],repeated_cards[0]])
            list_of_ranks.remove(repeated_cards[0])
            list_of_ranks.remove(repeated_cards[0])
            configuration_of_ranks.extend(self.sort_ranks_from_highest(list_of_ranks)[:3])
        else:
            return None
        configuration_of_cards = self.get_cards_from_list(cards, configuration_of_ranks, "ranks")
        return configuration_of_cards, "one pair"


    def is_two_pairs(self, cards):  #   TODO doesnt catch full houses, rewrite!

        if self.is_straight_or_straight_flush(cards) != None:
            return None
        if self.is_flush(cards) != None:
            return None
        list_of_ranks = self.get_list_from_cards(cards, "ranks")
        rank_dictionary = self.repeated_rank_dict(list_of_ranks)
        configuration_of_ranks = []
        if 3 in rank_dictionary.keys():
            return None
        elif 2 in rank_dictionary.keys() and len(rank_dictionary[2]) == 2:
                rank_dictionary[2] = self.sort_ranks_from_highest(rank_dictionary[2])
                configuration_of_ranks.extend([rank_dictionary[2][0]] * 2)
                configuration_of_ranks.extend([rank_dictionary[2][1]] * 2)
        else:
            return None
        remaining_ranks = list(set(list_of_ranks) - set(configuration_of_ranks))
        remaining_ranks_sorted = self.sort_ranks_from_highest(remaining_ranks)
        configuration_of_ranks.append(remaining_ranks_sorted[0])
        configuration_of_cards = self.get_cards_from_list(cards, configuration_of_ranks, "ranks")
        return configuration_of_cards, "two pairs"

    def is_three_of_a_kind(self, cards):

        if self.is_straight_or_straight_flush(cards) != None:
            return None
        if self.is_flush(cards) != None: #  TODO does it really filter flushes? [3,3,3,K,10]
            return None
        list_of_ranks = self.get_list_from_cards(cards, "ranks")
        repeated_cards = self.return_repeated_ranks(list_of_ranks)
        configuration_of_ranks = []
        if len(repeated_cards) == 1 and list_of_ranks.count(repeated_cards[0]) == 3:
            configuration_of_ranks.extend([repeated_cards[0]] * 3)
            for rank in configuration_of_ranks:
                list_of_ranks.remove(rank)
            configuration_of_ranks.extend(self.sort_ranks_from_highest(list_of_ranks)[:2])
        else:
            return None
        configuration_of_cards = self.get_cards_from_list(cards, configuration_of_ranks, "ranks")
        return configuration_of_cards, "three of a kind"



    def is_straight(self, cards):

        if self.is_five_in_same_suits(cards):
            return None
        configuration_of_cards = self.is_straight_or_straight_flush(cards)
        if configuration_of_cards != None:
            return configuration_of_cards, "straight"
        else:
            return None


    def is_straight_or_straight_flush(self, cards): #   TODO wrong name, it checks for conf of straight no matter the colour

        list_of_ranks = self.get_list_from_cards(cards, "ranks")
        set_of_ranks = set(list_of_ranks)
        list_of_ranks_sorted_wo_rep = self.sort_ranks_from_highest(list(set_of_ranks))
        if len(list_of_ranks_sorted_wo_rep) < 5:
            return None
        bool = False
        if {'A',2,3,4,5} - set(list_of_ranks_sorted_wo_rep) == set() and (6 not in list_of_ranks_sorted_wo_rep): #    TODO refactor this?
            configuration_of_ranks = ["A",2,3,4,5]
            bool = True
        else:
            for i in range(len(list_of_ranks_sorted_wo_rep) - 4):
                bool = self.is_sublist(list_of_ranks_sorted_wo_rep[i:i+5], self.ranks_from_highest)
                if bool == True:
                    configuration_of_ranks = list_of_ranks_sorted_wo_rep[i:i+5]
                    break
        if bool == False:
            return None
        configuration_of_cards = self.get_cards_from_list(cards, configuration_of_ranks, "ranks")
        return configuration_of_cards

    def is_flush(self, cards):  #   TODO doesnt return none when full house sometimes

        if not self.is_five_in_same_suits(cards):
            return None
        if self.is_straight_flush(cards): # TODO refactor? it repeats code 2 or 3 times
            return None
        if self.is_full_house(cards):
            return None
#         if self.is_straight_or_straight_flush(cards) == None:
#             return None
        configuration_of_cards = self.get_highest_cards_in_same_suits(cards) #    TODO maybe refactor that func? its similair to is_five_in_same_suits
        return configuration_of_cards, "flush"


    def is_full_house(self, cards): #   TODO

        list_of_ranks = self.get_list_from_cards(cards, "ranks")
        rank_dictionary = self.repeated_rank_dict(list_of_ranks)
        configuration_of_ranks = []
        if 3 in rank_dictionary.keys() and 2 in rank_dictionary.keys():
                rank_dictionary[3] = self.sort_ranks_from_highest(rank_dictionary[3])
                rank_dictionary[2] = self.sort_ranks_from_highest(rank_dictionary[2])
                configuration_of_ranks.extend([rank_dictionary[3][0]] * 3)
                configuration_of_ranks.extend([rank_dictionary[2][0]] * 2)
        elif 3 in rank_dictionary.keys() and len(rank_dictionary[3]) == 2:
                rank_dictionary[3] = self.sort_ranks_from_highest(rank_dictionary[3])
                configuration_of_ranks.extend([rank_dictionary[3][0]] * 3)
                configuration_of_ranks.extend([rank_dictionary[3][1]] * 2)
        else:
            return None
        configuration_of_cards = self.get_cards_from_list(cards, configuration_of_ranks, "ranks")
        return configuration_of_cards, "full house"


    def is_four_of_a_kind(self, cards):
        list_of_ranks = self.get_list_from_cards(cards, "ranks")
        rank_dictionary = self.repeated_rank_dict(list_of_ranks)
        configuration_of_ranks = []
        if 4 in rank_dictionary.keys():
            configuration_of_ranks.extend([rank_dictionary[4][0]] * 4)
            list_of_ranks = [elem for elem in list_of_ranks if elem != rank_dictionary[4][0]]
            list_of_ranks = self.sort_ranks_from_highest(list_of_ranks)
            configuration_of_ranks.append(list_of_ranks[0])
        else:
            return None
        configuration_of_cards = self.get_cards_from_list(cards, configuration_of_ranks,"ranks")
        return configuration_of_cards, "four of a kind"


    def is_straight_flush(self, cards):
        configuration_of_cards = self.is_straight_or_straight_flush(cards) # TODO refactor this func
        if configuration_of_cards == None:
            return None
        if self.is_five_in_same_suits(configuration_of_cards) == False:
            return None
        return configuration_of_cards, "straight flush"


    def get_list_from_cards(self, cards, property):
        output_list = []
        if property == "suits":
            for card in cards:
                output_list.append(card.suits)
        elif property == "ranks":
            for card in cards:
                output_list.append(card.rank)
        else:
            raise ValueError("second argument has to be suits or ranks")
        return output_list


    def get_cards_from_list(self, cards, input_list, property): # TODO refactor so no property input is needed
        working_list = copy.copy(input_list)
        cards_list = copy.copy(cards)
        output_list = []
        if property == "ranks":
            for rank in working_list:
                for card in cards_list:
                    if card.rank == rank:
                        output_list.append(card)
                        cards_list.remove(card)
                        break
        else:
            raise ValueError("second argument has to be suits or ranks")
        return output_list

    def return_repeated_ranks(self, list_of_ranks):

        output_list = []
        for rank in list_of_ranks:
            if list_of_ranks.count(rank) > 1:
                output_list.append(rank)
        output_list = list(set(output_list))
        return output_list

    def sort_ranks_from_highest(self, ranks):
        output = []
        working_ranks = copy.copy(ranks)
        while "A" in working_ranks:
            output.append("A")
            working_ranks.remove("A")
        while "K" in working_ranks:
            output.append("K")
            working_ranks.remove("K")
        while "Q" in working_ranks:
            output.append("Q")
            working_ranks.remove("Q")
        while "J" in working_ranks:
            output.append("J")
            working_ranks.remove("J")
        if len(ranks) > 0:
            working_ranks.sort(reverse=True)
            for rank in working_ranks:
                output.append(rank)
        return output


    def is_sublist(self, sublist, list):
        list1 = []
        length = len(sublist)
        try:
            starting_index = list.index(sublist[0])
            list1 = list[starting_index:starting_index + length]
            if list1 == sublist:
                return True
            else:
                return False
        except IndexError:
            return False


    def is_five_in_same_suits(self, cards):
        suit_list = [card.suits for card in cards]
        most_frequent_suit = max(set(suit_list), key = suit_list.count)
        if suit_list.count(most_frequent_suit) >= 5:
            return True
        else:
            return False

    def get_highest_cards_in_same_suits(self, cards):
        suit_list = [card.suits for card in cards]
        most_frequent_suit = max(set(suit_list), key = suit_list.count)
        output_cards = []
        list_of_ranks = self.get_list_from_cards(cards, "ranks")
        list_of_ranks_sorted = self.sort_ranks_from_highest(list_of_ranks)
        cards_sorted = self.get_cards_from_list(cards, list_of_ranks_sorted, "ranks")
        for card in cards_sorted:
            if card.suits != most_frequent_suit:
                cards_sorted.remove(card)
        return cards_sorted

    def repeated_rank_dict(self, list_of_ranks):
        '''
        return a dictionary where times of occurence is key and
        the rank or list of ranks is value '''

        repeated_ranks = self.return_repeated_ranks(list_of_ranks)
        output_dict = {}
        for i in range(2,5):
            list1 = []
            for rank in set(list_of_ranks):
                if list_of_ranks.count(rank) == i:
                    list1.append(rank)
                    if list != []:
                        output_dict.update({i : list1} )
            list1 = []
        return output_dict



