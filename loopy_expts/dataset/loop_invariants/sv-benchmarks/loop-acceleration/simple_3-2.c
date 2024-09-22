// Source: data/benchmarks/sv-benchmarks/loop-acceleration/simple_3-2.c
#include <stdlib.h>
#define assume(e) if(!(e)) exit(-1);
extern unsigned short unknown_ushort(void);

int main(void) {
  unsigned int x = 0;
  unsigned short N = unknown_ushort();

  while (x < N) {
    x += 2;
  }

  {;
//@ assert(!(x % 2));
}

}