// Source: data/benchmarks/tpdb/C_Integer/Stroeder_15/BradleyMannaSipma-CAV2005-Fig1_true-termination.c
#include <stdlib.h>
#define assume(e) if(!(e)) exit(-1);
extern int unknown_int(void);

typedef enum {false, true} bool;

int main() {
    int y1, y2;
	y1 = unknown_int();
	y2 = unknown_int();
	if (y1 > 0 && y2 > 0) {
    	while (y1 != y2) {
	    	if (y1 > y2) {
		    	y1 = y1 - y2;
    		} else {
	    		y2 = y2 - y1;
		    }
	    }
	}
	return 0;
}