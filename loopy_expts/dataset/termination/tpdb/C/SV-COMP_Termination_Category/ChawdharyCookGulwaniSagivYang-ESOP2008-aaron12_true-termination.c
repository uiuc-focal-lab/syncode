// Source: data/benchmarks/tpdb/C/SV-COMP_Termination_Category/ChawdharyCookGulwaniSagivYang-ESOP2008-aaron12_true-termination.c
#include <stdlib.h>
#define assume(e) if(!(e)) exit(-1);
extern int unknown_int(void);

int main() {
	int x = unknown_int();
	int y = unknown_int();
	int z = unknown_int();
	while (x >= y) {
		if (unknown_int()) {
			x = x + 1;
			y = y + x;
		} else {
			x = x - z;
			y = y + (z * z);
			z = z - 1;
		}
	}
	return 0;
}