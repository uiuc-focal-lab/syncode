#include <stdlib.h>
#define assume(e) if(!(e)) exit(-1);
extern int unknown(void);

int main() {
  
  int x;
  int y;
  
  assume((x >= 0));
  assume((x <= 2));
  assume((y <= 2));
  assume((y >= 0));
  
  while (unknown()) {
    {
    (x  = (x + 2));
    (y  = (y + 2));
    }

  }
  
if ( (y == 0) )
{;
//@ assert( (x != 4) );
}

}