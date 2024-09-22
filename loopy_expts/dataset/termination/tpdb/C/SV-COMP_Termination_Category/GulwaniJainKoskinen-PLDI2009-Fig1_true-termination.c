// Source: data/benchmarks/tpdb/C/SV-COMP_Termination_Category/GulwaniJainKoskinen-PLDI2009-Fig1_true-termination.c
#include <stdlib.h>
#define assume(e) if(!(e)) exit(-1);
extern int unknown_int(void);

int main() {
    int id = unknown_int();
    int maxId = unknown_int();

    if(0 <= id && id < maxId) {
        int tmp = id+1;
        while(tmp!=id && unknown_int()) {
            if (tmp <= maxId) {
                tmp = tmp + 1;
            } else {
                tmp = 0;
            }
        }
    }

    return 0;
}
