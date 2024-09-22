// Source: data/benchmarks/tpdb/C_Integer/Stroeder_15/ColonSipma-TACAS2001-Fig1_true-termination.c
#include <stdlib.h>
#define assume(e) if(!(e)) exit(-1);
extern int unknown_int(void);

typedef enum {false, true} bool;

int main() {
    int k, i, j, tmp;
	k = unknown_int();
    i = unknown_int();
    j = unknown_int();
	while (i <= 100 && j <= k) {
		tmp = i;
		i = j;
		j = tmp + 1;
		k = k - 1;
	}
	return 0;
}