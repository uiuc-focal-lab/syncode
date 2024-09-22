// Source: data/benchmarks/LinearArbitrary-SeaHorn/loops/loops/terminator_02_true-unreach-call_true-termination.i.annot.c
#include <stdlib.h>
#define assume(e) if(!(e)) exit(-1);
extern int unknown_int(void);
extern _Bool unknown_bool(void);

int main()
{
    int  x=unknown_int();
    int y=unknown_int();
    int  z=unknown_int();
assume(x<100);
assume(x>-100);
assume(z<100);
assume(z>-100);
    while(x<100 && 100<z)
    {
        int  tmp=unknown_bool();
        if(tmp){
            x++;
        } else {
            x--;
            z--;
        }
    }
    {;
//@ assert(x>=100 || z<=100);
}

    return 0;
}