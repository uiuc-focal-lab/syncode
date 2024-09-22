// Source: data/benchmarks/tpdb/C/SV-COMP_Termination_Category/ChenFlurMukhopadhyay-SAS2012-Ex1.02_true-termination.c
#include <stdlib.h>
#define assume(e) if(!(e)) exit(-1);
extern int unknown_int(void);

int main() {
    int x = unknown_int();
    while (x > 0 && x < 100) {
        int old_x = x;
        x = unknown_int();
        if (x < 2*old_x + 10) {
            break;
        }
    }
    return 0;
}