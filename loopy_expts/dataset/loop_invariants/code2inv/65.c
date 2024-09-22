// Source: data/benchmarks/code2inv/65.c
#include <stdlib.h>
#define assume(e) if(!(e)) exit(-1);

int main() {
    int x = 1;
    int y;

    while (x <= 100) {
        y = 100 - x;
        x = x +1;
    }

    {;
//@ assert(y >= 0);
}

}