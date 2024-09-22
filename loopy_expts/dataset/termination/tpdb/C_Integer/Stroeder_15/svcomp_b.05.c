// Source: data/benchmarks/tpdb/C_Integer/Stroeder_15/svcomp_b.05.c
#include <stdlib.h>
#define assume(e) if(!(e)) exit(-1);
extern int unknown_int(void);

typedef enum {false, true} bool;

int main() {
    int x, tmp;
    x = unknown_int();
    tmp = unknown_int();
    while ((x > 0) && (x == 2*tmp)) {
        x = x - 1;
        tmp = unknown_int();
    }
    return 0;
}