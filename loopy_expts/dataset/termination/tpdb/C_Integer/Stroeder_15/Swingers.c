// Source: data/benchmarks/tpdb/C_Integer/Stroeder_15/Swingers.c
#include <stdlib.h>
#define assume(e) if(!(e)) exit(-1);

typedef enum {false,true} bool;

int main() {
    int bob;
    int samantha;
    int temp;
    bob = 13;
    samantha = 17;
    
    while (bob + samantha < 100) {
        temp = bob;
        bob = samantha;
        samantha = temp;
    }
    
    return 0;
}