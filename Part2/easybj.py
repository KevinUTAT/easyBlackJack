#!/usr/bin/python3
#
# easybj.py
#
# Calculate optimal strategy for the game of Easy Blackjack
#

from table import Table
from collections import defaultdict
import copy

# code names for all the hard hands
HARD_CODE = [ '4', '5', '6', '7', '8', '9', '10', '11', '12', '13', '14', 
    '15', '16', '17', '18', '19', '20']

# code names for all the soft hands
SOFT_CODE = [ 'AA', 'A2', 'A3', 'A4', 'A5', 'A6', 'A7', 'A8', 'A9' ]

# code names for all the hands that can be split
SPLIT_CODE = [ '22', '33', '44', '55', '66', '77', '88', '99', 'TT', 'AA' ]

# code names for all the hands that cannot be split
NON_SPLIT_CODE = HARD_CODE + SOFT_CODE

# code names for standing
STAND_CODE = HARD_CODE + ['21'] + SOFT_CODE
   
# code names for all the y-labels in the strategy table
PLAYER_CODE = HARD_CODE + SPLIT_CODE + SOFT_CODE[1:]

# code names for all the x-labels in all the tables
DEALER_CODE = HARD_CODE + SOFT_CODE[:6]

# code names for all the initial player starting hands
# (hard 4 is always 22, and hard 20 is always TT)
INITIAL_CODE = HARD_CODE[1:-1] + SPLIT_CODE + SOFT_CODE[1:] + ['BJ']

# 
# Returns whether a and b are close enough in floating point value
# Note: use this to debug your code
#
def isclose(a, b=1., rel_tol=1e-09, abs_tol=0.0):
    return abs(a-b) <= max(rel_tol * max(abs(a), abs(b)), abs_tol)  

# use the numeral value 0 to represent a busted hand (makes it easier to
# compare using integer comparison)
BUST = 0

# list of distinct card values
DISTINCT = [ 'A', '2', '3', '4', '5', '6', '7', '8', '9', 'T' ]

# number of cards with 10 points
NUM_FACES = 4

# number of ranks in a French deck
NUM_RANKS = 13

# return the probability of receiving this card
def probability(card):
    return (1 if card != 'T' else NUM_FACES) / NUM_RANKS

#
# Represents a Blackjack hand (owned by either player or dealer)
#
# Note: you should make BIG changes to this class
#
class Hand:
    def __init__(self, x, y, dealer=False):
        self.cards = [x, y]
        self.is_dealer = dealer

        self.soft_aces = 0        
        self.sum = 0
        self.code_str = ""

        self._calculate_sum()
        self._calculate_code()

    
    # Return whether hand is eligable to split
    def can_split(self):
        tens = "TJQK"

        if (len(self.cards) == 2):
            if (self.cards[0] == self.cards[1] or (self.cards[0] in tens and self.cards[1] in tens)):
                return True
        return False

    # Return whether hand is BJ
    def _is_blackjack(self):
        return (len(self.cards) == 2 and self.sum == 21)

    # Return whether hand is busted
    def _is_bust(self):
        return self.sum > 21

    # calculates and saves value of hand, softaces as attributes
    def _calculate_sum(self):
        tens = "TJQK"

        for card in self.cards:

            if (card == 'A'):
                if (self.sum + 11 > 21):
                    self.sum += 1
                else:
                    self.sum += 11
                    self.soft_aces += 1

            elif (card in tens):
                self.sum += 10

            else:
                self.sum += int(card)


            if (self.sum > 21 and self.soft_aces > 0):
                self.soft_aces -= 1
                self.sum -= 10
            # print (card, self.sum, self.soft_aces)


    # calculates and saves the hand code as an attribute
    def _calculate_code(self):
        # Hierarchy: BlackJack/Bust > Split > Soft > Hard

        if (self._is_blackjack()):
            self.code_str = "BJ"

        elif (self._is_bust()): 
            self.code_str = "0"

        elif (self.can_split() and not self.is_dealer):
            tens = "TJQK"
            if (self.cards[0] in tens):
                self.code_str = "TT"
            elif (self.soft_aces > 0):
                self.code_str = "AA"
            else:
                self.code_str = str(self.cards[0]) + str(self.cards[1])

        elif (self.soft_aces > 0 and self.sum < 21):            
            self.code_str = "A" + str(self.sum - 11)

            if (self.is_dealer and self.sum >= 18):     # Dealer treats all soft >= 18 as hard
                self.code_str = str(self.sum)
            elif(self.is_dealer and self.can_split()):
                self.code_str = "AA"


        elif (self.sum <= 21):
            self.code_str = str(self.sum)

        else:
            # print (self.cards, self.sum, self.soft_aces, self.code_str, self.is_dealer)
            raise ValueError("unknown card combination code")

    def add_card(self,card):
        assert(type(card) is str)
        self.cards.append(card)
        tens = "TJQK"
        if (card == 'A'):
            if (self.sum + 11 > 21):
                self.sum += 1
            else:
                self.sum += 11
                self.soft_aces += 1

        elif (card in tens):
            self.sum += 10

        else:
            self.sum += int(card)


        if (self.sum > 21 and self.soft_aces > 0):
            self.soft_aces -= 1
            self.sum -= 10
        # print (card, self.sum, self.soft_aces)

        self._calculate_code()        


    # probability of receiving this hand
    def probability(self):
        p = 1.
        for c in self.cards:
            p *= probability(c)
        return p
  
    # the code which represents this hand
    def code(self, nosplit=False):
        # print (self.cards, self.sum, self.soft_aces, self.code_str, self.is_dealer)
        return self.code_str
                
#
# Singleton class to store all the results. 
#
# Note: you should make HUGE changes to this class
#
class Calculator:
    def __init__(self): 
        self.initprob = Table(float, DEALER_CODE + ['BJ'], INITIAL_CODE, unit='%')
        self.dealprob = defaultdict(dict)
        self.stand_ev = Table(float, DEALER_CODE, STAND_CODE)
        self.hit_ev = Table(float, DEALER_CODE, NON_SPLIT_CODE)
        self.double_ev = Table(float, DEALER_CODE, NON_SPLIT_CODE)
        self.split_ev3 = Table(float, DEALER_CODE, SPLIT_CODE)
        self.split_ev2 = Table(float, DEALER_CODE, SPLIT_CODE[:-1])
        self.split_ev1 = Table(float, DEALER_CODE, SPLIT_CODE[:-1])
        self.split_ev0 = Table(float, DEALER_CODE, STAND_CODE)
        self.optimal_ev = Table(float, DEALER_CODE, PLAYER_CODE)
        self.strategy = Table(str, DEALER_CODE, PLAYER_CODE)
        self.advantage = 0.
    
    # make each cell of the initial probability table      
    def make_initial_cell(self, player, dealer):
        table = self.initprob
        dc = dealer.code()  
        pc = player.code()
        prob = dealer.probability() * player.probability()
        if table[pc,dc] is None:
            table[pc,dc] = prob
        else:
            table[pc,dc] += prob
    
    # make the initial probability table            
    def make_initial_table(self, fill_func):
        #
        # TODO: refactor so that other table building functions can use it
        #
        for i in DISTINCT:
            for j in DISTINCT:
                for x in DISTINCT:
                    for y in DISTINCT:
                        dealer = Hand(i, j, dealer=True)
                        player = Hand(x, y)
                        fill_func(player, dealer)
    
    # verify sum of initial table is close to 1    
    def verify_initial_table(self):
        total = 0.
        for x in self.initprob.xlabels:
            for y in self.initprob.ylabels:
                total += self.initprob[y,x]
        assert(isclose(total))


    # make each cell of stand EV table
    def make_stand_cell(self, player, dealer):
        table = self.stand_ev
        dealprob = self.dealprob
        dc = dealer.code()  
        pc = player.code()

        if pc == "BJ":
            pc = "21"

        if player.can_split() and pc != "AA":
            pc = str(player.sum)

        if dc == "BJ":
            return

        EV = 0.0

        for outcome in dealprob[dc]:
            # Dealer wins case
            if int(outcome) > player.sum:
                EV -= dealprob[dc][outcome] * 1

            # Player wins case
            elif int(outcome) < player.sum:
                EV += dealprob[dc][outcome] * 1

        if table[pc,dc] is None:
            table[pc,dc] = EV


    # make double EV table
    def make_double_table(self):
        table = self.double_ev

         # Traverse hands in bottom up order
        traverse_order_p = HARD_CODE[:5:-1] + SOFT_CODE[::-1] + HARD_CODE[5::-1]
        traverse_order_d = HARD_CODE[:2:-1] + SOFT_CODE[5::-1] + HARD_CODE[2::-1]

        for p in traverse_order_p:
            
            p_hand = None

            # Initialize hand to the given cards (eg A6) or arbitrary cards that sum up to given sum (eg 20)

            if p[0] == "A":
                p_hand = Hand(p[0], p[1])
            elif p == "20":
                p_hand = Hand("T","T")
            else:
                p_hand = Hand(str(int((int(p)/2))),str(int(int(p)/2) + (int(p) %2 != 0)))

            for d in traverse_order_d:

                if table[p,d] is None:
                    table[p,d] = 0.0

                for k in range(1,14,1):
                    
                    d_hand = None

                    if d[0] == "A":
                        d_hand = Hand(d[0], d[1], dealer=True)
                    elif d == "20":
                        d_hand = Hand("T","T", dealer=True)
                    else:
                        d_hand = Hand(str(int((int(d)/2))),str(int(int(d)/2) + (int(d) %2 != 0)), dealer=True)

                    lookup = copy.deepcopy(p_hand)

                    # Initialize lookup hand based on possible cards drawn
                    if k == 1:
                        lookup.add_card("A")
                    elif k < 10:
                        lookup.add_card(str(k))
                    else:
                        lookup.add_card("T")

                    l_c = lookup.code()

                    # Add probabilities to probability table
                    if lookup.sum > 21: # Double into bust
                        table[p,d] -= 2 * 1/13.0
                    else:
                        table[p,d] += self.stand_ev[l_c,d]*2 * 1/13.0


    # Calculate the dealer table probabilities
    def make_dealer_table(self):

        def get_row_sum(row):
            sum = 0
            for key in row:
                sum += row[key]
            return sum

        def add_row_probabilities(row1, row2, factor):
            for key in row2:
                row1[key] += row2[key]*factor


        table = self.dealprob

        for i in DEALER_CODE:
            table[i] = defaultdict(float)


        # First calculate probabilities for when dealer stands
        for i in range(21,16,-1):
            table[str(i)] = {str(i): 1}

        # Traverse hands in bottom up order
        traverse_order = HARD_CODE[-5:2:-1] + SOFT_CODE[5::-1] + HARD_CODE[2::-1]

        for i in traverse_order:
            for k in range(1,14,1):
                hand = None

                # Initialize hand to the given cards (eg A6) or arbitrary cards that sum up to given sum (eg 20)
                if i[0] == "A":
                    hand = Hand(i[0], i[1], dealer=True)
                elif i == "20":
                    hand = Hand("T","T",dealer=True)
                else:
                    hand = Hand(str(int((int(i)/2))),str(int(int(i)/2) + (int(i) %2 != 0)), dealer=True) 
                lookup = copy.deepcopy(hand)

                # Initialize lookup hand based on possible cards drawn
                if k == 1:
                    lookup.add_card("A")
                elif k < 10:
                    lookup.add_card(str(k))
                else:
                    lookup.add_card("T")

                h_c, l_c = (hand.code(), lookup.code())

                # Add probabilities to probability table
                if l_c == "BJ":
                    table[h_c]["21"] += 1/13.0
                if l_c == "0":
                    table[h_c]["0"] += 1/13.0
                else:
                    add_row_probabilities(table[h_c], table[l_c], 1/13.0)


        for i in table:
            assert isclose(get_row_sum(table[i]))


    # Make Hit EV table
    def make_hit_table(self):
        table = self.hit_ev

        # Traverse hands in bottom up order
        traverse_order_p = HARD_CODE[:5:-1] + SOFT_CODE[::-1] + HARD_CODE[5::-1]
        traverse_order_d = HARD_CODE[:2:-1] + SOFT_CODE[5::-1] + HARD_CODE[2::-1]

        for p in traverse_order_p:
            
            p_hand = None

            # Initialize hand to the given cards (eg A6) or arbitrary cards that sum up to given sum (eg 20)
            if p[0] == "A":
                p_hand = Hand(p[0], p[1])
            elif p == "20":
                p_hand = Hand("T","T")
            else:
                p_hand = Hand(str(int((int(p)/2))),str(int(int(p)/2) + (int(p) %2 != 0))) 

            for d in traverse_order_d:

                if table[p,d] is None:
                    table[p,d] = 0.0

                # iterate through possible draws
                for k in range(1,14,1):
                    
                    d_hand = None

                    if d[0] == "A":
                        d_hand = Hand(d[0], d[1], dealer=True)
                    elif d == "20":
                        d_hand = Hand("T","T", dealer=True)
                    else:
                        d_hand = Hand(str(int((int(d)/2))),str(int(int(d)/2) + (int(d) %2 != 0)), dealer=True)

                    lookup = copy.deepcopy(p_hand)

                    # Initialize lookup hand based on possible cards drawn
                    if k == 1:
                        lookup.add_card("A")
                    elif k < 10:
                        lookup.add_card(str(k))
                    else:
                        lookup.add_card("T")

                    l_c = lookup.code()


                    # Add probabilities to probability table
                    if lookup.sum > 21: # bust
                        table[p,d] -= 1/13.0
                    elif lookup.sum == 21:
                        table[p,d] += self.stand_ev[l_c,d] * 1/13.0
                    else:
                        table[p,d] += max(self.stand_ev[l_c,d], table[l_c,d])* 1/13.0
                  

    def make_split_table(self):
        table0 = self.split_ev0
        table1 = self.split_ev1
        table2 = self.split_ev2
        table3 = self.split_ev3

        traverse_order_p = SPLIT_CODE[::-1]
        traverse_order_d = HARD_CODE[:2:-1] + SOFT_CODE[5::-1] + HARD_CODE[2::-1]

        # make split_ev0 (base case)
        for p in STAND_CODE:
            for d in traverse_order_d:
                if p == '21':
                    table0[p, d] = self.stand_ev[p, d]
                else:
                    table0[p, d] = max(self.stand_ev[p, d], self.hit_ev[p, d], \
                             self.double_ev[p, d])

        # make split_ev1 where can split one more time
        for p in traverse_order_p:
            if p == 'AA':
                continue
            p_hand = Hand(p[0], p[1])
            for d in traverse_order_d:
                EV_split0 = 0.0
                if p_hand.can_split():
                    for k in range(1,14,1):
                        if k == 1:
                            new_hand0 = Hand(p[0], "A")
                        elif k < 10:
                            new_hand0 = Hand(p[0], str(k))
                        else:
                            new_hand0 = Hand(p[0], "T")

                        nh0_c = new_hand0.code()
                        # At the 3rd split, cannot split into over 20
                        if new_hand0.can_split():
                            nh0_c = split2hard(nh0_c)
                        if nh0_c is 'BJ':
                            nh0_c = '21'
                        #EV_split0 += max(self.stand_ev[nh0_c, d], self.hit_ev[nh0_c, d], \
                                        #self.double_ev[nh0_c, d]) * 1/13.0
                        EV_split0 += table0[nh0_c, d] * 1/13.0
                    '''
                    table1[p, d] = max(self.stand_ev[split2hard(p), d], self.hit_ev[split2hard(p), d], \
                                    self.double_ev[split2hard(p), d], 2 * EV_split0)
                    '''
                    table1[p, d] = 2 * EV_split0
                '''
                else:
                    table1[p, d] = max(self.stand_ev[p, d], self.hit_ev[p, d], \
                                    self.double_ev[p, d])
                '''

        # make split_ev2
        for p in traverse_order_p:
            if p == 'AA':
                continue
            p_hand = Hand(p[0], p[1])
            for d in traverse_order_d:
                EV_split0 = 0.0 #new hand that re split
                EV_split1 = 0.0 #new hand dose not resplit
                if p_hand.can_split():
                    for k in range(1, 14, 1):
                        if k == 1:
                            new_hand0 = Hand(p[0], "A")
                        elif k < 10:
                            new_hand0 = Hand(p[0], str(k))
                        else:
                            new_hand0 = Hand(p[0], "T")

                        nh0_c = new_hand0.code()

                        for l in range(1, 14, 1):
                            if l == 1:
                                new_hand1 = Hand(p[1], "A")
                            elif l < 10:
                                new_hand1 = Hand(p[1], str(l))
                            else:
                                new_hand1 = Hand(p[1], "T")

                            nh1_c = new_hand1.code()

                            if new_hand0.can_split() and new_hand1.can_split():
                                EV_split0 += table1[nh0_c, d] * 1/13.0**2
                                EV_split1 += table0[split2hard(nh1_c), d] * 1/13.0**2
                                continue

                            if nh0_c is 'BJ':
                                EV_split0 += self.stand_ev['21', d] * 1/13.0**2
                            # EV_split0 += self.stand_ev['21', d]
                            elif new_hand0.can_split():
                                #EV_split0 +=  max(table0[split2hard(nh0_c), d], table1[nh0_c, d]) * 1/13.0
                                EV_split0 +=  table1[nh0_c, d] * 1/13.0**2
                            # EV_split0 += max(self.stand_ev[split2hard(nh0_c), d], self.hit_ev[split2hard(nh0_c), d], \
                            #             self.double_ev[split2hard(nh0_c), d], table1[nh0_c, d]) * 1/13.0
                            else:
                                EV_split0 += table0[split2hard(nh0_c), d] * 1/13.0**2

                            if nh1_c is 'BJ':
                                EV_split1 += self.stand_ev['21', d] * 1/13.0**2
                            # EV_split0 += self.stand_ev['21', d]
                            elif new_hand1.can_split():
                                #EV_split1 +=  max(table0[split2hard(nh1_c), d], table1[nh1_c, d]) * 1/13.0
                                EV_split1 +=  table1[nh1_c, d] * 1/13.0**2
                            # EV_split0 += max(self.stand_ev[split2hard(nh0_c), d], self.hit_ev[split2hard(nh0_c), d], \
                            #             self.double_ev[split2hard(nh0_c), d], table1[nh0_c, d]) * 1/13.0
                            else:
                                EV_split1 += table0[split2hard(nh1_c), d] * 1/13.0**2
                            



                    """ for k in range(1,14,1):
                        if k == 1:
                            new_hand0 = Hand(p[0], "A")
                        elif k < 10:
                            new_hand0 = Hand(p[0], str(k))
                        else:
                            new_hand0 = Hand(p[0], "T")

                        nh0_c = new_hand0.code()
                        #print(nh0_c)
                        if nh0_c is 'BJ':
                            EV_split0 += self.stand_ev['21', d] * 1/13.0
                            # EV_split0 += self.stand_ev['21', d]
                        elif new_hand0.can_split():
                            EV_split0 +=  max(table0[split2hard(nh0_c), d], table1[nh0_c, d]) * 1/13.0
                            #EV_split0 +=  table1[nh0_c, d] * 1/13.0
                            # EV_split0 += max(self.stand_ev[split2hard(nh0_c), d], self.hit_ev[split2hard(nh0_c), d], \
                            #             self.double_ev[split2hard(nh0_c), d], table1[nh0_c, d]) * 1/13.0
                        else:
                            EV_split0 += table0[split2hard(nh0_c), d] * 1/13.0
                            # EV_split0 += max(self.stand_ev[nh0_c, d], self.hit_ev[nh0_c, d], \
                            #             self.double_ev[nh0_c, d]) * 1/13.0

                    
                    for l in range(1,14,1):
                        if l == 1:
                            new_hand1 = Hand(p[1], "A")
                        elif l < 10:
                            new_hand1 = Hand(p[1], str(l))
                        else:
                            new_hand1 = Hand(p[1], "T")

                        nh1_c = new_hand1.code()
                        #print(nh0_c)
                        # At the 3rd split, cannot split into over 21
                        if nh1_c is 'BJ':
                            EV_split1 += table0['21', d] * 1/13.0
                        else:
                            EV_split1 += table0[split2hard(nh1_c), d] * 1/13.0
                            # EV_split1 += max(self.stand_ev[nh1_c, d], self.hit_ev[nh1_c, d], \
                            #             self.double_ev[nh1_c, d]) * 1/13.0
                    # table2[p, d] = max(self.stand_ev[split2hard(p), d], self.hit_ev[split2hard(p), d], \
                    #                 self.double_ev[split2hard(p), d], EV_split0 + EV_split1) """
                    
                table2[p, d] = EV_split0 + EV_split1
                '''
                else:
                    table2[p, d] = max(self.stand_ev[split2hard(p), d], self.hit_ev[split2hard(p), d], \
                                    self.double_ev[split2hard(p), d])
                '''


        # make split_ev3
        for p in traverse_order_p:
            p_hand = Hand(p[0], p[1])
            for d in traverse_order_d:
                EV_split0 = 0.0 #new hand that re split
                EV_split1 = 0.0 #new hand dose not resplit
                if p_hand.can_split():
                    for k in range(1, 14, 1):
                        if k == 1:
                            new_hand0 = Hand(p[0], "A")
                        elif k < 10:
                            new_hand0 = Hand(p[0], str(k))
                        else:
                            new_hand0 = Hand(p[0], "T")

                        nh0_c = new_hand0.code()

                        for l in range(1, 14, 1):
                            if l == 1:
                                new_hand1 = Hand(p[1], "A")
                            elif l < 10:
                                new_hand1 = Hand(p[1], str(l))
                            else:
                                new_hand1 = Hand(p[1], "T")

                            nh1_c = new_hand1.code() 

                            if p == 'AA':
                                if nh0_c == 'BJ':
                                    EV_split0 += self.stand_ev['21', d] * 1/13.0**2
                                else:
                                    EV_split0 += self.stand_ev[split2hard(nh0_c), d] * 1/13.0**2
                                if nh1_c == 'BJ':
                                    EV_split1 += self.stand_ev['21', d] * 1/13.0**2
                                else:
                                    EV_split1 += self.stand_ev[split2hard(nh1_c), d] * 1/13.0**2
                                continue

                            # the case that both hand can split
                            if new_hand0.can_split() and new_hand1.can_split():
                                EV_split0 += table1[nh0_c, d] * 1/13.0**2
                                EV_split1 += table1[nh1_c, d] * 1/13.0**2
                                continue
                            
                            if nh0_c is 'BJ':
                                EV_split0 += self.stand_ev['21', d] * 1/13.0**2
                            # EV_split0 += self.stand_ev['21', d]
                            elif new_hand0.can_split():
                                #EV_split0 +=  max(table0[split2hard(nh0_c), d], table1[nh0_c, d]) * 1/13.0
                                EV_split0 +=  table2[nh0_c, d] * 1/13.0**2
                            # EV_split0 += max(self.stand_ev[split2hard(nh0_c), d], self.hit_ev[split2hard(nh0_c), d], \
                            #             self.double_ev[split2hard(nh0_c), d], table1[nh0_c, d]) * 1/13.0
                            else:
                                EV_split0 += table0[split2hard(nh0_c), d] * 1/13.0**2

                            if nh1_c is 'BJ':
                                EV_split1 += self.stand_ev['21', d] * 1/13.0**2
                            # EV_split0 += self.stand_ev['21', d]
                            elif new_hand1.can_split():
                                #EV_split1 +=  max(table0[split2hard(nh1_c), d], table1[nh1_c, d]) * 1/13.0
                                EV_split1 +=  table2[nh1_c, d] * 1/13.0**2
                            # EV_split0 += max(self.stand_ev[split2hard(nh0_c), d], self.hit_ev[split2hard(nh0_c), d], \
                            #             self.double_ev[split2hard(nh0_c), d], table1[nh0_c, d]) * 1/13.0
                            else:
                                EV_split1 += table0[split2hard(nh1_c), d] * 1/13.0**2

                table3[p, d] = EV_split0 + EV_split1
            """ for d in traverse_order_d:
                EV_split0 = 0.0
                if p_hand.can_split():
                    for k in range(1,14,1):
                        if k == 1:
                            new_hand0 = Hand(p[0], "A")
                        elif k < 10:
                            new_hand0 = Hand(p[0], str(k))
                        else:
                            new_hand0 = Hand(p[0], "T")

                        nh0_c = new_hand0.code()
                        # At the 3rd split, cannot split into over 20
                        if nh0_c is 'BJ':
                            EV_split0 += self.stand_ev['21', d]
                        elif new_hand0.can_split():
                            if nh0_c is 'AA':
                                EV_split0 += table0[nh0_c, d] * 1/13.0
                            else:
                                EV_split0 += table2[nh0_c, d] * 1/13.0
                        else:
                            nh0_c = split2hard(nh0_c)
                            EV_split0 += max(self.stand_ev[nh0_c, d], self.hit_ev[nh0_c, d], \
                                        self.double_ev[nh0_c, d]) * 1/13.0

                    table3[p, d] = max(self.stand_ev[split2hard(p), d], self.hit_ev[split2hard(p), d], \
                                    self.double_ev[split2hard(p), d], 2 * EV_split0)
                else:
                    table3[p, d] = max(self.stand_ev[split2hard(p), d], self.hit_ev[split2hard(p), d], \
                                    self.double_ev[split2hard(p), d]) """
        #print(table0)
        #print(table1)
        #print(table2)

    # Make Hit EV table
    def make_optimal_table(self):
        table = self.optimal_ev

        # Traverse hands in bottom up order
        traverse_order_p = PLAYER_CODE
        traverse_order_d = DEALER_CODE

        for p in traverse_order_p:
            
            p_hand = None

            # Initialize hand to the given cards (eg A6) or arbitrary cards that sum up to given sum (eg 20)
            if p[0] == "A":
                p_hand = Hand(p[0], p[1], dealer=True)
            elif p == "20":
                p_hand = Hand("T","T", dealer=True)
            elif len(p) == 2 and p[0] == p[1]:
                p_hand = Hand(p[0], p[1], dealer=True)
            else:
                p_hand = Hand(str(int((int(p)/2))),str(int(int(p)/2) + (int(p) %2 != 0)), dealer=True) 

            for d in traverse_order_d:

                # print (p,d)
                if p not in SPLIT_CODE:
                    table[p,d] = max(self.stand_ev[p,d], self.hit_ev[p,d], self.double_ev[p,d], -0.5)
                else:
                    pc = p_hand.code()
                    table[p,d] = max(self.stand_ev[pc,d], self.hit_ev[pc,d], self.double_ev[pc,d], self.split_ev3[p,d], -0.5)

            # Make Hit EV table
    def make_strategy_table(self):

        def add_alt_action (table,p,d,p_t = None):
            if not p_t:
                p_t = p

            if self.stand_ev[p,d] < self.hit_ev[p,d]:
                table[p_t,d] += 'h'
            else:
                table[p_t,d] += 's'

        table = self.strategy

        # Traverse hands in bottom up order
        traverse_order_p = PLAYER_CODE
        traverse_order_d = DEALER_CODE

        for p in traverse_order_p:
            
            p_hand = None

            # Initialize hand to the given cards (eg A6) or arbitrary cards that sum up to given sum (eg 20)
            if p[0] == "A":
                p_hand = Hand(p[0], p[1], dealer=True)
            elif p == "20":
                p_hand = Hand("T","T", dealer=True)
            elif len(p) == 2 and p[0] == p[1]:
                p_hand = Hand(p[0], p[1], dealer=True)
            else:
                p_hand = Hand(str(int((int(p)/2))),str(int(int(p)/2) + (int(p) %2 != 0)), dealer=True) 

            for d in traverse_order_d:

                if p not in SPLIT_CODE:
                    
                    # Stand
                    if max(self.hit_ev[p,d], self.double_ev[p,d], -0.5) < self.stand_ev[p,d]:
                        table[p,d] = 'S'
                    
                    # Hit
                    elif max(self.stand_ev[p,d], self.double_ev[p,d], -0.5) < self.hit_ev[p,d]:
                        table[p,d] = 'H'
                    
                    # Double
                    elif max(self.stand_ev[p,d], self.hit_ev[p,d], -0.5) < self.double_ev[p,d]:
                        table[p,d] = 'D'
                        add_alt_action(table,p,d)
                    
                    # Surrender
                    else:
                        table[p,d] = 'R'
                        add_alt_action(table,p,d)

                else:
                    pc = p_hand.code()                    
                    
                    # Split
                    if max(self.hit_ev[pc,d], self.double_ev[pc,d], self.stand_ev[pc,d], -0.5) < self.split_ev3[p,d]:
                        table[p,d] = 'P'

                    # Stand
                    elif max(self.hit_ev[pc,d], self.double_ev[pc,d], self.split_ev3[p,d], -0.5) < self.stand_ev[pc,d]:
                        table[p,d] = 'S'
                    
                    # Hit
                    elif max(self.stand_ev[pc,d], self.double_ev[pc,d], self.split_ev3[p,d], -0.5) < self.hit_ev[pc,d]:
                        table[p,d] = 'H'
                    
                    # Double
                    elif max(self.stand_ev[pc,d], self.hit_ev[pc,d], self.split_ev3[p,d], -0.5) < self.double_ev[pc,d]:
                        table[p,d] = 'D'
                        add_alt_action(table,pc,d,p)
                    
                    # Surrender
                    else:
                        table[p,d] = 'R'
                        add_alt_action(table,pc,d,p)


                

    
    def calc_advantage(self):
        player_adventage = 0.0

        dealer_hands = DEALER_CODE + ['BJ']

        for d in dealer_hands:
            for p in INITIAL_CODE:
                if p == 'BJ':
                    if d == 'BJ':
                        player_adventage += self.initprob[p, d] * 0
                    else:
                        player_adventage += self.initprob[p, d] * 1.5
                elif d == 'BJ':
                    player_adventage += self.initprob[p, d] * -1
                else:
                    player_adventage += self.initprob[p, d] * self.optimal_ev[p, d]

        self.advantage = player_adventage
#
# Calculate all the ev tables and the final strategy table and return them
# all in a dictionary
#      
def calculate():
    calc = Calculator()   
    
    calc.make_initial_table(calc.make_initial_cell)
    
    # TODO: uncomment once you finished your table implementation
    #       and Hand.code implementation
    calc.verify_initial_table()

    # TODO: calculate all other tables and numbers

    # Dealer Table
    calc.make_dealer_table()

    # Stand EV table
    calc.make_initial_table(calc.make_stand_cell)

    # Double EV table
    calc.make_double_table()

    # Hit EV table
    calc.make_hit_table()

    calc.make_split_table()

    calc.make_optimal_table()

    calc.calc_advantage()

    calc.make_strategy_table()

    return {
        'initial' : calc.initprob,
        'dealer' : calc.dealprob,
        'stand' : calc.stand_ev,
        'hit' : calc.hit_ev,
        'double' : calc.double_ev,
        'split' : calc.split_ev3,
        "resplit" : [ 
            calc.split_ev0,
            calc.split_ev1,
            calc.split_ev2,
        ],
        'optimal' : calc.optimal_ev,
        'strategy' : calc.strategy,
        'advantage' : calc.advantage,
    }


def split2hard(split_str):
    if split_str is 'AA':
        return '12'
    elif split_str is 'TT':
        return str(20)
    elif len(split_str) == 2:
        if split_str[0] == split_str[1]:
            if split_str[0] == '1':
                return str(11)
            else:
                return str(int(split_str[0]) + int(split_str[1]))
        else:
            return split_str
    else:
        return split_str

