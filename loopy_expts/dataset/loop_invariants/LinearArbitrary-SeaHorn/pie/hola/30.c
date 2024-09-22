// Source: data/benchmarks/LinearArbitrary-SeaHorn/pie/hola/30.c
#include <stdlib.h>
#define assume(e) if(!(e)) exit(-1);

int main() {

  int i, c;
  i = 0;
  c = 0;
  while (i < 1000) {
    c = c + i;
    i = i + 1;
  }

  {;
//@ assert(c>=0);
}

}
