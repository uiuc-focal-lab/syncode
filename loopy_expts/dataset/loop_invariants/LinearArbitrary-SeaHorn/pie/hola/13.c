// Source: data/benchmarks/LinearArbitrary-SeaHorn/pie/hola/13.c
#include <stdlib.h>
#define assume(e) if(!(e)) exit(-1);

extern int unknown1();
extern int unknown2();
extern int unknown3();
extern int unknown4();

int main() {
   int j = 2; 
   int k = 0;

   int flag = unknown2();

   while(unknown1()){ 
     if (flag)
       j = j + 4;
     else {
       j = j + 2;
       k = k + 1;
     }
   }
   if(k!=0)
     {;
//@ assert(j==2*k+2);
}

   return 0;
}