// Source: data/benchmarks/LinearArbitrary-SeaHorn/VeriMAP/MAP-singleloop2-pepm-proc.c_VeriMAP_true.c
#include <stdlib.h>
#define assume(e) if(!(e)) exit(-1);
extern int unknown_int(void);

;
int main() {
int x=0;
int y=0;
int n = unknown_int();

	assume(n>=1);

	while(x < 2*n){
	   x = x + 1;

	   if ( x > n )
		  y = y - 1;
	   else
		  y = y + 2;
	}

	if(x < y)
		goto ERROR;

	return 0;
{ ERROR: {; 
//@ assert(\false);
}
}
	return -1;
}