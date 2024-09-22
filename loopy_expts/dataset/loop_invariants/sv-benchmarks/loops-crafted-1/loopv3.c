// Source: data/benchmarks/sv-benchmarks/loops-crafted-1/loopv3.c
#include <stdlib.h>
#define assume(e) if(!(e)) exit(-1);
extern int unknown_int(void);

int SIZE = 50000001;

int main() {
  int i,j;
  i = 0; j=0;
  while(i<SIZE){ 

    if(unknown_int())	  
      i = i + 8; 
    else
     i = i + 4;    
	  
  }
  j = i/4 ;
    {;
//@ assert( (j * 4) == i);
}

  return 0;
}