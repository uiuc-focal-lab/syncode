// Source: data/benchmarks/tpdb/C_Integer/Stroeder_15/aaron2_true-termination.c
#include <stdlib.h>
#define assume(e) if(!(e)) exit(-1);
extern int unknown_int(void);

typedef enum {false, true} bool;

int main() {
    int x, y, tx;
	tx = unknown_int();
	x = unknown_int();
	y = unknown_int();
	while (x >= y && tx >= 0) {
		if (unknown_int() != 0) {
			x = x - 1 - tx;
		} else {
			y = y + 1 + tx;
		}
	}
	return 0;
}