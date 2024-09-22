// Source: data/benchmarks/sv-benchmarks/loop-acceleration/simple_2-1.c
#include <stdlib.h>
#define assume(e) if(!(e)) exit(-1);
extern unsigned int unknown_uint(void);

int main(void) {
  unsigned int x = unknown_uint();

  while (x < 0x0fffffff) {
    x++;
  }

  {;
//@ assert(x >= 0x0fffffff);
}

}