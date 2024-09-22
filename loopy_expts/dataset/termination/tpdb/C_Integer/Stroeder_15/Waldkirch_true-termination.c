// Source: data/benchmarks/tpdb/C_Integer/Stroeder_15/Waldkirch_true-termination.c
#include <stdlib.h>
#define assume(e) if(!(e)) exit(-1);

typedef enum {false, true} bool;

int main()
{
	int x;
    x = 0;
	while (x >= 0) {
		x = x - 1;
	}
	return 0;
}