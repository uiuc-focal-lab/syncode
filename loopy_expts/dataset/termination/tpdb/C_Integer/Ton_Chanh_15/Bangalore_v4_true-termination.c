// Source: data/benchmarks/tpdb/C_Integer/Ton_Chanh_15/Bangalore_v4_true-termination.c
#include <stdlib.h>
#define assume(e) if(!(e)) exit(-1);
extern int unknown_int(void);

typedef enum {false, true} bool;

int main()
{
    int x;
    int y;
    x = unknown_int();
    y = unknown_int();
	if (y > x) {
	    while (x >= 0) {
	    	x = x - y;
    	}
	}
	return 0;
}