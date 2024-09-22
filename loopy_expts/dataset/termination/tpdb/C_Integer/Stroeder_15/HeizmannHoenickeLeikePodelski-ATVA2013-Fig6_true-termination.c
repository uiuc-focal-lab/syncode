// Source: data/benchmarks/tpdb/C_Integer/Stroeder_15/HeizmannHoenickeLeikePodelski-ATVA2013-Fig6_true-termination.c
#include <stdlib.h>
#define assume(e) if(!(e)) exit(-1);
extern int unknown_int(void);

typedef enum {false, true} bool;

int main() {
    int x, y;
	x = unknown_int();
	y = unknown_int();
	while (x >= 0 && y >= 1) {
		x = x - y;
		y = unknown_int();
	}
	return 0;
}