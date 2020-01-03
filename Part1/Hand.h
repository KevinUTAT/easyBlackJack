#ifndef HAND_H
#define HAND_H

#include <string>
#include <iostream>
#include <vector>
#include "shoe.h"
#include "easybj.h"
#include "config.h"

class Hand {
	std::vector <char> cards;
	int sum;	// Point sum of the cards in this hand
	int softAces;	// Number of soft aces remaining in this hand
	Blackjack* bjInstance = nullptr;	
	double bet;	// Bet total on this hand
	bool surrendered; 	// Player has surrendered the hand
	bool done;	// Hand has no further action (last action was stand)
	bool dirty; // An action was already performed on this hand
	bool from_split; // this hand is a result of a split

public:
	Hand(Blackjack* bjInstance);
	Hand(Blackjack* bjInstance, bool dirty);

	/*
	 * adds a card to the hand
	 */
	void add (char card); 

	/*
	 * draw n cards from shoe and add to hand
	 */
	void draw (int n);

	/*
	 * Remove the last card in the hand and return it
	 */
	char pop();


	//==== Actions (all below functions set state to dirty) ====//

	/*
	 * draw 1 card from shoe and add to hand
	 */
	void hit();

	/*
	 * split hand into, other hand is saved in the bjInstance
	 */
	void split();

	/*
	 * surrender current hand, halves the bet ammount and forfeits
	 */
	void surrender();


	/*
	 * doubles the bet ammount if this is a starting hand.
	 * Performs a hit and no further actions allowed.
	 */
	void double_bet();
	
	/*
	 * end all actions on this hand.
	 */
	void stand();

	void set_from_split();

	//==== Accessors ====//

	int get_sum() const;

	bool is_blackjack() const;

	bool is_bust() const;

	bool is_soft() const;

	bool is_surrender() const;

	bool is_from_split() const;

	bool is_done() const;	

	double get_bet() const;

	bool can_split() const; // this check can the current hand be split?

	bool is_dirty() const;

	bool is_from_A_split() const;

	Blackjack* get_bjInstance();


	friend std::ostream & operator<<(std::ostream &, const Hand &);

};

#endif