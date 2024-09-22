// Source: data/benchmarks/sv-benchmarks/loops-crafted-1/sumt2.c
#include <stdlib.h>
#define assume(e) if(!(e)) exit(-1);
extern unsigned int unknown_uint(void);

int SIZE = 20000001;

int main() {
  unsigned int n,i,j,l=0;
  n = unknown_uint();
  if (!(n <= SIZE)) return 0;
  i = 0;
  j = 0;
  l=0;
  while( l < n ) {
	
	  if(!(l%2))
	    i = i + 1;
	  else 
		  j = j+1;
    l = l+1;
  }
  {;
//@ assert((i+j) == l);
}

  return 0;
}
