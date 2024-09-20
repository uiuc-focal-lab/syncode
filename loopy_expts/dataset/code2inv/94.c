// Source: data/benchmarks/code2inv/94.c
#include <stdlib.h>
#define assume(e) if(!(e)) exit(-1);

int main() {
  
  int i;
  int j;
  int k;
  int n;
  
  assume((k >= 0));
  assume((n >= 0));
  (i = 0);
  (j = 0);
  
  while ((i <= n)) {
    {
    (i  = (i + 1));
    (j  = (j + i));
    }

  }
  
{;
//@ assert( ((i + (j + k)) > (2 * n)) );
}

}