// Source: data/benchmarks/tpdb/C_Integer/Stroeder_15/Gothenburg_true-termination.c
#include <stdlib.h>
#define assume(e) if(!(e)) exit(-1);
extern int unknown_int(void);

typedef enum {false, true} bool;

int main()
{
    int a, b, x, y;
	a = unknown_int();
	b = unknown_int();
	x = unknown_int();
	y = unknown_int();
	if (a == b) {
	    while (x >= 0 || y >= 0) {
		    x = x + a - b - 1;
	    	y = y + b - a - 1;
    	}
	}
	return 0;
}