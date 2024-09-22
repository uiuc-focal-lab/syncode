// Source: data/benchmarks/LinearArbitrary-SeaHorn/sharma_splitter/popl.c
#include <stdlib.h>
#define assume(e) if(!(e)) exit(-1);

int main(){
       int x, y;
       x=0;
       y=50;
       while(x<100) {
               x=x+1;
               if (x>50) {
                       y=y+1;
               }
       }
	{;
//@ assert(y==100);
}

	return 0;
}