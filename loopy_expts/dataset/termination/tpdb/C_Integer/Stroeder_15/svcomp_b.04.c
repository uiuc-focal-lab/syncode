// Source: data/benchmarks/tpdb/C_Integer/Stroeder_15/svcomp_b.04.c
#include <stdlib.h>
#define assume(e) if(!(e)) exit(-1);
extern int unknown_int(void);

typedef enum {false, true} bool;

int main() {
    int x, y, tmp;
    x = unknown_int();
    y = unknown_int();
    tmp = unknown_int();
    while (x > y) {
        tmp = x;
        x = y;
        y = tmp;
    }
    return 0;
}