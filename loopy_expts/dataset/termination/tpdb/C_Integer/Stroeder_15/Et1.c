// Source: data/benchmarks/tpdb/C_Integer/Stroeder_15/Et1.c
#include <stdlib.h>
#define assume(e) if(!(e)) exit(-1);
extern int unknown_int(void);

typedef enum {false,true} bool;

int main() {
    int a;
    int b;
    a = - unknown_int();
    b = - unknown_int();
    
    while (a > b) {
        b = b + a;
        a = a + 1;
    }
    
    return 0;
}