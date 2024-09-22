// Source: data/benchmarks/tpdb/C_Integer/Stroeder_15/PodelskiRybalchenko-TACAS2011-Fig1_true-termination.c
#include <stdlib.h>
#define assume(e) if(!(e)) exit(-1);
extern int unknown_int(void);

typedef enum {false, true} bool;

int main() {
	int y;
    y = unknown_int();
	while (y >= 0) {
		y = y - 1;
	}
	return 0;
}