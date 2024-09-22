// Source: data/benchmarks/tpdb/C/SV-COMP_Termination_Category/ChenFlurMukhopadhyay-SAS2012-Ex4.01_true-termination.c
#include <stdlib.h>
#define assume(e) if(!(e)) exit(-1);
extern int unknown_int(void);

int main() {
    int x = unknown_int();
    int y = unknown_int();
    int z = unknown_int();
    int n = unknown_int();
    while (x + y >= 0 && x <= n) {
        x = 2*x + y;
        y = z;
        z = z + 1;
    }
    return 0;
}