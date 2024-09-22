// Source: data/benchmarks/tpdb/C_Integer/Stroeder_15/ChawdharyCookGulwaniSagivYang-ESOP2008-aaron6_true-termination.c
#include <stdlib.h>
#define assume(e) if(!(e)) exit(-1);
extern int unknown_int(void);

typedef enum {false, true} bool;

int main() {
    int x, tx, y, ty, n;
	x = unknown_int();
	tx = unknown_int();
	y = unknown_int();
	ty = unknown_int();
	n = unknown_int();
	if (x + y >= 0) {
		while (x <= n && x >= 2 * tx + y && y >= ty + 1 && x >= tx + 1) {
			if (unknown_int() != 0) {
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