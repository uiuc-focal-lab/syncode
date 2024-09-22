// Source: data/benchmarks/tpdb/C_Integer/Stroeder_15/svcomp_a.09_assume.c
#include <stdlib.h>
#define assume(e) if(!(e)) exit(-1);
extern int unknown_int(void);

typedef enum {false, true} bool;

int main() {
    int x, y, z;
    x = unknown_int();
    y = unknown_int();
    z = unknown_int();
    while (y > 0 && x >= z) {
        z = z + y;
    }
    return 0;
}