/*
 * player.cpp
 *
 * Note: change this file to implement Player subclass
 *
 * University of Toronto
 * Fall 2019
 */

#include "player.h"
#include "Hand.h"
#include <unordered_set>
#include <fstream>
#include <iostream>
#include <vector>
#include <string>
#include <sstream>
#include <cstring>

void player_actions(Hand * hand, std::string player_action);


class ManualPlayer : public Player {
	public:
	virtual void play(Hand* hand, const Hand* dealer) override;
	virtual bool again() const;
};


void ManualPlayer::play(Hand* hand, const Hand* dealer)
{
	while (!hand -> is_bust() && hand->get_sum() != 21 && !hand -> is_done()
		&& !hand->is_from_A_split()){
		// Print blackjack status 
		std::cout << *hand->get_bjInstance() << std::endl;

		std::string player_action;
		if (hand->can_split() && hand->get_bjInstance()->players_hands.size() < 4){
			if (hand->is_from_split()){
				std::cout << "Stand (S) Hit (H) Double (D) Split (P): ";
			}
			else {
				std::cout << "Stand (S) Hit (H) Double (D) Split (P) Surrender (R): ";
			}
		}
		else if (hand -> is_dirty()){
			std::cout << "Stand (S) Hit (H): ";
		}
		else{
			if (hand->is_from_split()) {
				std::cout << "Stand (S) Hit (H) Double (D): ";	
			}
			else {
				std::cout << "Stand (S) Hit (H) Double (D) Surrender (R): ";		
			}
		}
		// std::cin >> player_action;
		std::getline(std::cin, player_action);

		player_actions(hand, player_action);

		player_action = std::tolower(player_action[0]);



		// std::unordered_set<std::string> stand = {"s", "S", "Stand", "stand"};
		// std::unordered_set<std::string> hit = {"h", "H", "hit", "Hit"};
		// std::unordered_set<std::string> double_bet = {"d", "D", "double", "Double"};
		// std::unordered_set<std::string> split = {"p", "P"};
		// std::unordered_set<std::string> surrender = {"r", "R"};
		
		// if (stand.count(player_action)) 
		// 	hand->stand();
		// else if (hit.count(player_action)) 
		// 	hand->hit();
		// else if (double_bet.count(player_action) && !hand->is_dirty()) 
		// 	hand->double_bet();
		// else if (split.count(player_action) && hand->can_split()
		// 	&& hand->get_bjInstance()->players_hands.size() < 4) {
		// 	hand->split();
		// }
		// else if (surrender.count(player_action) && !hand->is_dirty()
		// 	&& !hand->is_from_split()) 
		// 	hand->surrender();
		// else std::cout << ("Unrecognized action")  << std::endl;

	}
	(void) dealer;
}

bool ManualPlayer::again() const{
	std::string player_action;
	std::cout << "Press Any Key to Continue, (Q to Quit): ";	
	std::getline(std::cin, player_action); // "std::cin >>" can't handle empty input
	//std::cin >> player_action;
	//if (player_action.empty()) return false;
	player_action = std::tolower(player_action[0]);
	if (player_action.compare("q"))
		return true;
	return false;

}


class AutoPlayer : public Player {
	
	public:
	int nr_hands_to_play;
	bool silent = false;		
	std::vector<std::vector<char*>> strategy_table;
	virtual void play(Hand* hand, const Hand* dealer) override;
	virtual bool again() const;
	virtual ~AutoPlayer();
};


void AutoPlayer::play(Hand* hand, const Hand* dealer)
{
	// std::cout << "AutoPlayer plays\n";

	//Look up correct action from strat table
	while (!hand -> is_bust() && hand->get_sum() != 21 && !hand -> is_done()
		&& !hand->is_from_A_split()){
		int row = -1;
		int col = -1;
		bool hand_can_split = hand->can_split();

		Get_Strategy_From_Table:
		int dealer_sum = dealer -> get_sum();
		if (dealer -> is_soft() && (dealer_sum >= 12 && dealer_sum <= 17)){
			// col 18 to 23
			col = dealer_sum - 11 + 17;
		}else{
			// first 17 cols
			col = dealer_sum - 3;
		}

		int player_sum = hand -> get_sum();
		if (hand -> is_soft() && (player_sum >= 13 && player_sum <= 20)){
			//last 8 rows (28 : 35)
			row = player_sum - 12 + 27;
		}else if (hand_can_split){
			if (hand -> is_soft()){
				row = 27; //AA
			}else{
				row = player_sum/2 + 16;	//row 18 to 26
			}		
		}else{ //row 1 to 17
			row = player_sum - 3;
		}

		if (strategy_table.empty()){
			throw std::logic_error("no strategy_table");
		}

		std::string player_action;
		if (row != -1 && col != -1){
			player_action = strategy_table[row-1][col-1];
		}	


		//carry out player action
		std::unordered_set<char> actions;
		if (hand_can_split && hand->get_bjInstance()->players_hands.size() < 4){
			if (hand->is_from_split()){
				// options S H D P
				actions = {'S', 'H', 'D', 'P'};
			}
			else {
				// options S H D P R
				actions = {'S', 'H', 'D', 'P', 'R'};
			}
		}
		else if (hand -> is_dirty()){
			// options S H
			actions = {'S', 'H'};
		}
		else{
			if (hand->is_from_split()) {
				//options S H D
				actions = {'S', 'H', 'D'};
			}
			else {
				//options S H D R
				actions = {'S', 'H', 'D', 'R'};
			}
		}

		if (!actions.count(player_action[0])){ //action not available, take alt action

			if (player_action.size() == 2 ){
				player_action = std::toupper(player_action[1]);
			}
			else if (player_action[0] == 'P')
			{
				hand_can_split = false;
				goto Get_Strategy_From_Table;
			}
			else{
				throw std::logic_error("can't take action");
			}		
		}

		player_actions(hand, player_action);		
	}

	(void)hand;
	(void)dealer;
}


// void AutoPlayer::play(Hand* hand, const Hand* dealer)
// {
// 	// for debug:
// 	for (unsigned r = 0; r < strategy_table.size(); r ++) {
// 		for (unsigned c = 0; c < strategy_table[0].size(); c++) {
// 			std::cout << strategy_table[r][c] << "\t";
// 		}
// 		std::cout << '\n';
// 	}
// 	(void)hand;
// 	(void)dealer;
// }


bool AutoPlayer::again() const 
{
	if (get_hands_played() != nr_hands_to_play){
		return true;
	}
		
	return false;
}


AutoPlayer::~AutoPlayer()
{
	for (unsigned r = 0; r < strategy_table.size(); r ++)
	{
		for (unsigned c = 0; c < strategy_table[0].size(); c ++) 
		{
			delete strategy_table[r][c];
		}
	}
}


Player * Player::factory(const Config * config)
{
	ManualPlayer * player;
	if (config->strategy_file == nullptr)
	{
		player = new ManualPlayer;
		return player;
	}
	else
	{
		std::ifstream strat_file;
		strat_file.open(config->strategy_file);

		if (strat_file.fail()) return nullptr;

		AutoPlayer * player = new AutoPlayer;

		// parsing the file in to a table
		std::string line_buf;
		unsigned line_count = 0;
		while (std::getline(strat_file, line_buf))
		{
			if (line_count == 0)
			{
				line_count ++;
				continue;
			}
			std::istringstream line_stream;
			line_stream.str(line_buf);
			std::vector<char*> line_list;
			for (unsigned i = 0; i < 24; i ++)
			{
				
				std::string element_buf;
				if (!(line_stream >> element_buf)) {
					std::cout << "Parsing error at line " << line_count
						<< " element " << i << std::endl;
					delete player;
					return nullptr;
				}
				if (i == 0) continue;
				char* c_str_ele = new char[element_buf.length()+1];
				std::strcpy (c_str_ele, element_buf.c_str());
				line_list.push_back(c_str_ele);
			}
			player->strategy_table.push_back(line_list);
			line_count ++;
		}
		player -> nr_hands_to_play = config -> num_hands;
		player -> silent = config -> silent;
		strat_file.close();
		return player;

	}
	

	//return player;
}

void player_actions(Hand * hand, std::string player_action){

	player_action = std::tolower(player_action[0]);

/*
	std::unordered_set<std::string> stand = {"s"};
	std::unordered_set<std::string> hit = {"h"};
	std::unordered_set<std::string> double_bet = {"d"};
	std::unordered_set<std::string> split = {"p"};
	std::unordered_set<std::string> surrender = {"r"};

	if (stand.count(player_action)) 
			hand->stand();
	else if (hit.count(player_action)) 
		hand->hit();
	else if (double_bet.count(player_action) && !hand->is_dirty()) 
		hand->double_bet();
	else if (split.count(player_action) && hand->can_split()
		&& hand->get_bjInstance()->players_hands.size() < 4) {
		hand->split();
	}
	else if (surrender.count(player_action) && !hand->is_dirty()
		&& !hand->is_from_split()) 
		hand->surrender();
	else std::cout << ("Unrecognized action")  << std::endl;
	*/
	if (player_action[0] == 's') 
			hand->stand();
	else if (player_action[0] == 'h') 
		hand->hit();
	else if (player_action[0] == 'd' && !hand->is_dirty()) 
		hand->double_bet();
	else if (player_action[0] == 'p' && hand->can_split()
		&& hand->get_bjInstance()->players_hands.size() < 4) {
		hand->split();
	}
	else if (player_action[0] == 'r' && !hand->is_dirty()
		&& !hand->is_from_split()) 
		hand->surrender();
	else std::cout << ("Unrecognized action")  << std::endl;
}

