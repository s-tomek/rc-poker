
from local_repo.hand_check import Hand_Check

h_c = Hand_Check()
a = h_c.is_sublist([6, 5, 4, 3, 2], h_c.ranks_from_highest)
print(a)