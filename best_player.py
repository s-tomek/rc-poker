

class Best_Player:

    hand_ranking = {
        "high card": 1,
        "one pair": 2,
        "two pairs": 3,
        "three of a kind": 4,
        "straight": 5,
        "flush": 6,
        "full house": 7,
        "four of a kind": 8,
        "straight flush": 9,
        "royal flush": 10
    }

    rank_equivalents = {
        2: 2,
        3: 3,
        4: 4,
        5: 5,
        6: 6,
        7: 7,
        8: 8,
        9: 9,
        10: 10,
        "J": 11,
        "Q": 12,
        "K": 13,
        "A": 14
    }

    def _init__(self):
        pass

    def get_best_player(self, hand_check, common_cards, *players):
        """
        gets best player or players if split,
        configuration of five cards
        and name of configuration as a dictionary, where players are keys
        and configuration and name of it in a tuple as value
        As input it takes five common cards
        (not table instance) and a number of player instances (not their hands).
          """

        best_conf_and_ranking_for_each = self.get_conf_from_table_and_players(hand_check, common_cards, players)
        all_configurations = [best_conf_and_ranking_for_each[player][1] for player in best_conf_and_ranking_for_each]
        best_conf = max(all_configurations, key=lambda conf: self.hand_ranking[conf])

        #  filters dictionary of all players to just those with best configuration
        players_with_best_conf = {key: value for (key, value) in best_conf_and_ranking_for_each.items()
                                  if value[1] == best_conf}

        #  if multiple players have the same configuration, compares highest card of each player, then
        #  filters to those with same, highest cards, and repeats the process with all five cards if needed.
        #  if c_num = 5, it means there are still multiple players in the players with best conf dict,
        #  so a split is needed.
        c_num = 0
        while c_num < 5 and len(players_with_best_conf) > 1:
            list_of_ranks = []
            for player in players_with_best_conf:
                list_of_ranks.append(players_with_best_conf[player][0][c_num].rank)
            highest_rank = max(list_of_ranks, key=lambda p: self.rank_equivalents[p])
            players_with_best_conf = {key: value for (key, value) in players_with_best_conf.items()
                                      if value[0][c_num].rank == highest_rank}
            c_num += 1
        return players_with_best_conf



    def get_conf_from_table_and_players(self, hand_check, common_cards, players):
        """
        returns a dictionary of all players as keys and corresponding configurations and
        configuration names in tuples as values. Note that to access the configuration name
        one has to use players index and [0] for configuration of cards
        or [1] for configuration name, for example "one pair"
        """

        output_dict = {}
        for player in players:
            all_cards = common_cards + player.hand
            value = hand_check.get_configuration_and_ranking(all_cards)
            output_dict.update({player: value})
        return output_dict

