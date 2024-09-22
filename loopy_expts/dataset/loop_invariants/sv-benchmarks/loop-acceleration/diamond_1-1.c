// Source: data/benchmarks/sv-benchmarks/loop-acceleration/diamond_1-1.c
#include <stdlib.h>
#define assume(e) if(!(e)) exit(-1);
extern unsigned int unknown_uint(void);

int main(void) {
  unsigned int x = 0;
  unsigned int y = unknown_uint();

  while (x < 99) {
    if (y % 2 == 0) {
      x += 2;
    } else {
      x++;
    }
  }

  {;
//@ assert((x % 2) == (y % 2));
}

}