// Source: data/benchmarks/tpdb/C_Integer/Stroeder_15/4NestedWith3Variables_true-termination.c
#include <stdlib.h>
#define assume(e) if(!(e)) exit(-1);
extern int unknown_int(void);

typedef enum {false, true} bool;

int main()
{
    int a, b, q, olda;
	q = unknown_int();
	a = unknown_int();
	b = unknown_int();
	while (q > 0) {
		q = q + a - 1;
		olda = a;
		a = 3*olda - 4*b;
		b = 4*olda + 3*b;
	}
	return 0;
}