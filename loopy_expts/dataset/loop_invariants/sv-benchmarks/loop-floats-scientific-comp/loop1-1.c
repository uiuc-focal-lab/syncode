// Source: data/benchmarks/sv-benchmarks/loop-floats-scientific-comp/loop1-1.c
#include <stdlib.h>
#define assume(e) if(!(e)) exit(-1);
extern int unknown_int(void);

int main()
{
	float x = unknown_float() ;
	assume(x > -1.0) ;
	assume(x < 1.0) ;
	float exp = 1.0 ;
	float term = 1.0 ;
	unsigned int count = 1 ;
	float result = 2*(1/(1-x)) ;
	int temp ;

	while(1)
	{
		term = term * (x/count) ; 
		exp = exp + term ;
		count++ ;

		temp = unknown_int() ;
		if(temp ==0 ) break ;
	}

	{;
//@ assert( result >= exp );
}

	return 0 ;
}	