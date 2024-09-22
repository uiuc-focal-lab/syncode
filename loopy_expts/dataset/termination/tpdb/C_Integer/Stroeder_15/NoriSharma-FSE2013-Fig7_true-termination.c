// Source: data/benchmarks/tpdb/C_Integer/Stroeder_15/NoriSharma-FSE2013-Fig7_true-termination.c
#include <stdlib.h>
#define assume(e) if(!(e)) exit(-1);
extern int unknown_int(void);

typedef enum {false, true} bool;

int main() {
	int a, b, c, i, j, M, N;
	i = unknown_int();
	j = unknown_int();
	M = unknown_int();
	N = unknown_int();
    a = i;
    b = j;
    c = 0;
    while (i<M || j<N) {
    	i = i + 1;
    	j = j + 1;
    	c = c + 1;
    }
    return 0;
}