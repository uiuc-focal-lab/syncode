// Source: data/benchmarks/tpdb/C_Integer/Stroeder_15/ChenFlurMukhopadhyay-SAS2012-Ex2.22_true-termination.c
#include <stdlib.h>
#define assume(e) if(!(e)) exit(-1);
extern int unknown_int(void);

typedef enum {false, true} bool;

int main() {
    int x, y, oldy;
    x = unknown_int();
    y = unknown_int();
    while (x > 0 && y <= -oldy) {
        x = y;
        oldy = y;
        y = unknown_int();
    }
    return 0;
}