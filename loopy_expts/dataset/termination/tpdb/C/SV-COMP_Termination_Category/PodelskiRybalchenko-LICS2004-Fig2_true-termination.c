// Source: data/benchmarks/tpdb/C/SV-COMP_Termination_Category/PodelskiRybalchenko-LICS2004-Fig2_true-termination.c
#include <stdlib.h>
#define assume(e) if(!(e)) exit(-1);
extern int unknown_int(void);

int main() {
	int x = unknown_int();
	int y = unknown_int();
	while (x > 0 && y > 0) {
		int old_x = x;
		int old_y = y;
		if (unknown_int()) {
			x = old_x - 1;
			y = old_x;
		} else {
			x = old_y - 2;
			y = old_x + 1;
		}
	}
	return 0;
}