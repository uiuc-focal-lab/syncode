// Source: data/benchmarks/LinearArbitrary-SeaHorn/pie/hola/23.c
#include <stdlib.h>
#define assume(e) if(!(e)) exit(-1);

extern int unknown1();

int main(){
   int i, sum=0;
   int n = unknown1();
   if( n >= 0){

   for (i=0; i < n; ++i)
      sum = sum +i;

   {;
//@ assert(sum >= 0);
}

   }
}
