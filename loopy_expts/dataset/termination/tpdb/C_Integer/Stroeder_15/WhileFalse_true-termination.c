// Source: data/benchmarks/tpdb/C_Integer/Stroeder_15/WhileFalse_true-termination.c
#include <stdlib.h>
#define assume(e) if(!(e)) exit(-1);

typedef enum {false, true} bool;

int main()
{
	while (false) {
	}
	return 0;
}