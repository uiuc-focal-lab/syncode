// Source: data/benchmarks/tpdb/C_Integer/Stroeder_15/Fibonacci.c
#include <stdlib.h>
#define assume(e) if(!(e)) exit(-1);
extern int unknown_int(void);

typedef enum {false,true} bool;

int main() {
    int n;
    int i;
    int j;
    int t;
    n = unknown_int();
    i = 0;
    j = 1;
    t = 0;
    
    while (j != n) {
        t = j+i;
        i = j;
        j = t;
    }
	
    return 0;
}