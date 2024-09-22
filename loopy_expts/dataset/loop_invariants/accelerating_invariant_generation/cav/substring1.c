// Source: data/benchmarks/accelerating_invariant_generation/cav/substring1.c
#include <stdlib.h>
#define assume(e) if(!(e)) exit(-1);

void main () {
int i, j;
int from;
int to;
int k;

if (!(k >= 0)) 
return;

if (!(k <= 100)) 
return;

if (!(from >= 0)) 
return;

if (!(from <= k)) 
return;

i = from;
j = 0;

while (i < k) {
i++;
j++;
}

if (j >= 101)
  goto ERROR;

return;

{ ERROR: {; 
//@ assert(\false);
}
}

}
