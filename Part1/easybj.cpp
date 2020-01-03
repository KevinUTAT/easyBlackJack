/*
 * easybj.cpp
 *
 * Note: change this file to implement Blackjack logic
 *
 * University of Toronto
 * Fall 2019
 */

#include "easybj.h"
#include "player.h"
#include "Hand.h"
#include <sstream>
#include <iomanip>
#include <unordered_set>

Blackjack::Blackjack(Player * p, Shoe * s)
	: player(p)
	, shoe(s)
	, finished(false)
{
	/*
	 * TODO: implement this
	 */
	// shoe = s;
	// player = p;
	// num_current_hands = 0;
}

Blackjack::~Blackjack()
{
	delete dealers_hand;
	for (unsigned i = 0; i < players_hands.size(); i ++)
	{
		delete players_hands[i];
	}
}

 
Hand * Blackjack::start() 
{
	//std::cout << "Dealer Setup" << std::endl;
	dealers_hand = new Hand(this);
	dealers_hand -> draw(2);
	//std::cout << *dealers_hand << std::endl;

	//std::cout << "Player Setup" << std::endl;
	Hand * new_hand = new Hand(this);
	new_hand -> draw(2);
	players_hands.push_back(new_hand);
	//std::cout << *players_hands[0] << std::endl;

	if (players_hands[0] -> is_blackjack() or dealers_hand -> is_blackjack()){
		return nullptr;
	}

	current_hand = 0;
	return players_hands[current_hand];
}


Hand * Blackjack::next() 
{
	//return null if no more hands
	if (current_hand == int(players_hands.size() -1))
		return nullptr;

	current_hand++;
	// std::cout << *players_hands[current_hand] << std::endl;
	return players_hands[current_hand];
}


const Hand * Blackjack::dealer_hand() const
{
	if (players_hands.empty())
		return nullptr;
	return dealers_hand;
}


void Blackjack::finish() 
{
	//double profit = 0.;

	bool all_done = true;

	for (auto hand : players_hands){
		//std::cout << "hand = " << hand->get_sum() << std::endl;
		if (!hand -> is_bust() && !hand -> is_blackjack() && !hand->is_surrender())
			all_done = false;
	}

	while (!all_done && (dealers_hand->get_sum() < 17 || (dealers_hand->get_sum() == 17  && dealers_hand->is_soft()) ) )
		dealers_hand -> hit();
/*
	for (auto hand : players_hands){

		//draw sum=sum , both bj, both bust
		if ((dealers_hand -> is_blackjack() &&  hand -> is_blackjack()) ||
			(dealers_hand -> is_bust() &&  hand -> is_bust()) ||
			(!dealers_hand -> is_bust() &&  !dealers_hand -> is_blackjack() && !hand -> is_bust() && !hand -> is_blackjack()
				&& hand -> get_sum() == dealers_hand -> get_sum())
			){
			continue;
		}

		//lose cases
		else if (hand -> is_bust() || 
			(hand -> get_sum() < dealers_hand -> get_sum() && !dealers_hand -> is_bust()) || 
			hand -> is_surrender()
			){
			profit -= hand->get_bet();
		}

		//win cases
		else if (hand -> is_blackjack()){
			profit += 1.5 * hand->get_bet();
		}
		else if (dealers_hand -> is_bust() ||
			hand -> get_sum() > dealers_hand -> get_sum()			
			){
			profit += hand->get_bet();
		}
		else{
			throw std::logic_error("finish unknown case");
		}
	}
*/
	// std::cout << *this << std::endl;
	
	finished = true;
	player->update_balance(get_result());
}


void Blackjack::split_hand(){
	// creat a new hand and draw a new card
	Hand * new_hand = new Hand(this);
	new_hand -> add(players_hands[current_hand]->pop());

	// draw a new card for the original hand
	players_hands[current_hand]->draw(1);
	players_hands[current_hand]->set_from_split();

	new_hand -> draw(1);
	new_hand->set_from_split();
	//current_hand ++;
	players_hands.push_back(new_hand);
}

Shoe *& Blackjack::getShoe(){
	return shoe;
}

std::string to_currency(double v)
{
	std::ostringstream ostr;
	
	ostr << std::fixed << std::setprecision(2);
	if (v > 0) {
		ostr << "+$" << v;
	} else if (v < 0) {
		ostr << "-$" << -v;
	}
	else {
		ostr << "$" << v;
	}
	
	return ostr.str();
}


double Blackjack::get_result() const
{
	double sum = 0;
	
	for (unsigned i = 0; i < players_hands.size(); i ++)
	{
		// check for bust first
		if (dealers_hand->is_bust()) {
			if (players_hands[i]->is_bust()){
				sum -= players_hands[i]->get_bet();
			}
			else {
				sum += players_hands[i]->get_bet();
			}
			continue;
		}
		if (players_hands[i]->is_bust()) {
			sum -= players_hands[i]->get_bet();
			continue;
		}

		/* the order is: 	Tie
		*					Dealer Blackjack
		*					Player Blackjack
		*					Surrender
		*					Compare Points
		*/
		if (players_hands[i]->get_sum() == dealers_hand->get_sum()){}
		else if (dealers_hand->is_blackjack())
			sum -= players_hands[i]->get_bet();
		else if (players_hands[i]->is_blackjack()) 
			sum += 1.5 * players_hands[i]->get_bet();
		else if (players_hands[i]->is_surrender())
			sum -= 0.5 * players_hands[i]->get_bet();
		else if (players_hands[i]->get_sum() > dealers_hand->get_sum())
			sum += players_hands[i]->get_bet();
		else sum -= players_hands[i]->get_bet();
	}

	return sum;
}

void Blackjack::print_session_summery()
{
	std::cout << "Result: " << to_currency(this->get_result()) << std::endl;
	std::cout << "Current Balance: " << to_currency(this->player->get_balance()) << std::endl;
}


// << operator for Blackjack
std::ostream & operator<<(std::ostream & ostr, const Blackjack & bj)
{
	ostr << "Dealer: " << *bj.dealer_hand() << '\n';
	for (unsigned i = 0; i < bj.players_hands.size(); i++)
	{
		ostr << "Hand " << i+1 << ": " << *bj.players_hands[i] << '\n';
	} 

	if (bj.finished) {
		ostr << "Result: " << to_currency(bj.get_result()) << '\n';
		ostr << "Current Balance: " << to_currency(bj.player->get_balance())
			<< '\n';
	}

	return ostr;
}