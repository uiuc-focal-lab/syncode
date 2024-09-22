// Source: data/benchmarks/tpdb/C_Integer/Stroeder_15/AliasDarteFeautrierGonnord-SAS2010-speedpldi2_true-termination.c
#include <stdlib.h>
#define assume(e) if(!(e)) exit(-1);
extern int unknown_int(void);

typedef enum {false, true} bool;

int main() {
    int m, n, v1, v2;
	n = unknown_int();
	m = unknown_int();
	if (n >= 0 && m > 0) {
		v1 = n;
		v2 = 0;
		while (v1 > 0) {
			if (v2 < m) {
				v2 = v2 + 1;
				v1 = v1 - 1;
			} else {
				v2 = 0;
			}
		}
	}
	return 0;
}