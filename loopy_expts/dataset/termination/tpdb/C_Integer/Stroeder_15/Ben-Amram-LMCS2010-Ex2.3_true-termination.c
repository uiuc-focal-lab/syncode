// Source: data/benchmarks/tpdb/C_Integer/Stroeder_15/Ben-Amram-LMCS2010-Ex2.3_true-termination.c
#include <stdlib.h>
#define assume(e) if(!(e)) exit(-1);
extern int unknown_int(void);

typedef enum {false, true} bool;

int main() {
    int x, y, z;
	x = unknown_int();
	y = unknown_int();
	z = unknown_int();

	while (x > 0 && y > 0 && z > 0) {
		if (y > x) {
			y = z;
			x = unknown_int();
			z = x - 1;
		} else {
			z = z - 1;
			x = unknown_int();
			y = x - 1;
		}
	}
	return 0;
}