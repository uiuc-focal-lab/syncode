// Source: data/benchmarks/tpdb/C/SV-COMP_Termination_Category/aaron3_true-termination.c
#include <stdlib.h>
#define assume(e) if(!(e)) exit(-1);
extern int unknown_int(void);

int main() {
	int x = unknown_int();
	int y = unknown_int();
	int z = unknown_int();
	int tx = unknown_int();
	while (x >= y && x <= tx + z) {
		if (unknown_int()) {
			z = z - 1;
			tx = x;
			x = unknown_int();
		} else {
			y = y + 1;
		}
	}
	return 0;
}