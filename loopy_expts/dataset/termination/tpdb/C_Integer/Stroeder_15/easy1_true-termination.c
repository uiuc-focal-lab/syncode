// Source: data/benchmarks/tpdb/C_Integer/Stroeder_15/easy1_true-termination.c
#include <stdlib.h>
#define assume(e) if(!(e)) exit(-1);
extern int unknown_int(void);

typedef enum {false, true} bool;

int main() {
    int x, y, z;
	x = 0;
    y = 100;
    z = unknown_int();
	while (x < 40) {
		if (z == 0) {
			x = x + 1;
		} else {
			x = x + 2;
		}
	}
	return 0;
}