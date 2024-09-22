// Source: data/benchmarks/tpdb/C_Integer/Stroeder_15/ChenFlurMukhopadhyay-SAS2012-Ex2.09_true-termination.c
#include <stdlib.h>
#define assume(e) if(!(e)) exit(-1);
extern int unknown_int(void);

typedef enum {false, true} bool;

int main() {
    int x, y, n;
    x = unknown_int();
    y = unknown_int();
    n = unknown_int();
    while (x > 0 && x < n) {
        x = -x + y - 5;
        y = 2*y;
    }
    return 0;
}