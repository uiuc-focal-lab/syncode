// Source: data/benchmarks/code2inv/38.c
#include <stdlib.h>
#define assume(e) if(!(e)) exit(-1);
extern int unknown(void);

int main() {
    int n;
    int c = 0;
    assume (n > 0);

    while (unknown()) {
        if(c == n) {
            c = 1;
        }
        else {
            c = c + 1;
        }
    }

    if(c == n) {
        {;
//@ assert( c >= 0);
}

    }
}