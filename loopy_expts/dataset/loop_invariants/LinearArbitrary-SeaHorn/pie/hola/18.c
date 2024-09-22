// Source: data/benchmarks/LinearArbitrary-SeaHorn/pie/hola/18.c
#include <stdlib.h>
#define assume(e) if(!(e)) exit(-1);

extern int unknown1();
extern int unknown2();
extern int unknown3();

int main() {
   int flag = unknown1();
   int a = unknown2();
   int b = unknown3();
   int j = 0;

   for (b=0; b < 100 ; ++b){
      if (flag)
         j = j +1;
   }

   if(flag)
      {;
//@ assert(j==100);
}

}