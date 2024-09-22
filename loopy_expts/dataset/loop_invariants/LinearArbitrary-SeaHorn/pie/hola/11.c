// Source: data/benchmarks/LinearArbitrary-SeaHorn/pie/hola/11.c
#include <stdlib.h>
#define assume(e) if(!(e)) exit(-1);

void main()
{
  int j=0;
  int i;
  int x=100;
   
  for (i =0; i< x ; i++){
    j = j + 2;
  }

  {;
//@ assert(j == 2*x);
}

}
