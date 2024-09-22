// Source: data/benchmarks/sv-benchmarks/loop-crafted/simple_vardep_2.c
#include <stdlib.h>
#define assume(e) if(!(e)) exit(-1);

int main()
{
  unsigned int i = 0;
  unsigned int j = 0;
  unsigned int k = 0;

  while (k < 0x0fffffff) {
    i = i + 1;
    j = j + 2;
    k = k + 3;
    {;
//@ assert((k == 3*i) && (j == 2*i));
}

  }

}