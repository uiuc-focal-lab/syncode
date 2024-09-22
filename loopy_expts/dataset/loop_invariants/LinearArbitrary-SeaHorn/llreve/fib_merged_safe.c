// Source: data/benchmarks/LinearArbitrary-SeaHorn/llreve/fib_merged_safe.c
#include <stdlib.h>
#define assume(e) if(!(e)) exit(-1);
extern int unknown(void);

void main() {
	int n = unknown();
  int f1 = 0;   
  int f2 = 1;  
  int g1 = 1, g2 = 1;
  int h1 = 0, h2 = 0;

  while((n > 0)) {
    h1 = f1 + g1;
    f1 = g1;
    g1 = h1;
    n --;

    h2 = f2 + g2;
    f2 = g2;
    g2 = h2;

	{;
//@ assert(h2==h1+f1);
}

  }
}