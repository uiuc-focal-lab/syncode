// Source: data/benchmarks/tpdb/C_Integer/Stroeder_15/Masse-VMCAI2014-Fig1a_true-termination.c
#include <stdlib.h>
#define assume(e) if(!(e)) exit(-1);
extern int unknown_int(void);

typedef enum {false, true} bool;

int main() {
    int a, b;
	a = unknown_int();
	b = unknown_int();
	while (a >= 0) {
		a = a + b;
		if (b >= 0) {
			b = -b - 1;
		} else {
			b = -b;
		}
	}
	return 0;
}