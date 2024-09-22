// Source: data/benchmarks/LinearArbitrary-SeaHorn/loops/loops/terminator_03_true-unreach-call_true-termination.i.annot.c
#include <stdlib.h>
#define assume(e) if(!(e)) exit(-1);
extern int unknown_int(void);

int main(){
    int  x=unknown_int();
    int  y=unknown_int();
assume(y <= 1000000);
    if(y>0){
        while(x<100){
            x=x+y;
        }
    }
    {;
//@ assert(y<=0 ||(y>0 && x>=100));
}

    return 0;
}