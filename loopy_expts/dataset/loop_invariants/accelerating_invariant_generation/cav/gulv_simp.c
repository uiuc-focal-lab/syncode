// Source: data/benchmarks/accelerating_invariant_generation/cav/gulv_simp.c
#include <stdlib.h>
#define assume(e) if(!(e)) exit(-1);
extern int unknown_int(void);

int nondet(){
  int x;
  return x;
}

int main(){
int x = 0, y = 0;
while (unknown_int()) {
   if (unknown_int())
     {x = x+1; y = y+100;}
   else if (unknown_int()){
     if (x >= 4)
       {x = x+1; y = y+1;}
   }
 
   x = x; 
}
if (x >= 4 && y <= 2)
  goto ERROR;

return 0;

{ ERROR: {; 
//@ assert(\false);
}
}
}