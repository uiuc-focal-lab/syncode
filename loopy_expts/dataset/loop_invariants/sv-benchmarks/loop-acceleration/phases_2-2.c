// Source: data/benchmarks/sv-benchmarks/loop-acceleration/phases_2-2.c
#include <stdlib.h>
#define assume(e) if(!(e)) exit(-1);
extern unsigned int unknown_uint(void);

int main(void) {
  unsigned int x = 1;
  unsigned int y = unknown_uint();

  if (!(y > 0)) return 0;

  while (x < y) {
    if (x < y / x) {
      x *= x;
    } else {
      x++;
    }
  }

  {;
//@ assert(x == y);
}

}