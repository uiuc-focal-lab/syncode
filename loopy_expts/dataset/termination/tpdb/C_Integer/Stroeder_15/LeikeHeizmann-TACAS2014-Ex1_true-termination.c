// Source: data/benchmarks/tpdb/C_Integer/Stroeder_15/LeikeHeizmann-TACAS2014-Ex1_true-termination.c
#include <stdlib.h>
#define assume(e) if(!(e)) exit(-1);
extern int unknown_int(void);

typedef enum {false, true} bool;

int main() {
    int q, y;
	q = unknown_int();
	y = unknown_int();
	while (q > 0) {
		if (y > 0) {
			q = q - y - 1;
		} else {
			q = q + y - 1;
		}
	}
	return 0;
}