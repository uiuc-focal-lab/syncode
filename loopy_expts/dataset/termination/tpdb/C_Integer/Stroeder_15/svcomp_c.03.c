// Source: data/benchmarks/tpdb/C_Integer/Stroeder_15/svcomp_c.03.c
#include <stdlib.h>
#define assume(e) if(!(e)) exit(-1);
extern int unknown_int(void);

typedef enum {false, true} bool;

int main() {
    int c, x, y, z;
    x = unknown_int();
    y = unknown_int();
    z = unknown_int();
    c = 0;
    while (x < y) {
        if (x < z) {
            x = x + 1;
        } else {
            z = z + 1;
        }
        c = c + 1;
    }
    return 0;
}
