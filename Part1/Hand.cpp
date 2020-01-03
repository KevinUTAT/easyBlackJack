#include "Hand.h"
#include <sstream>
#include <iomanip>
#include <unordered_set>

Hand::Hand(Blackjack* bjInstance){
	sum = 0;
	softAces = 0;
	this -> bjInstance = bjInstance;
	bet = 1.00;
	surrendered = 0;
	done = 0;
	dirty = 0;
	from_split = false;
}

Hand::Hand(Blackjack* bjInstance, bool dirty){
	sum = 0;
	softAces = 0;
	this -> bjInstance = bjInstance;
	bet = 1.00;
	surrendered = 0;
	done = 0;
	this -> dirty = dirty;
	from_split = false;
}

void Hand::add(char card){

	cards.push_back(card);

	//std::unordered_set<char> tens = {'T', 'J', 'Q', 'K'};
	std::string tens = "TJQK";
	
	if (card == 'A'){
		if (sum + 11 > 21){
			sum += 1;
		}
		else{
			sum += 11;
			softAces += 1;
		}
	}
	//else if (tens.find(card) != tens.end()){
	else if (tens.find(card) != std::string::npos) {
		sum += 10;
	}
	else{
		sum += card-'0';
	}

	if (sum > 21 && softAces > 0){
		softAces--;
		sum -= 10;
	}
}


void Hand::draw(int n){

	while (/*!bjInstance->getShoe()->over() && */n > 0){	
		this -> add(bjInstance->getShoe()->pop());
		n--;
	} 
}


char Hand::pop(){
	char end = cards.back();
	cards.pop_back();
	return end;
}



void Hand::hit(){
	this -> draw(1);
	dirty = true;
}


void Hand::split(){
	if (can_split())
	{
		if (cards[0] == 'A') sum = 11;
		else sum /= 2; // when split, the current sum halfs
		bjInstance -> split_hand();
		// when split, hand can have forther action
	}
	else throw std::logic_error("Can't split");
}


void Hand::surrender(){
	// Can't surrender after any action.
	if (dirty){
		throw std::logic_error("Action already taken");
	}
	surrendered = true;
	this -> stand();
	dirty = true;
}


void Hand::double_bet(){
	// Can't double if already have more than 2 cards.
	if (cards.size() > 2){
		throw std::logic_error("Not starting hand (more than 2 cards in play)");
	}

	bet *= 2;
	this -> hit();
	this -> stand();
}


void Hand::stand(){
	dirty = true;
	done = true;
}


void Hand::set_from_split()
{
	from_split = true;
}


int Hand::get_sum() const{
	return sum;
}


bool Hand::is_blackjack() const{
	if (!from_split && cards.size() == 2) return sum == 21;
	else return false;
}


bool Hand::is_bust() const{
	return sum > 21;
}

bool Hand::is_soft() const{
	return softAces > 0 && !is_blackjack() && !is_bust();
}


bool Hand::is_surrender() const
{
	return surrendered;
}


bool Hand::is_from_split() const
{
	return from_split;
}

bool Hand::is_done() const
{
	return done;
}


double Hand::get_bet() const
{
	return bet;
}


bool Hand::can_split() const
{
	//std::unordered_set<char> tens = {'T', 'J', 'Q', 'K'};
	std::string tens = "TJQK";
	if (cards.size() == 2 && bjInstance->players_hands.size() < 4) {
		if (cards[0] == cards[1]) {
			return true;
		}
		else if (tens.find(cards[0]) != std::string::npos 
		&& tens.find(cards[1])!= std::string::npos) return true;
	}
	return false;
}


bool Hand::is_dirty() const
{
	return dirty;
}


bool Hand::is_from_A_split() const
{
	return (from_split && cards[0] == 'A');
}


Blackjack* Hand::get_bjInstance()
{
	return bjInstance;
}


// << operator for Hand
std::ostream & operator<<(std::ostream & ostr, const Hand & hand)
{
	for (unsigned i = 0; i < hand.cards.size(); i++)
	{
		ostr << hand.cards[i] << ' ';
	}
	if (hand.is_blackjack()) ostr << "(blackjack) ";
	else if (hand.is_bust()) ostr << "(bust) ";
	else
	{
		ostr << '(';
		if ( hand.is_soft()) ostr << "soft ";
		ostr << hand.get_sum() << ") ";
	}

	if (hand.bet > 1) ostr << "DOUBLE";
	if (hand.surrendered) ostr << "SURRENDER";
	

	return ostr;
}