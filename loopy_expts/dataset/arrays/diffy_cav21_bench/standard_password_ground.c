// Source: data/benchmarks/diffy_cav21_bench/standard_password_ground.c
#include <stdlib.h>
#define assume(e) if(!(e)) exit(-1);
extern int unknown_int(void);

/*@
	requires SIZE > 0;
	requires \separated(password+(0..SIZE-1), guess+(0..SIZE-1));
*/
int main(int* password, int* guess, int SIZE)
{
	int i;
	int result[1];
	result[0] = 1;	

	/* Loop_A */  for (i = 0; i < SIZE; i++)
	{
		password[i] = unknown_int();
		guess[i] = unknown_int();
	}

	/* Loop_B */  for ( i = 0 ; i < SIZE ; i++ ) {
		if ( password[ i ] != guess[ i ] ) {
			result[0] = 0;
		}
	}

	int x;
	/* Loop_C */  for ( x = 0 ; x < SIZE ; x++ ) {
		{;
//@ assert( result[0] == 0 ||  password[ x ] == guess[ x ]  );
}

	}
	return 0;
}