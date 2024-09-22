// Source: data/benchmarks/tpdb/C/SV-COMP_Termination_Category/ChenFlurMukhopadhyay-SAS2012-Ex2.20_true-termination.c
#include <stdlib.h>
#define assume(e) if(!(e)) exit(-1);
extern int unknown_int(void);

int main() {
    int x = unknown_int();
    int y = unknown_int();
    while (x > y) {
        x = x - y;
        y = unknown_int();
        if (y < 1 || y > 2) {
            break;
        }
    }
    return 0;
}