// Source: data/benchmarks/LinearArbitrary-SeaHorn/pie/ICE/benchmarks/ex14n.v.c
#include <stdlib.h>
#define assume(e) if(!(e)) exit(-1);
extern int unknown_int(void);

int main() {

    	int x,y,N, v1, v2, v3;
   	
   	x=1;
        N = unknown_int();
   	while (x <= N){
      		y=N-x;

		if(y < 0 || y >= N)
			{;
//@ assert(0 == 1);
}

      		x++;
		v1 = v2;
		v2 = v3;
		v3 = v1;
	
   	}

   	return 1;

}