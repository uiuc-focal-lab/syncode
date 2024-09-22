// Source: data/benchmarks/code2inv/67.c
#include <stdlib.h>
#define assume(e) if(!(e)) exit(-1);

int main() {
    int n,y;
    int x = 1;

    while (x <= n) {
        y = n - x;
        x = x +1;
    }

    if (n > 0) {
        {;
//@ assert(y >= 0);
}

    }
}