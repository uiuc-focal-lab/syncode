// Source: data/benchmarks/tpdb/C_Integer/Stroeder_15/GulavaniGulwani-CAV2008-Fig1a_true-termination.c
#include <stdlib.h>
#define assume(e) if(!(e)) exit(-1);
extern int unknown_int(void);

typedef enum {false, true} bool;

int main() {
    int x, y, z, i;
	x = unknown_int();
	y = unknown_int();
	z = unknown_int();
	i = unknown_int();
	while (x < y) {
		i = i + 1;
		if (z > x) {
			x = x + 1;
		} else {
			z = z + 1;
		}
	}
	return 0;
}