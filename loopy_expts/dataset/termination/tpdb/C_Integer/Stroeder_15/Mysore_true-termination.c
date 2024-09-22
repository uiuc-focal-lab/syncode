// Source: data/benchmarks/tpdb/C_Integer/Stroeder_15/Mysore_true-termination.c
#include <stdlib.h>
#define assume(e) if(!(e)) exit(-1);
extern int unknown_int(void);

typedef enum {false, true} bool;

int main()
{
    int c, x;
	x = unknown_int();
	c = unknown_int();
	if (c >= 2) {
	    while (x + c >= 0) {
		    x = x - c;
		    c = c + 1;
	    }
    }
	return 0;
}