// Source: data/benchmarks/LinearArbitrary-SeaHorn/VeriMAP/TRACER-paper-prog_d-pepm-proc.c_VeriMAP_true.c
#include <stdlib.h>
#define assume(e) if(!(e)) exit(-1);
extern unsigned int unknown_uint(void);

;

void errorFn() {ERROR: goto ERROR;}
int main(){
int y = unknown_uint();
int x=0;

    assume(y>=0);

	while ( x < 10000) {
		y = y + 1;
		x = x + 1;
	}

	if( y + x < 10000)		
		goto ERROR;

	return 0;
{ ERROR: {; 
//@ assert(\false);
}
}
	return -1;
}