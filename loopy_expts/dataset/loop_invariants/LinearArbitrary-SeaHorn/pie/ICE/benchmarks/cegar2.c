// Source: data/benchmarks/LinearArbitrary-SeaHorn/pie/ICE/benchmarks/cegar2.c
#include <stdlib.h>
#define assume(e) if(!(e)) exit(-1);
extern int unknown_int(void);

int main() {

	int N = unknown_int();
	int x = 0;
	int m = 0;
	int input;

 	while (x < N) {

		input = unknown_int();
		if( input ) {

			m = x;
		}

		x = x + 1;

	}

	if (N > 0) {
		{;
//@ assert((0 <= m) && (m < N));
}

	}

}