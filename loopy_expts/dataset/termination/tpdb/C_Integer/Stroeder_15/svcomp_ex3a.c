// Source: data/benchmarks/tpdb/C_Integer/Stroeder_15/svcomp_ex3a.c
#include <stdlib.h>
#define assume(e) if(!(e)) exit(-1);
extern int unknown_int(void);

typedef enum {false, true} bool;

int main() {
    int c, x;
    x = unknown_int();
    c = 0;
    while ((x > 1) && (x < 100)) {
        x = x*x;
        c = c + 1;
    }
    return 0;
}