// Source: data/benchmarks/tpdb/C/SV-COMP_Termination_Category/Toulouse-MultiBranchesToLoop_true-termination.c
#include <stdlib.h>
#define assume(e) if(!(e)) exit(-1);
extern int unknown_int(void);

int main() {
	int y = unknown_int();
	int z = unknown_int();
    int x;
    if (unknown_int()) {
        x = 1;
    } else {
        x = -1;
    }
    if (x > 0) {
        x++;
    } else {
        x--;
    }
    if (x > 0) {
        x++;
    } else {
        x--;
    }
    if (x > 0) {
        x++;
    } else {
        x--;
    }
    if (x > 0) {
        x++;
    } else {
        x--;
    }
    if (x > 0) {
        x++;
    } else {
        x--;
    }
    if (x > 0) {
        x++;
    } else {
        x--;
    }
    if (x > 0) {
        x++;
    } else {
        x--;
    }
    if (x > 0) {
        x++;
    } else {
        x--;
    }
    while (y<100 && z<100) {
        y = y+x;
        z = z-x;
    }
    return 0;
}