// Source: data/benchmarks/tpdb/C_Integer/Stroeder_15/CookSeeZuleger-TACAS2013-Fig8b_true-termination.c
#include <stdlib.h>
#define assume(e) if(!(e)) exit(-1);
extern int unknown_int(void);

typedef enum {false, true} bool;

int main() {
    int x, M;
	x = unknown_int();
	M = unknown_int();
	if (M > 0) {
		while (x != M) {
			if (x > M) {
				x = 0;
			} else {
				x = x + 1;
            }
		}
	}
	return 0;
}