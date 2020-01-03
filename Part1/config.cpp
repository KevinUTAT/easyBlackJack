/*
 * config.cpp
 *
 * Parses program arguments and returns Config object
 *
 * Note: change this file to parse program arguments
 *
 * University of Toronto
 * Fall 2019
 */
 
#include "config.h"
#include "player.h"
#include "shoe.h"
#include <cstdio>
#include <getopt.h>
#include <cstring>
#include <vector>
#include <string>

static int
usage(const char * prog) {
	fprintf(stderr, "usage: %s [-h] [-f FILE|-i SEED [-r FILE]] [[-s] -a FILE NUM]\n", prog);
	fprintf(stderr, "Options:\n");
	fprintf(stderr, " -h:\tDisplay this message\n");
	fprintf(stderr, " -f:\tUse file-based shoe\n");
	fprintf(stderr, " -i:\tUse random-based shoe (default)\n");
	fprintf(stderr, " -r:\tRecord random-based shoe to file\n");
	fprintf(stderr, " -a:\tPlay automatically using strategy chart\n");
	fprintf(stderr, " -s:\tSilent mode\n");
	fprintf(stderr, " FILE:\tFile name for associated option\n");
	fprintf(stderr, " SEED:\trandom seed\n");
	fprintf(stderr, " NUM:\tnumber of hands to be played\n");
	return -1;
}

int
Config::process_arguments(int argc, const char * argv[])
{
    /*
     * TODO: implement this 
     */
     /*
    if (argc == 2 && !strcmp(argv[1], "-h")) {
        return usage(argv[0]);
    }
*/
	int opt;
	std::string opt_buf = "";

	while ((opt = getopt(argc, (char**)argv, "hf:i:r:a:s")) != -1)
	{
		switch (opt)
		{
			case 'h': 
				return usage(argv[0]);;
			case 'f':
				if (opt_buf.find('i') != std::string::npos) 
				{
					fprintf(stderr, 
						"Error: cannot choose both file and random-based shoe.\n");
					return -1;
				}
				else
				{
					shoe_file = optarg;
					opt_buf.append("f");
				}
				break;
			case 'i':
				if (opt_buf.find('f') != std::string::npos)
				{
					fprintf(stderr, 
						"Error: cannot choose both file and random-based shoe.\n");
					return -1;
				}
				else
				{
					if (atol(optarg) < 0)  // atol return 0 if it cannot convert the string to integer
					{
						// printf("Error: SEED must be a non-negative integer\n");
						fprintf(stderr, 
							"Error: SEED must be a non-negative integer.\n");
						return -1;
					}
					/*
					if ((atof(optarg) - atol(optarg) != 0) || atol(optarg) == 0) // check if the input is a int
					{
						fprintf(stderr, 
							"Error: NUM must be a natural number.\n");
						// printf("NUM=%ld\n", atol(optarg));
						return -1;
					}
					*/
					random_seed = atol(optarg);
					opt_buf.append("i");
				}
				break;
			case 'r':
				if (opt_buf.find('f') != std::string::npos)
				{
					fprintf(stderr, 
						"Error: recording is only available for random-based shoe.\n");
					return -1;
				}
				else
				{
					record_file = optarg;
					opt_buf.append("r");
				}
				break;
			case 'a':
				strategy_file = optarg;
				
				if (argc <= optind)
				{
					fprintf(stderr, 
						"Error: must specify number of hands when playing automatically.\n");
					return -1;
				}
				num_hands = atol(argv[optind]);
				
				
				
				/*
				if (argv[optind] && !argv[optind][0])
				{
					fprintf(stderr, 
						"Error: must specify number of hands when playing automatically.\n");
					return -1;
				}*/
				if ((atof(argv[optind]) - atol(argv[optind]) != 0) || atol(argv[optind]) == 0) // check if the input is a int
				{
					fprintf(stderr, 
						"Error: NUM must be a natural number.\n");
					// printf("NUM=%ld\n", atol(optarg));
					return -1;
				}
				
				optind ++;
				opt_buf.append("a");
				break;
			case 's':
				silent = true;
				opt_buf.append("s");
				break;
			case '?':
				return -1;

		}
	}

	// error checking

	if (opt_buf.find('s') != std::string::npos 
		&& opt_buf.find('a') == std::string::npos)
	{
		fprintf(stderr, 
			"Error: silent mode is only available when playing automatically.\n");
		return -1;				
	}


	player = Player::factory(this);
	if (player == nullptr) {
		fprintf(stderr, "Error: cannot instantiate Player. (bad file?)\n");
		return usage(argv[0]);
	}
	
	shoe = Shoe::factory(this);
	if (shoe == nullptr) {
		fprintf(stderr, "Error: cannot instantiate Shoe. (bad file?)\n");
		return usage(argv[0]);
	}	
	
	return 0;
}

Config::~Config()
{
	if (player != nullptr)
		delete player;
	
	if (shoe != nullptr)
		delete shoe;
}

