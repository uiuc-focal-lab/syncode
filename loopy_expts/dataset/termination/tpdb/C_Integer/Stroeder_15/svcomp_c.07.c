// Source: data/benchmarks/tpdb/C_Integer/Stroeder_15/svcomp_c.07.c
#include <stdlib.h>
#define assume(e) if(!(e)) exit(-1);
extern int unknown_int(void);

typedef enum {false, true} bool;

int main() {
    int c, i, j, k, tmp;
    i = unknown_int();
    j = unknown_int();
    k = unknown_int();
    tmp = unknown_int();
    c = 0;
    while ((i <= 100) && (j <= k)) {
        tmp = i;
        i = j;
        j = tmp + 1;
        k = k - 1;
        c = c + 1;
    }
    return 0;
}