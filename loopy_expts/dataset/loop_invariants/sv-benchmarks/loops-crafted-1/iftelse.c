// Source: data/benchmarks/sv-benchmarks/loops-crafted-1/iftelse.c
#include <stdlib.h>
#define assume(e) if(!(e)) exit(-1);
extern unsigned int unknown_uint(void);

int SIZE = 20000001;

int main() {
  unsigned int n,i,k,j;
  n = unknown_uint();
  if (!(n <= SIZE)) return 0;
  i = j = k = 0;
  while( i < n ) {
    i = i + 3;
    if(i%2)
	    j = j+3;
    else
	    k = k+3;
    if(n>0)
	  {;
//@ assert( (i/2<=j) );
}

  }
  return 0;
}
