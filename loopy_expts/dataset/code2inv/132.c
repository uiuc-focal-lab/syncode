// Source: data/benchmarks/code2inv/132.c
#include <stdlib.h>
#define assume(e) if(!(e)) exit(-1);
extern int unknown(void);

int main() {
    int i = 0;
    int j, c, t;

    while( unknown() ) {
        if(c > 48) {
            if (c < 57) {
                j = i + i;
                t = c - 48;
                i = j + t;
            }
        }
    } 
    {;
//@ assert(i >= 0);
}

}