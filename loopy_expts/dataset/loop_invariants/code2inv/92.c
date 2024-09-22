// Source: data/benchmarks/code2inv/92.c
#include <stdlib.h>
#define assume(e) if(!(e)) exit(-1);

int main(){
    int z1,z2,z3;

    int x = 0;
    int y = 0;

    while(y >= 0){
        y = y + x;
    }

    {;
//@ assert( y>= 0);
}

}