// Source: data/benchmarks/LinearArbitrary-SeaHorn/pie/hola/41.c
#include <stdlib.h>
#define assume(e) if(!(e)) exit(-1);

extern int unknown1();

int main() {
   int n = unknown1();
   int flag = unknown1();

   if(n>=0){
   int k = 1;
   if(flag) {
	k = unknown1();
	if(k>=0) ; else return 0;
   }
   int i = 0, j = 0;
   while(i <= n) {
     i++;
     j+=i;
   }
   int z = k + i + j;
   {;
//@ assert(z > 2*n);
}

   }
   return 0;
}
