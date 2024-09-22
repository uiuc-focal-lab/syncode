// Source: data/benchmarks/tpdb/C/SV-COMP_Termination_Category/aaron2_true-termination.c
#include <stdlib.h>
#define assume(e) if(!(e)) exit(-1);
extern int unknown_int(void);

int main() {
	int tx = unknown_int();
	int x = unknown_int();
	int y = unknown_int();
	while (x >= y && tx >= 0) {
		if (unknown_int()) {
			x = x - 1 - tx;
		} else {
			y = y + 1 + tx;
		}
	}
	return 0;
}