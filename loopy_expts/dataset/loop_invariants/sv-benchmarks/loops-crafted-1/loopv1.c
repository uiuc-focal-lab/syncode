// Source: data/benchmarks/sv-benchmarks/loops-crafted-1/loopv1.c
#include <stdlib.h>
#define assume(e) if(!(e)) exit(-1);
extern int unknown_int(void);

int SIZE = 50000001;

int main() {
  int n,i,j;
  n = unknown_int();
  if (!(n <= SIZE)) return 0;
  i = 0; j=0;
  while(i<n){ 
 
    if(unknown_int())	  
      i = i + 6; 
    else
     i = i + 3;    
  }
  {;
//@ assert( (i%3) == 0 );
}

  return 0;
}