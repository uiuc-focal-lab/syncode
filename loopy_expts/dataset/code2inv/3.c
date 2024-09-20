// Source: data/benchmarks/code2inv/3.c
#include <stdlib.h>
#define assume(e) if(!(e)) exit(-1);

int main()
{
    int x = 0;
    int y, z;

    while(x < 5) {
       x += 1;
       if( z <= y) {
          y = z;
       }
    }

    {;
//@ assert(z >= y);
}

}