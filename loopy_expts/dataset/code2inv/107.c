// Source: data/benchmarks/code2inv/107.c
#include <stdlib.h>
#define assume(e) if(!(e)) exit(-1);

int main() {
    int a,m,j,k;

    j = 0;
    k = 0;

    while ( k < 1) {
        if(m < a) {
            m = a;
        }
        k = k + 1;
    }

    {;
//@ assert( a <= m);
}

}