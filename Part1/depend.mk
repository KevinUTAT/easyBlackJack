easybj.o: easybj.cpp easybj.h shoe.h player.h Hand.h config.h
player.o: player.cpp player.h Hand.h shoe.h easybj.h config.h
config.o: config.cpp config.h player.h shoe.h
Hand.o: Hand.cpp Hand.h shoe.h easybj.h config.h
shoe.o: shoe.cpp shoe.h config.h
main.o: main.cpp easybj.h shoe.h config.h player.h
