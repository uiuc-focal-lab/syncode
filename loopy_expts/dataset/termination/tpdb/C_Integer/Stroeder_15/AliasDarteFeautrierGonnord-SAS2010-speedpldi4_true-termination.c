// Source: data/benchmarks/tpdb/C_Integer/Stroeder_15/AliasDarteFeautrierGonnord-SAS2010-speedpldi4_true-termination.c
#include <stdlib.h>
#define assume(e) if(!(e)) exit(-1);
extern int unknown_int(void);

typedef enum {false, true} bool;

int main() {
    int i, m, n;
	n = unknown_int();
	m = unknown_int();
	if (m > 0 && n > m) {
		i = n;
		while (i > 0) {
			if (i < m) {
				i = i - 1;
			} else {
				i = i - m;
            }
		}
	}
	return 0;
}