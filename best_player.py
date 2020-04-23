from hand_check import Hand_Check
from copy import copy

class Best_Player:

    hand_ranking = {
    "high card":1,
    "one pair": 2,
    "two pairs":3,
    "three of a kind":4,
    "straight":5,
    "flush":6,
    "full house":7,
    "four of a kind":8,
    "straight flush":9,
    "royal flush":10
    }

    rank_equivalents = {
    2:2,
    3:3,
    4:4,
    5:5,
    6:6,
    7:7,
    8:8,
    9:9,
    10:10,
    "J":11,
    "Q":12,
    "K":13,
    "A":14
    }

    def _init__(self):
        pass

    def get_best_player(self, hand_check, common_cards, *players ):
        """gets best player or players if split,
         configuration of five cards (of random player if split)(?)
         and name of configuration as a dictionary, where player is the key
         and configuration and name of it in tuple as value
          As input it takes five common cards
          (not table instance) and a number of players. (not their hands)"""

        best_conf_and_ranking_for_each = self.get_conf_from_table_and_players(hand_check, common_cards, players)
        # print(best_conf_and_ranking_for_each)
        all_configurations = [best_conf_and_ranking_for_each[player][1] for player in best_conf_and_ranking_for_each]
        # print(all_configurations)
        best_conf = max(all_configurations, key= lambda conf: self.hand_ranking[conf])
        # print(best_conf)
        players_with_best_conf = {key:value for (key, value) in best_conf_and_ranking_for_each.items() if value[1] == best_conf}
        if len(players_with_best_conf) == 1:
            return players_with_best_conf
        i = 0
        while i < 5 and len(players_with_best_conf) > 1:
            list_of_ranks = []
            for player in players_with_best_conf:
                list_of_ranks.append(players_with_best_conf[player][0][i].rank)
            # print("start while loop")
            # print(f"number of card: {i+ 1} ")
            # print(f"dict: {players_with_best_conf}")
            # print(f"length of dict: {len(players_with_best_conf)}")
            # print(f"list of ranks:{list_of_ranks}")
            highest_rank = max(list_of_ranks, key= lambda p: self.rank_equivalents[p])
            # print(highest_rank)
            players_with_best_conf = {key:value for (key,value) in players_with_best_conf.items() if value[0][i].rank == highest_rank}
            i += 1
        return players_with_best_conf



    def get_conf_from_table_and_players(self, hand_check, common_cards, players):
        output_dict = {}
        for player in players:
            all_cards = common_cards + player.hand
            value = hand_check.get_configuration_and_ranking(all_cards)
            output_dict.update({player: value})
        return output_dict

