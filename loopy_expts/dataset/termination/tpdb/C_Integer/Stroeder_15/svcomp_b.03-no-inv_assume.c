// Source: data/benchmarks/tpdb/C_Integer/Stroeder_15/svcomp_b.03-no-inv_assume.c
#include <stdlib.h>
#define assume(e) if(!(e)) exit(-1);
extern int unknown_int(void);

typedef enum {false, true} bool;

int main() {
    int x, y;
    x = unknown_int();
    y = unknown_int();
    if (x > 0) {
        while (x > y) {
            y = y + x;
        }
    }
    return 0;
}