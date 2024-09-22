// Source: data/benchmarks/tpdb/C/SV-COMP_Termination_Category/ChenFlurMukhopadhyay-SAS2012-Ex2.22_true-termination.c
#include <stdlib.h>
#define assume(e) if(!(e)) exit(-1);
extern int unknown_int(void);

int main() {
    int x = unknown_int();
    int y = unknown_int();
    while (x > 0) {
        x = y;
        int old_y = y;
        y = unknown_int();
        if (y > -old_y) {
            break;
        }
    }
    return 0;
}