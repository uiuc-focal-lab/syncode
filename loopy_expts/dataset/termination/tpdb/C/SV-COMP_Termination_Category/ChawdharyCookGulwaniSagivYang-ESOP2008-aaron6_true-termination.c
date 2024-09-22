// Source: data/benchmarks/tpdb/C/SV-COMP_Termination_Category/ChawdharyCookGulwaniSagivYang-ESOP2008-aaron6_true-termination.c
#include <stdlib.h>
#define assume(e) if(!(e)) exit(-1);
extern int unknown_int(void);

int main() {
	int x = unknown_int();
	int tx = unknown_int();
	int y = unknown_int();
	int ty = unknown_int();
	int n = unknown_int();
	if (x + y >= 0) {
		while (x <= n && x >= 2 * tx + y && y >= ty + 1 && x >= tx + 1) {
			if (unknown_int()) {
				tx = x;
				ty = y;
				x = unknown_int();
				y = unknown_int();
			} else {
				tx = x;
				x = unknown_int();
			}
		}
	}	
	return 0;
}