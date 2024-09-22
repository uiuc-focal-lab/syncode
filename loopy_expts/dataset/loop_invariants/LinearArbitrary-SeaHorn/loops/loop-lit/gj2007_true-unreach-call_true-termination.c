// Source: data/benchmarks/LinearArbitrary-SeaHorn/loops/loop-lit/gj2007_true-unreach-call_true-termination.c
#include <stdlib.h>
#define assume(e) if(!(e)) exit(-1);

int main() {
    int x = 0;
    int y = 50;
    while(x < 100) {
	if (x < 50) {
	    x = x + 1;
	} else {
	    x = x + 1;
	    y = y + 1;
	}
    }
    {;
//@ assert(y == 100);
}

    return 0;
}