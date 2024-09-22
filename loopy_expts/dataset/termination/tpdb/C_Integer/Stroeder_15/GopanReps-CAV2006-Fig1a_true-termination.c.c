// Source: data/benchmarks/tpdb/C_Integer/Stroeder_15/GopanReps-CAV2006-Fig1a_true-termination.c.c
#include <stdlib.h>
#define assume(e) if(!(e)) exit(-1);

typedef enum {false, true} bool;

int main() {
    int x, y;
	x = 0;
    y = 0;
	while (y >= 0) {
		if (x <= 50) {
			y = y + 1;
		} else {
			y = y - 1;
		}
		x = x + 1;
	}
	return 0;
}