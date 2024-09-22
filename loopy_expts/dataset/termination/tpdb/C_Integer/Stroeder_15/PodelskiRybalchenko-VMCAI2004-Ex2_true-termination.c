// Source: data/benchmarks/tpdb/C_Integer/Stroeder_15/PodelskiRybalchenko-VMCAI2004-Ex2_true-termination.c
#include <stdlib.h>
#define assume(e) if(!(e)) exit(-1);
extern int unknown_int(void);

typedef enum {false, true} bool;

int main() {
	int x;
    x = unknown_int();
	while ( x >= 0 ) {
		x = -2*x + 10;
	}
	return 0;
}