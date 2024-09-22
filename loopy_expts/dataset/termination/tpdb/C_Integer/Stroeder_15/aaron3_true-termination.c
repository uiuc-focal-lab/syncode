// Source: data/benchmarks/tpdb/C_Integer/Stroeder_15/aaron3_true-termination.c
#include <stdlib.h>
#define assume(e) if(!(e)) exit(-1);
extern int unknown_int(void);

typedef enum {false, true} bool;

int main() {
    int x, y, z, tx;
	x = unknown_int();
	y = unknown_int();
	z = unknown_int();
	tx = unknown_int();
	while (x >= y && x <= tx + z) {
		if (unknown_int() != 0) {
			z = z - 1;
			tx = x;
			x = unknown_int();
		} else {
			y = y + 1;
		}
	}
	return 0;
}