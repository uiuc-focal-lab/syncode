// Source: data/benchmarks/tpdb/C_Integer/Stroeder_15/svcomp_b.09_assume.c
#include <stdlib.h>
#define assume(e) if(!(e)) exit(-1);
extern int unknown_int(void);

typedef enum {false, true} bool;

int main() {
    int c;
    int x, y;
    x = unknown_int();
    y = unknown_int();
    c = 0;
    if (y > 0) {
        while (x > 0) {
            if (x > y) {
                x = y;
            } else {
                x = x - 1;
            }
            c = c + 1;
        }
    }
    return 0;
}