// Source: data/benchmarks/tpdb/C_Integer/Stroeder_15/Factorial.c
#include <stdlib.h>
#define assume(e) if(!(e)) exit(-1);
extern int unknown_int(void);

typedef enum {false,true} bool;

int main() {
    int j;
    int i;
    int fac;
    j = unknown_int();
    i = 1;
    fac = 1;
    
    while (fac != j) {
        fac = fac * i;
        i = i+1;
    }
	
    return 0;
}