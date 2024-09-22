// Source: data/benchmarks/sv-benchmarks/loop-acceleration/const_1-1.c
#include <stdlib.h>
#define assume(e) if(!(e)) exit(-1);

int main(void) {
  unsigned int x = 1;
  unsigned int y = 0;

  while (y < 1024) {
    x = 0;
    y++;
  }

  {;
//@ assert(x == 0);
}

}