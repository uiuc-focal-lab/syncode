// Source: data/benchmarks/tpdb/C/SV-COMP_Termination_Category/genady_true-termination.c
#include <stdlib.h>
#define assume(e) if(!(e)) exit(-1);

int main() {
   int j = 1;
   for (int i = 10000; i-j >= 1; i--) {
     j++;
   }  
}
