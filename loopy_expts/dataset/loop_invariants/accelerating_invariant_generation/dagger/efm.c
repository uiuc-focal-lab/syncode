// Source: data/benchmarks/accelerating_invariant_generation/dagger/efm.c
#include <stdlib.h>
#define assume(e) if(!(e)) exit(-1);
extern int unknown_int(void);

int nondet_int();

int main()
{
	int X1;
	int X2;
	int X3;
	int X4;
	int X5;
	int X6;

	if (! (X1>=1)) 
return 0;

	if (! (X2==0)) 
return 0;

	if (! (X3==0)) 
return 0;

	if (! (X4==1)) 
return 0;

	if (! (X5==0)) 
return 0;

	if (! (X6==0)) 
return 0;

	while(unknown_int())
	{
		if (unknown_int())
		{
			if (! (X1 >= 1)) 
return 0;

			if (! (X4 >= 1)) 
return 0;

			X1=X1-1;
			X4=X4-1;
			X2=X2+1;
			X5=X5+1;
		}
		else
		{
			if (unknown_int())
			{
				if (! (X2 >= 1)) 
return 0;

				if (! (X6 >= 1)) 
return 0;

				X2=X2-1;
				X3=X3+1;
			}
			else
			{
				if (unknown_int())
				{
					if (! (X4 >= 1)) 
return 0;

					if (! (X3 >= 1)) 
return 0;

					X3=X3-1;
					X2=X2+1;
				}
				else
				{
					if (unknown_int())
					{
						if (! (X3>=1)) 
return 0;

						X3=X3-1;
						X1=X1+1;
						X6=X6+X5;
						X5=0;
					}
					else
					{
						if (! (X2 >= 1)) 
return 0;

						X2 = X2 - 1;
						X1 = X1 + 1;
						X4 = X4 + X6;
						X6 = 0;
					}
				}
			}
		}
	}

	{;
//@ assert(X4 + X5 + X6 -1 >= 0);
}
 
	{;
//@ assert(X4 + X5 + X6 -1 <= 0);
}
 
	{;
//@ assert(X4 + X5 <= 1);
}

	{;
//@ assert(X5  >= 0);
}

	{;
//@ assert(X4  >= 0);
}

	{;
//@ assert(X3  >= 0);
}

	{;
//@ assert(X2  >= 0);
}

	{;
//@ assert(X1 + X5 >= 1);
}

	{;
//@ assert(X1 + X2 >= X4 + X5);
}

	{;
//@ assert(X1 + X2 + X3 >= 1);
}

}
