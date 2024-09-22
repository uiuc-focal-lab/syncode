// Source: data/benchmarks/tpdb/C/SV-COMP_Termination_Category/ChenFlurMukhopadhyay-SAS2012-Ex1.04_true-termination.c
#include <stdlib.h>
#define assume(e) if(!(e)) exit(-1);
extern int unknown_int(void);

int main() {
    int x = unknown_int();
    while (x > 1) {
        int old_x = x;
        x = unknown_int();
        if (2*x > old_x) {
            break;
        }
    }
    return 0;
}