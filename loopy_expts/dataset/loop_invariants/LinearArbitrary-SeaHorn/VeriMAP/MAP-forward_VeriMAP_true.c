// Source: data/benchmarks/LinearArbitrary-SeaHorn/VeriMAP/MAP-forward_VeriMAP_true.c
#include <stdlib.h>
#define assume(e) if(!(e)) exit(-1);
extern int unknown_int(void);

;

void main(){

   int i, n, a, b;
   n = unknown_int();
   assume( n>= 0 );

   i = 0; 
   a = 0; 
   b = 0;

   while( i < n ){
      if(unknown_int()) {
         a = a+1;
         b = b+2;
      } else {
         a = a+2;
         b = b+1;
      }
      i = i+1;
   }

   if ( a+b != 3*n)
      goto ERROR;

return;

{ ERROR: {; 
//@ assert(\false);
}
}
}