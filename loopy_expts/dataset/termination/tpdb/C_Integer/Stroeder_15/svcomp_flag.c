// Source: data/benchmarks/tpdb/C_Integer/Stroeder_15/svcomp_flag.c
#include <stdlib.h>
#define assume(e) if(!(e)) exit(-1);
extern int unknown_int(void);

typedef enum {false, true} bool;

int main() {
    int flag;
    int c, x, y;
    flag = 1;
    c = 0;
    x = unknown_int();
    y = unknown_int();
    while (flag != 0) {
        if (x >= y) {
            flag = 0;
        }
        x = x + 1;
        c = c + 1;
    }
    return 0;
}