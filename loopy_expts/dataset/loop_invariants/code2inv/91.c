// Source: data/benchmarks/code2inv/91.c
#include <stdlib.h>
#define assume(e) if(!(e)) exit(-1);

int main(){

    int x = 0;
    int y = 0;

    while(y >= 0){
        y = y + x;
    }

    {;
//@ assert( y>= 0);
}

}