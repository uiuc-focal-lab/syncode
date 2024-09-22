// Source: data/benchmarks/diffy_cav21_bench/sanfoundry_27_ground.c
#include <stdlib.h>
#define assume(e) if(!(e)) exit(-1);
extern int unknown_int(void);

int SIZE;
int main()
{
	SIZE = unknown_int();
	if(SIZE <= 0) return 1;
	int i;
	int largest[1];
	int array[SIZE];

	/* Loop_A */  for(i = 0; i < SIZE; i++) 
	{
		array[i] = unknown_int();
	}

	/* Loop_B */  for (i = 0; i < SIZE; i++)
	{
		if(i == 0) {
			largest[0] = array[0];
		} else {
			if (largest[0] < array[i])
				largest[0] = array[i];
		}
	}

	int x;
	/* Loop_C */  for ( x = 0 ; x < SIZE ; x++ ) {
		{;
//@ assert(  largest[0] >= array[ x ]  );
}

	}

	return 0;
}