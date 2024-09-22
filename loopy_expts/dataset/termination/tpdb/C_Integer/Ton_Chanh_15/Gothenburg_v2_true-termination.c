// Source: data/benchmarks/tpdb/C_Integer/Ton_Chanh_15/Gothenburg_v2_true-termination.c
#include <stdlib.h>
#define assume(e) if(!(e)) exit(-1);
extern int unknown_int(void);

typedef enum {false, true} bool;

int main()
{
    int x, y, a, b;
    a = unknown_int();
    b = unknown_int();
    x = unknown_int();
    y = unknown_int();
	if (a == b + 1 && x < 0) {
	    while (x >= 0 || y >= 0) {
		    x = x + a - b - 1;
	    	y = y + b - a - 1;
    	}
	}
	return 0;
}