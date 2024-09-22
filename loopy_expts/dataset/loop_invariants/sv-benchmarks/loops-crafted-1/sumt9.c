// Source: data/benchmarks/sv-benchmarks/loops-crafted-1/sumt9.c
#include <stdlib.h>
#define assume(e) if(!(e)) exit(-1);
extern int unknown_int(void);

int SIZE = 20000001;

int main() {
  unsigned int n=0,i=0,k=0,j=0,l=0;
  unsigned int v1=0, v2=0, v3=0, v4=0, v5=0, v6=0;
  n = unknown_int();
  if (!(n <= SIZE)) return 0;
  while( l < n ) {
	
	  if(!(l%9))
	    v6 = v6 + 1;
	  else if(!(l%8))
	    v5 = v5 + 1;
	  else if(!(l%7))
	    v1 = v1 + 1;
	  else if(!(l%6))
	    v2 = v2 + 1;
	  else if(!(l%5))
	    v3 = v3 + 1;
	  else if(!(l%4))
	    v4 = v4 + 1;
	  else if(!(l%3))
	    i = i + 1;
	  else if(!(l%2)) 
		  j = j+1;
	  else 
	    k = k+1;
    l = l+1;
    {;
//@ assert((i+j+k+v1+v2+v3+v4+v5+v6) == l);
}

  }
  return 0;
}
