// Source: data/benchmarks/accelerating_invariant_generation/dagger/lifo.c
#include <stdlib.h>
#define assume(e) if(!(e)) exit(-1);
extern int unknown_int(void);

int nondet_int();

int main()
{
	int I;
	int Sa;
	int Ea;
	int Ma;
	int Sb;
	int Eb;
	int Mb;

	if (! (I>=1)) 
return 0;

	Sa=0;
	Ea=0;
	Ma=0;
	Sb=0;
	Eb=0;
	Mb=0;

	while(unknown_int())
	{
		if (unknown_int())
		{
			if (! (Sb >= 1)) 
return 0;

			Sb = Sb-1;
			Sa = Ea+Ma+1;
			Ea = 0;
			Ma = 0;
		}
		else
		{
			if (unknown_int())
			{
				if (! (I >= 1)) 
return 0;

				I = I -1;
				Sa = Sa + Ea + Ma + 1;
				Ea = 0;
				Ma =0;
			}
			else
			{
				if (unknown_int())
				{
					if (! (I>=1)) 
return 0;

					I=I-1;
					Sb=Sb+Eb+Mb+1;
					Eb=0;
					Mb=0;
				}
				else
				{
					if (unknown_int())
					{
						if (! (Sa>=1)) 
return 0;

						Sa=Sa-1;
						Sb=Sb+Eb+Mb+1;
						Eb=0;
						Mb=0;
					}
					else
					{
						if (unknown_int())
						{
							if (! (Sa>=1)) 
return 0;

							I=I+Sa+Ea+Ma;
							Sa=0;
							Ea=1;
							Ma=0;
						}
						else
						{
							if (unknown_int())
							{
								if (! (Sb>=1)) 
return 0;

								Sb=Sb-1;
								I=I+Sa+Ea+Ma;
								Sa=0;
								Ea=1;
								Ma=0;
							}
							else
							{
								if (unknown_int())
								{
									if (! (Sb>=1)) 
return 0;

									I=I+Sb+Eb+Mb;
									Sb=0;
									Eb=1;
									Mb=0;
								}
								else
								{
									if (unknown_int())
									{
										if (! (Sa>=1)) 
return 0;

										Sa=Sa-1;
										I=I+Sb+Eb+Mb;
										Sb=0;
										Eb=1;
										Mb=0;
									}
									else
									{
										if (unknown_int())
										{
											if (! (Ea >=1)) 
return 0;

											Ea = Ea -1;
											Ma = Ma +1;
										}
										else
										{
											if (! (Eb >=1)) 
return 0;

											Eb = Eb -1;
											Mb = Mb +1;
										}
									}
								}
							}
						}
					}
				}
			}
		}
	}

	{;
//@ assert(Ea + Ma <= 1);
}

	{;
//@ assert(Eb + Mb <= 1);
}

	{;
//@ assert(Mb  >= 0);
}

	{;
//@ assert(Eb  >= 0);
}

	{;
//@ assert(Ma  >= 0);
}

	{;
//@ assert(Ea  >= 0);
}

}
