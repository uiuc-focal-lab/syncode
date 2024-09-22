// Source: data/benchmarks/tpdb/C_Integer/Stroeder_15/svcomp_ex3b.c
#include <stdlib.h>
#define assume(e) if(!(e)) exit(-1);
extern int unknown_int(void);

typedef enum {false, true} bool;

int main() {
    int c, x, y;
    x = unknown_int();
    y = unknown_int();
    c = 0;
    while ((x > 1) && (x < y)) {
        x = x*x;
        c = c + 1;
    }
    return 0;
}