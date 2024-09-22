// Source: data/benchmarks/tpdb/C_Integer/Stroeder_15/AliasDarteFeautrierGonnord-SAS2010-wise_true-termination.c
#include <stdlib.h>
#define assume(e) if(!(e)) exit(-1);
extern int unknown_int(void);

typedef enum {false, true} bool;

int main() {
    int x, y;
	x = unknown_int();
	y = unknown_int();
	if (x >= 0 && y >= 0) {
		while (x - y > 2 || y - x > 2) {
			if (x < y) {
				x = x + 1;
			} else {
				y = y + 1;
			}
		}
	}
	return 0;
}