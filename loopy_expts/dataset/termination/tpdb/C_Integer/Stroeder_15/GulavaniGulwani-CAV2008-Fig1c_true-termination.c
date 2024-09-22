// Source: data/benchmarks/tpdb/C_Integer/Stroeder_15/GulavaniGulwani-CAV2008-Fig1c_true-termination.c
#include <stdlib.h>
#define assume(e) if(!(e)) exit(-1);
extern int unknown_int(void);

typedef enum {false, true} bool;

int main() {
    int x, i, n;
	x = unknown_int();
	i = unknown_int();
	n = unknown_int();
	while (x < n) {
		i = i + 1;
		x = x + 1;
	}
	return 0;
}