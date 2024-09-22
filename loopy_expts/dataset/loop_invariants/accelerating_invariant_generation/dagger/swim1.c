// Source: data/benchmarks/accelerating_invariant_generation/dagger/swim1.c
#include <stdlib.h>
#define assume(e) if(!(e)) exit(-1);
extern int unknown_int(void);

int nondet_int();

int main()
{
	int x1;
	int x2;
	int x3;
	int x4;
	int x5;
	int x6;
	int x7;
	int p;
	int q;

	x1=0;
	x2=0;
	x3=0;
	x4=0;
	x5=0;
	if (! (x6==p)) 
return 0;

	if (! (x7==q)) 
return 0;
 
	if (! (p >=1)) 
return 0;

	if (! (q >=1)) 
return 0;

	while (unknown_int())
	{
		if (unknown_int())
		{
			if (! (x6 >=1)) 
return 0;

			x1 = x1 + 1;
			x6 = x6 - 1;
		}
		else
		{
			if (unknown_int())
			{
				if (! (x1 >=1)) 
return 0;

				if (! (x7 >=1)) 
return 0;

				x1 = x1-1;
				x2 = x2+1;
				x7 = x7-1;
			}
			else
			{
				if (unknown_int())
				{
					if (! (x2 >=1)) 
return 0;

					x2 = x2-1;
					x3 = x3+1;
					x6 = x6+1;
				}
				else
				{
					if (unknown_int())
					{
						if (! (x3>=1)) 
return 0;

						if (! (x6>=1)) 
return 0;

						x3 = x3-1;
						x4 = x4+1;
						x6 = x6-1;
					}
					else
					{
						if (unknown_int())
						{
							if (! (x4>=1)) 
return 0;

							x4 = x4-1;
							x5 = x5+1;
							x7 = x7+1;
						}
						else
						{
							if (! (x5>=1)) 
return 0;

							x5 = x5-1;
							x6 = x6+1;
						}
					}
				}
			}
		}
	}
	{;
//@ assert(x2 + x3 + x4 + x7 == q);
}

	{;
//@ assert(x2 + x3 + x4 + x7 >= q);
}

	{;
//@ assert(x1 + x2 + x4 + x5 + x6 >= p);
}

	{;
//@ assert(x1 + x2 + x4 + x5 + x6 <= p);
}

	{;
//@ assert(x7  >= 0);
}

	{;
//@ assert(x6  >= 0);
}

	{;
//@ assert(x5  >= 0);
}

	{;
//@ assert(x4  >= 0);
}

	{;
//@ assert(x3  >= 0);
}

	{;
//@ assert(x2  >= 0);
}

	{;
//@ assert(x1  >= 0);
}

	{;
//@ assert(x2 + x3 + x4 + x7 >= 1);
}

	{;
//@ assert(x1 + x2 + x4 + x5 + x6 >= 1);
}

	{;
//@ assert(x1 + x2 + x4 + x6 + x7 >= 1);
}

}
