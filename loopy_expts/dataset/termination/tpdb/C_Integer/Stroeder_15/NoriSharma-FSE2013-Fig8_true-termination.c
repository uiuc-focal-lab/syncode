// Source: data/benchmarks/tpdb/C_Integer/Stroeder_15/NoriSharma-FSE2013-Fig8_true-termination.c
#include <stdlib.h>
#define assume(e) if(!(e)) exit(-1);
extern int unknown_int(void);

typedef enum {false, true} bool;

int main() {
    int c, u, v, w, x, y, z;
	x = unknown_int();
	y = unknown_int();
	z = unknown_int();
    u = x;
    v = y;
    w = z;
    c = 0;
    while (x >= y) {
    	c = c + 1;
    	if (z > 1) {
    		z = z - 1;
    		x = x + z;
    	} else {
    		y = y + 1;
    	}
    }
    return 0;
}