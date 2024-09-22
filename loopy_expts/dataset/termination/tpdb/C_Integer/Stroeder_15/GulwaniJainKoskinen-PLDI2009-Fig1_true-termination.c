// Source: data/benchmarks/tpdb/C_Integer/Stroeder_15/GulwaniJainKoskinen-PLDI2009-Fig1_true-termination.c
#include <stdlib.h>
#define assume(e) if(!(e)) exit(-1);
extern int unknown_int(void);

typedef enum {false, true} bool;

int main() {
    int id, maxId, tmp;
    id = unknown_int();
    maxId = unknown_int();

    if(0 <= id && id < maxId) {
        tmp = id+1;
        while(tmp!=id && unknown_int() != 0) {
            if (tmp <= maxId) {
                tmp = tmp + 1;
            } else {
                tmp = 0;
            }
        }
    }

    return 0;
}