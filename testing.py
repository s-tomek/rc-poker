from local_repo.card import Card
from local_repo.deck import Deck
from local_repo.hand_check import Hand_Check
from local_repo.player import Player
from local_repo.best_player import Best_Player
from local_repo.roundmanager import RoundManager
from local_repo.table import Table

d = Deck()
hand_check = Hand_Check()
best_player = Best_Player()


p1 = Player("Auguste")
p2 = Player('Domante')
p3 = Player('Tomekas')
p4 = Player('Danielus')

list_of_p = [p1,p2,p3,p4]

count = 1
for player in list_of_p:
    player.draw_hand(d)
    player.personal_money = 5000
    # if count == 1:
    #     player.personal_money += 1000
    # count += 1


table = Table(list_of_p)

table.big_blind = 100

r_man = RoundManager()
for i in range(10):
    r_man.new_cycle(d, table)
    r_man.pre_flop(table)
    r_man.flop(d, table)
    r_man.turn(d, table)
    r_man.river(d, table, best_player, hand_check)


# for player in list_of_p:
    # print(f"{player.name} has cards : ['{player.hand[0].suits}',{player.hand[0].rank}], ['{player.hand[0].suits}',{player.hand[1].rank}]")
#
# table = Table()
# table.add_flop(d)
# table.add_card(d)
# table.add_card(d)
# c1 = Card('D',3)
# c2 = Card('D',3)
# c3 = Card('S',5)
# c4 = Card('H',9)
# c5 = Card('H',5)
# table.common_cards.extend([c1,c2,c3,c4,c5])
# list1 = []
# for card in table.common_cards:
#     list1.append([card.suits, card.rank])
# print(list1)
#
# a = best_player.get_best_player(hand_check, table.common_cards, p1, p2, p3)
# player = list(a.keys())
# print(f"{player[0].name} won!")




#to check get_configuration_and_ranking func. cards have to be initialized first

# c1 = Card('D',3)
# c2 = Card('D',3)
# c3 = Card('S',5)
# c4 = Card('H',9)
# c5 = Card('H',5)
# c6 = Card('H',10)
# c7 = Card('C','J')
#
# c1.rank = 2
# c2.rank = 10
# c3.rank = "J"
# c4.rank = "Q"
# c5.rank = 2
# c6.rank = "A"
# c7.rank = 6
#
# c1.suits = "D"
# c2.suits = "C"
# c3.suits = "C"
# c4.suits = "C"
# c5.suits = "D"
# c6.suits = "D"
# c7.suits = "D"
#
# checking = hand_check.get_configuration_and_ranking([c1,c2,c3,c4,c5,c6,c7])
# print([c1.rank,c2.rank,c3.rank,c4.rank,c5.rank,c6.rank, c7.rank])
# print(checking)
# try:
#     print(checking[1])
# except:
#     pass
# try:
#     card_conf = checking[0]
#     card_ranks = []
#     for card in card_conf:
#         card_ranks.append(card.rank)
#     print(card_ranks)
#     card_suits = []
#     for card in card_conf:
#         card_suits.append(card.suits)
#     print(card_suits)
# except:
#     print("not tested configuration")

#[9, 'A', 10, 6, 'Q', 3, 2] problemmm
# print(hand_check.is_sublist([6,5,4,3,2], hand_check.ranks_from_highest))
#
# a = [1,2,3] == [3,2,1]
# print(a)

#
# a = Hand_Check()
# b = Hand_Check.sort_ranks_from_highest(a,["A","A",3,3,10,10,"Q"])
# print(b)

# a = 10 not in [3, 4, 5, 8, 7, 2,'A']
# print(a)

# a = {2,3,4} - set([2,3,4,5])
# if a == set():
#     print(a)