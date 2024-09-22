// Source: data/benchmarks/tpdb/C_Integer/Stroeder_15/DoubleNeg.c
#include <stdlib.h>
#define assume(e) if(!(e)) exit(-1);
extern int unknown_int(void);

typedef enum {false,true} bool;

int main() {
    int i;
    int j;
    i = unknown_int();
    j = unknown_int();
    
    while (i*j > 0) {
        i = i - 1;
        j = j - 1;
    }
    
    return 0;
}