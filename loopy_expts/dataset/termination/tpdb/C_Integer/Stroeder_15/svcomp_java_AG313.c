// Source: data/benchmarks/tpdb/C_Integer/Stroeder_15/svcomp_java_AG313.c
#include <stdlib.h>
#define assume(e) if(!(e)) exit(-1);
extern int unknown_int(void);

typedef enum {false, true} bool;

int main() {
    int i, x, y;
    i = 0;
    x = unknown_int();
    y = unknown_int();
    if (x!=0) {
        while (x > 0 && y > 0) {
            i = i + 1;
            x = (x - 1)- (y - 1);
        }
    }
    return 0;
}