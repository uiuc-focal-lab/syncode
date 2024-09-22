// Source: data/benchmarks/LinearArbitrary-SeaHorn/loops/loop-lit/gj2007b_true-unreach-call_true-termination.c
#include <stdlib.h>
#define assume(e) if(!(e)) exit(-1);
extern int unknown_int(void);

int main() {
    int x = 0;
    int m = 0;
    int n = unknown_int();
    while(x < n) {
	if(unknown_int()) {
	    m = x;
	}
	x = x + 1;
    }
    {;
//@ assert((m >= 0 || n <= 0));
}

    {;
//@ assert((m < n || n <= 0));
}

    return 0;
}