// Source: data/benchmarks/accelerating_invariant_generation/crafted/simple_safe3.c
#include <stdlib.h>
#define assume(e) if(!(e)) exit(-1);

int main(void) {
  unsigned int x = 0;
  unsigned short N;

  while (x < N) {
    x += 2;
  }

  {;
//@ assert(!(x % 2));
}

}