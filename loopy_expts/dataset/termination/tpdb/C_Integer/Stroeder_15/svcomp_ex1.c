// Source: data/benchmarks/tpdb/C_Integer/Stroeder_15/svcomp_ex1.c
#include <stdlib.h>
#define assume(e) if(!(e)) exit(-1);
extern int unknown_int(void);

typedef enum {false, true} bool;

int main() {
    int x, y, r;
    x = unknown_int();
    y = unknown_int();
    r = 1;
    while (y > 0) {
        r = r*x;
        y = y - 1;
    }
    return 0;
}