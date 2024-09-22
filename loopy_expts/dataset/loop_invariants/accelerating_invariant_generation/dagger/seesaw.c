// Source: data/benchmarks/accelerating_invariant_generation/dagger/seesaw.c
#include <stdlib.h>
#define assume(e) if(!(e)) exit(-1);
extern int unknown_int(void);

int nondet_int();

int main()
{
	int x;
	int y;

	if (! (x==0)) 
return 0;

	if (! (y==0)) 
return 0;

	while (unknown_int())
	{
		if (unknown_int())
		{
			if (! (x >= 9)) 
return 0;

			x = x + 2;
			y = y + 1;
		}
		else
		{
			if (unknown_int())
			{
				if (!(x >= 7)) 
return 0;

				if (!(x <= 9)) 
return 0;

				x = x + 1;
				y = y + 3;
			}
			else
			{
				if (unknown_int())
				{
					if (! (x - 5 >=0)) 
return 0;

					if (! (x - 7 <=0)) 
return 0;

					x = x + 2;
					y = y + 1;
				}
				else
				{
					if (!(x - 4 <=0)) 
return 0;

					x = x + 1;
					y = y + 2;
				}
			}
		}
	}
	{;
//@ assert(-x + 2*y  >= 0);
}

	{;
//@ assert(3*x - y  >= 0);
}

}
