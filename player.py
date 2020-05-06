

class Player:

    def __init__(self, name, personal_money):
        self.name = name
        self.hand = []
        self.personal_money = personal_money
        self.bet_money = 0
        self.all_in = False

    def draw_hand(self, current_deck):
        self.clear_hand()
        self.hand = [current_deck.draw_card() for i in range(2)]

    def clear_hand(self):
        self.hand = []


