// Source: data/benchmarks/sv-benchmarks/loops-crafted-1/sumt4.c
#include <stdlib.h>
#define assume(e) if(!(e)) exit(-1);
extern unsigned int unknown_uint(void);

int SIZE = 20000001;

int main() {
  unsigned int n=0,i=0,k=0,j=0,l=0;
  unsigned int v4=0;
  n = unknown_uint();
  if (!(n <= SIZE)) return 0;
  while( l < n ) {
	
	  if(!(l%4))
	    v4 = v4 + 1;
	  else if(!(l%3))
	    i = i + 1;
	  else if(!(l%2)) 
		  j = j+1;
	  else 
	    k = k+1;
    l = l+1;
  }
  {;
//@ assert((i+j+k+v4) == l);
}

  return 0;
}
