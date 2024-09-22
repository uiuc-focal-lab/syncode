// Source: data/benchmarks/tpdb/C_Integer/Stroeder_15/genady_true-termination.c
#include <stdlib.h>
#define assume(e) if(!(e)) exit(-1);

typedef enum {false, true} bool;

int main() {
    int i, j;
    j = 1;
    i = 10000;
    while (i-j >= 1) {
        j = j + 1;
        i = i - 1;
    }  
    return 0;
}