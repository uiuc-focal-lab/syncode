// Source: data/benchmarks/sv-benchmarks/loop-floats-scientific-comp/loop3.c
#include <stdlib.h>
#define assume(e) if(!(e)) exit(-1);
extern int unknown_int(void);

float pi = 3.14159 ;

int main()
{
	float x = unknown_float() ;
	float octant1 = 0 ;
	float octant2 = pi/8 ;
	assume(x > octant1 && x < octant2) ;
	float oddExp = x ;
	float evenExp = 1.0 ;
	float term = x ;
	unsigned int count = 2 ;
	int multFactor = 0 ;
	int temp ;

	while(1)
	{
		term = term * (x/count) ;
		multFactor = (count>>1 % 2 == 0) ? 1 : -1 ;

		evenExp = evenExp + multFactor*term ;

		count++ ;

		term = term * (x/count) ;		
		
		oddExp = oddExp + multFactor*term ;
		
		count++ ;

		temp = unknown_int() ;
		if(temp == 0) break ;
	}

	{;
//@ assert( evenExp >= oddExp );
}

	return 0 ;
}	