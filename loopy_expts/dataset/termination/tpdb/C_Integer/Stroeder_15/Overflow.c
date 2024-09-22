// Source: data/benchmarks/tpdb/C_Integer/Stroeder_15/Overflow.c
#include <stdlib.h>
#define assume(e) if(!(e)) exit(-1);
extern int unknown_int(void);

typedef enum {false,true} bool;

int main() {
    int i;
    i = unknown_int();
    
    while(i <= 2147483647) {
        i = i+1;
    }
    
    return 0;
}