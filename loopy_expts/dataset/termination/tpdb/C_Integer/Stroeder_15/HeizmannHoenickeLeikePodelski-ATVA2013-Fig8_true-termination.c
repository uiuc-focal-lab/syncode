// Source: data/benchmarks/tpdb/C_Integer/Stroeder_15/HeizmannHoenickeLeikePodelski-ATVA2013-Fig8_true-termination.c
#include <stdlib.h>
#define assume(e) if(!(e)) exit(-1);
extern int unknown_int(void);

typedef enum {false, true} bool;

int main() {
    int x, y;
	x = unknown_int();
	y = unknown_int();
	if (2*y >= 1) {
    	while (x >= 0) {
	    	x = x - 2*y + 1;
	    }
	}
	return 0;
}