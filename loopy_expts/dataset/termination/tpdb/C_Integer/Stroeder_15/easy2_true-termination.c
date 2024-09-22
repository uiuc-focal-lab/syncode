// Source: data/benchmarks/tpdb/C_Integer/Stroeder_15/easy2_true-termination.c
#include <stdlib.h>
#define assume(e) if(!(e)) exit(-1);
extern int unknown_int(void);

typedef enum {false, true} bool;

int main() {
    int x, y, z;
	x = 12;
    y = 0;
    z = unknown_int();
	while (z > 0) {
		x = x + 1;
		y = y - 1;
		z = z - 1;
	}
	return 0;
}