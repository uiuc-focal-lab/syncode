// Source: data/benchmarks/sv-benchmarks/loops-crafted-1/Mono1_1-2.c
#include <stdlib.h>
#define assume(e) if(!(e)) exit(-1);

int main(void) {
  unsigned int x = 0;

  while (x < 100000000) {
    if (x < 10000000) {
      x++;
    } else {
      x += 2;
    }
  }

  {;
//@ assert(x == 100000000);
}

}