// Source: data/benchmarks/tpdb/C_Integer/Stroeder_15/PastaC7.c
#include <stdlib.h>
#define assume(e) if(!(e)) exit(-1);
extern int unknown_int(void);

typedef enum {false,true} bool;

int main() {
    int i;
    int j;
    int k;
    int t;
    i = unknown_int();
    j = unknown_int();
    k = unknown_int();
    
    while (i <= 100 && j <= k) {
        i = j;
        j = i + 1;
        k = k - 1;
    }
    
    return 0;
}