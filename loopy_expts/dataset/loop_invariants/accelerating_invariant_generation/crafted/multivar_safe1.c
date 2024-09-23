#include <stdlib.h>
#define assume(e) if(!(e)) exit(-1);

int main(void) {
  unsigned int x;
  unsigned int y = x;

  while (x < 100) {
    x++;
    y++;
  }

  {;
//@ assert(x == y);
}

}