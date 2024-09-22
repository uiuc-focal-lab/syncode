// Source: data/benchmarks/tpdb/C_Integer/Stroeder_15/Toulouse-MultiBranchesToLoop_true-termination.c
#include <stdlib.h>
#define assume(e) if(!(e)) exit(-1);
extern int unknown_int(void);

typedef enum {false, true} bool;

int main() {
    int x;
	int y;
	int z;
	y = unknown_int();
	z = unknown_int();
    if (unknown_int() != 0) {
        x = 1;
    } else {
        x = -1;
    }
    if (x > 0) {
        x = x + 1;
    } else {
        x = x - 1;
    }
    if (x > 0) {
        x = x + 1;
    } else {
        x = x - 1;
    }
    if (x > 0) {
        x = x + 1;
    } else {
        x = x - 1;
    }
    if (x > 0) {
        x = x + 1;
    } else {
        x = x - 1;
    }
    if (x > 0) {
        x = x + 1;
    } else {
        x = x - 1;
    }
    if (x > 0) {
        x = x + 1;
    } else {
        x = x - 1;
    }
    if (x > 0) {
        x = x + 1;
    } else {
        x = x - 1;
    }
    if (x > 0) {
        x = x + 1;
    } else {
        x = x - 1;
    }
    while (y<100 && z<100) {
        y = y+x;
        z = z-x;
    }
    return 0;
}