// Source: data/benchmarks/tpdb/C_Integer/Stroeder_15/AliasDarteFeautrierGonnord-SAS2010-counterex1a_true-termination.c
#include <stdlib.h>
#define assume(e) if(!(e)) exit(-1);
extern int unknown_int(void);

typedef enum {false, true} bool;

int main() {
    int x, y, n, b;
	n = unknown_int();
	b = unknown_int();
	x = unknown_int();
	y = unknown_int();
	while (x >= 0 && 0 <= y && y <= n) {
		if (b == 0) {
			y = y + 1;
			if (unknown_int() != 0) {
				b = 1;
            }
		} else {
			y = y - 1;
			if (unknown_int() != 0) {
				x = x - 1;
				b = 0;
			}
		}
	}
	return 0;
}