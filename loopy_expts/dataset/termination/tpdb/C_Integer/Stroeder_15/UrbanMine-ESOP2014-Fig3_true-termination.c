// Source: data/benchmarks/tpdb/C_Integer/Stroeder_15/UrbanMine-ESOP2014-Fig3_true-termination.c
#include <stdlib.h>
#define assume(e) if(!(e)) exit(-1);
extern int unknown_int(void);

typedef enum {false, true} bool;

int main() {
	int x;
	int y;
	x = unknown_int();
	y = unknown_int();
	while (x != 0 && y > 0) {
	    if (x > 0) {
		    if (unknown_int() != 0) {
			    x = x - 1;
				y = unknown_int();
			} else {
			    y = y - 1;
			}
		} else {
		    if (unknown_int() != 0) {
			    x = x + 1;
			} else {
			    y = y - 1;
				x = unknown_int();
			}		
		}
	}
    return 0;
}