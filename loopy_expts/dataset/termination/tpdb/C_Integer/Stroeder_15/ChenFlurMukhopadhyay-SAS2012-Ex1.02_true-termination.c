// Source: data/benchmarks/tpdb/C_Integer/Stroeder_15/ChenFlurMukhopadhyay-SAS2012-Ex1.02_true-termination.c
#include <stdlib.h>
#define assume(e) if(!(e)) exit(-1);
extern int unknown_int(void);

typedef enum {false, true} bool;

int main() {
    int x, oldx;
    x = unknown_int();
    while (x > 0 && x < 100 && x >= 2*oldx + 10) {
        oldx = x;
        x = unknown_int();
    }
    return 0;
}