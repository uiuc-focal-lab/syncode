// Source: data/benchmarks/sv-benchmarks/loops/terminator_03-2.c
#include <stdlib.h>
#define assume(e) if(!(e)) exit(-1);
extern int unknown_int(void);

#include <assert.h>

#define LIMIT 1000000

int main() {
    int x=unknown_int();
    int y=unknown_int();
    if (!(y <= LIMIT)) return 0;

    if (y>0) {
        while(x<100) {
            x=x+y;
        }
    }

    {;
//@ assert(y<=0 || (y>0 && x>=100));
}

    return 0;
}
