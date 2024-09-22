// Source: data/benchmarks/tpdb/C_Integer/Stroeder_15/AliasDarteFeautrierGonnord-SAS2010-terminate_true-termination.c
#include <stdlib.h>
#define assume(e) if(!(e)) exit(-1);
extern int unknown_int(void);

typedef enum {false, true} bool;

int main() {
    int i, j, k, ell;
	i = unknown_int();
	j = unknown_int();
	k = unknown_int();
	while (i <= 100 && j <= k) {
		ell = i;
		i = j;
		j = ell + 1;
		k = k - 1;
	}
	return 0;
}