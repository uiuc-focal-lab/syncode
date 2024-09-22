// Source: data/benchmarks/tpdb/C_Integer/Stroeder_15/ChenFlurMukhopadhyay-SAS2012-Ex2.07_true-termination.c
#include <stdlib.h>
#define assume(e) if(!(e)) exit(-1);
extern int unknown_int(void);

typedef enum {false, true} bool;

int main() {
    int x, y;
    x = unknown_int();
    y = unknown_int();
    while (x > 0 && x < y) {
        x = 2*x;
        y = y + 1;
    }
    return 0;
}