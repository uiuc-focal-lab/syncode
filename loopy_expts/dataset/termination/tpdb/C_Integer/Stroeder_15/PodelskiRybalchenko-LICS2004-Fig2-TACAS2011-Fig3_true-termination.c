// Source: data/benchmarks/tpdb/C_Integer/Stroeder_15/PodelskiRybalchenko-LICS2004-Fig2-TACAS2011-Fig3_true-termination.c
#include <stdlib.h>
#define assume(e) if(!(e)) exit(-1);
extern int unknown_int(void);

typedef enum {false, true} bool;

int main() {
    int x, y, oldx, oldy;
	x = unknown_int();
	y = unknown_int();
	while (x > 0 && y > 0) {
		oldx = x;
		oldy = y;
		if (unknown_int() != 0) {
			x = oldx - 1;
			y = oldx;
		} else {
			x = oldy - 2;
			y = oldx + 1;
		}
	}
	return 0;
}