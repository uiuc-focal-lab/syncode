// Source: data/benchmarks/sv-benchmarks/loop-acceleration/multivar_1-1.c
#include <stdlib.h>
#define assume(e) if(!(e)) exit(-1);
extern unsigned int unknown_uint(void);

int main(void) {
  unsigned int x = unknown_uint();
  unsigned int y = x;

  while (x < 1024) {
    x++;
    y++;
  }

  {;
//@ assert(x == y);
}

}