 /*
 * easybj.h
 *
 * Header files for Easy Blackjack.
 *
 * Note: change this file to implement Blackjack
 *
 * University of Toronto
 * Fall 2019
 */
 
#ifndef EASYBJ_H
#define EASYBJ_H

#include <string>
#include <iostream>
#include <vector>
#include "shoe.h"

class Player;
// class Shoe;
class Config;
class Hand;

class Blackjack {
	Player * player;
	Shoe * shoe;
	Hand * dealers_hand;
	bool finished;
	
	
public:
	std::vector<Hand*> players_hands;
	int current_hand;

	Blackjack(Player * p, Shoe * s);
	~Blackjack();
	
	/*
	 * Start a game of Blackjack
	 *
	 * Returns first hand to be played, nullptr if either dealer or player's
	 * initial hand is blackjack (or both)
	 */
	Hand * start();
	
	/*
	 * Returns dealer's hand
	 */
	const Hand * dealer_hand() const;
	
	/*
	 * Returns next hand to be played (may be the same hand)
	 */
	Hand * next();
	
	/*
	 * Call once next() returns nullptr
	 */
	void finish();

	/*
	 * Split the current player hand
	 */
	void split_hand();

	// Accessors
	Shoe *& getShoe();

	// get the resulting $$$
	double get_result() const;

	void print_session_summery();


	friend std::ostream & operator<<(std::ostream &, const Blackjack &);

	// TODO: you may add more functions as appropriate
};

/*
 * Returns string representation of currency for v
 */
std::string to_currency(double v);

#endif
