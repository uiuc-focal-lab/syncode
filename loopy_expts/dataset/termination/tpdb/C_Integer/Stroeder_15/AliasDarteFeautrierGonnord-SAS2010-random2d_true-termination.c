// Source: data/benchmarks/tpdb/C_Integer/Stroeder_15/AliasDarteFeautrierGonnord-SAS2010-random2d_true-termination.c
#include <stdlib.h>
#define assume(e) if(!(e)) exit(-1);
extern int unknown_int(void);

typedef enum {false, true} bool;

int main() {
    int N, x, y, i, r;
	N = 10;
    x = 0;
    y = 0;
    i = 0;
	while (i < N) {
		i = i + 1;
		r = unknown_int();
		if (r >= 0 && r <= 3) {
			if (r == 0) {
				x = x + 1;
			} else {if (r == 1) {
				x = x - 1;
			} else {if (r == 2) {
				y = y + 1;
			} else {if (r == 3) {
				y = y - 1;
            }}}}
		}
	}
	return 0;
}