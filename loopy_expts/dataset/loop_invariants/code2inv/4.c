
#include <stdlib.h>
#define assume(e) if(!(e)) exit(-1);

int main()
{
    int x = 0;
    int y, z;

    while(x < 500) {
       x += 1;
       if( z <= y) {
          y = z;
       }
    }

    {;
//@ assert(z >= y);
}

}