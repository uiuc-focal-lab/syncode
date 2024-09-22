// Source: data/benchmarks/tpdb/C_Integer/Stroeder_15/LeikeHeizmann-TACAS2014-Ex7_true-termination.c
#include <stdlib.h>
#define assume(e) if(!(e)) exit(-1);
extern int unknown_int(void);

typedef enum {false, true} bool;

int main() {
    int q, z;
	q = unknown_int();
	z = unknown_int();
	while (q > 0) {
		q = q + z - 1;
		z = -z;
	}
	return 0;
}