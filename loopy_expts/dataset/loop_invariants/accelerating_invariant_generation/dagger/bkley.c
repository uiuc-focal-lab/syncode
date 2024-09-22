// Source: data/benchmarks/accelerating_invariant_generation/dagger/bkley.c
#include <stdlib.h>
#define assume(e) if(!(e)) exit(-1);
extern int unknown_int(void);

int nondet_int();

int main()
{

	int invalid;
	int unowned;
	int nonexclusive;
	int exclusive;

	if (! (exclusive==0)) 
return 0;

	if (! (nonexclusive==0)) 
return 0;

	if (! (unowned==0)) 
return 0;

	if (! (invalid>= 1)) 
return 0;

	while (unknown_int())
	{
		if (unknown_int())
		{
			if (! (invalid >= 1)) 
return 0;

			nonexclusive=nonexclusive+exclusive;
			exclusive=0;
			invalid=invalid-1;
			unowned=unowned+1;
		}
		else
		{
			if (unknown_int())
			{
				if (! (nonexclusive + unowned >=1)) 
return 0;

				invalid=invalid + unowned + nonexclusive-1;
				exclusive=exclusive+1;
				unowned=0;
				nonexclusive=0;
			}
			else
			{
				if (! (invalid >= 1)) 
return 0;

				unowned=0;
				nonexclusive=0;
				exclusive=1;
				invalid=invalid+unowned+exclusive+nonexclusive-1;
			}
		}
	}

	{;
//@ assert(exclusive >= 0);
}

	{;
//@ assert(unowned >= 0);
}

	{;
//@ assert(invalid + unowned + exclusive + nonexclusive >= 1);
}

}
