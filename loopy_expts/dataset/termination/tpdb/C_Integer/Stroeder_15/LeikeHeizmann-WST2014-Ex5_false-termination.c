// Source: data/benchmarks/tpdb/C_Integer/Stroeder_15/LeikeHeizmann-WST2014-Ex5_false-termination.c
#include <stdlib.h>
#define assume(e) if(!(e)) exit(-1);
extern int unknown_int(void);

typedef enum {false, true} bool;

int main() {
    int a, b, olda;
	a = unknown_int();
	b = unknown_int();
	while (a >= 7) {
		olda = a;
		a = b;
		b = olda + 1;
		
	}
	return 0;
}