// Source: data/benchmarks/LinearArbitrary-SeaHorn/pie/ICE/benchmarks/fig3.c
#include <stdlib.h>
#define assume(e) if(!(e)) exit(-1);
extern int unknown_int(void);

int main() {

	int y = unknown_int();
	int lock;
	lock = 0;
	int x = unknown_int();
	int input;

	{
		lock = 1;
		x = y;
		input = unknown_int();
		if( input ) {

			lock = 0;
			y = y + 1;
		}
	}

	while(x != y) {

		lock = 1;
		x = y;
		input = unknown_int();
		if ( input ) {

			lock = 0;
			y = y + 1;
		}
	}

	{;
//@ assert(lock == 1);
}

}
