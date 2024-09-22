// Source: data/benchmarks/tpdb/C/SV-COMP_Termination_Category/ChenFlurMukhopadhyay-SAS2012-Ex2.07_true-termination.c
#include <stdlib.h>
#define assume(e) if(!(e)) exit(-1);
extern int unknown_int(void);

int main() {
    int x = unknown_int();
    int y = unknown_int();
    while (x > 0 && x < y) {
        x = 2*x;
        y++;
    }
    return 0;
}