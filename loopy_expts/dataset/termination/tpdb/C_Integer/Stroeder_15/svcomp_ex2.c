// Source: data/benchmarks/tpdb/C_Integer/Stroeder_15/svcomp_ex2.c
#include <stdlib.h>
#define assume(e) if(!(e)) exit(-1);
extern int unknown_int(void);

typedef enum {false, true} bool;

int main() {
    int c, flag, x, y, z;
    c = 0;
    flag = 1;
    x = unknown_int();
    y = unknown_int();
    z = unknown_int();
    while ((y < z) && (flag > 0)) {
        if ((y > 0) && (x > 1)) {
            y = x*y;
        } else {
            if ((y > 0) && (x < -1)) {
                y = -x*y;
            } else {
                flag = 0;
            }
        }
        c = c + 1;
    }
    return 0;
}