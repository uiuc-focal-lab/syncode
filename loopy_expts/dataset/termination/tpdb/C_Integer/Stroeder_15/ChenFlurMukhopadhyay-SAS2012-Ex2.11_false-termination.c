// Source: data/benchmarks/tpdb/C_Integer/Stroeder_15/ChenFlurMukhopadhyay-SAS2012-Ex2.11_false-termination.c
#include <stdlib.h>
#define assume(e) if(!(e)) exit(-1);
extern int unknown_int(void);

typedef enum {false, true} bool;

int main() {
    int x, y, oldx;
    x = unknown_int();
    y = unknown_int();
    while (4*x - 5*y > 0) {
        oldx = x;
        x = 2*oldx + 4*y;
        y = 4*oldx;
    }
    return 0;
}