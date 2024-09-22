// Source: data/benchmarks/tpdb/C/SV-COMP_Termination_Category/PodelskiRybalchenko-TACAS2011-Fig4_true-termination.c
#include <stdlib.h>
#define assume(e) if(!(e)) exit(-1);
extern int unknown_int(void);

int main() {
	int x = unknown_int();
	int y = unknown_int();
	while (x > 0 && y > 0) {
		if (unknown_int()) {
			x = x - 1;
			y = unknown_int();
		} else {
			y = y - 1;
		}
	}
	return 0;
}