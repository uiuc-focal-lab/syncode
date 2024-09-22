// Source: data/benchmarks/LinearArbitrary-SeaHorn/pie/ICE/benchmarks/fig3.v.c
#include <stdlib.h>
#define assume(e) if(!(e)) exit(-1);
extern int unknown_int(void);

int main() {

	int y = unknown_int();
	int lock, v1,v2,v3;
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
		v1 = unknown_int();
		v2 = unknown_int();
		v3 = unknown_int();

	}

	while(x != y) {

		lock = 1;
		x = y;
		input = unknown_int();
		if ( input ) {

			lock = 0;
			y = y + 1;
		}
		v1 = unknown_int();
		v2 = unknown_int();
		v3 = unknown_int();
	}

	{;
//@ assert(lock == 1);
}

}
