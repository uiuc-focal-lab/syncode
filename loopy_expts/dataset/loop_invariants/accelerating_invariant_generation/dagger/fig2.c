// Source: data/benchmarks/accelerating_invariant_generation/dagger/fig2.c
#include <stdlib.h>
#define assume(e) if(!(e)) exit(-1);
extern int unknown_int(void);

int nondet_int();

void main () {

int x, y, z, w;
x=y=z=w=0;

while (unknown_int() ) {

if (unknown_int()) {x++; y = y+2;}
else if (unknown_int()) {
	if (x >= 4) {x++; y = y+3; z = z+10; w = w+10;}
}
else if (x >= z && w > y) {x = -x; y = -y; }

}

{;
//@ assert(3*x >= y);
}

}