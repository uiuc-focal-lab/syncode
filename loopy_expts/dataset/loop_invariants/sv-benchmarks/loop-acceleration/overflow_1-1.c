// Source: data/benchmarks/sv-benchmarks/loop-acceleration/overflow_1-1.c
#include <stdlib.h>
#define assume(e) if(!(e)) exit(-1);

int main(void) {
  unsigned int x = 10;

  while (x >= 10) {
    x += 2;
  }

  {;
//@ assert(!(x % 2));
}

}