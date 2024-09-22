// Source: data/benchmarks/accelerating_invariant_generation/dagger/barbrprime.c
#include <stdlib.h>
#define assume(e) if(!(e)) exit(-1);
extern int unknown_int(void);

int nondet_int();

int main()
{
	int barber;
	int chair;
	int open;
	int p1;
	int p2;
	int p3;
	int p4;
	int p5;

	barber=0;
	chair=0;
	open=0;
	p1=0;
	p2=0;
	p3=0;
	p4=0;
	p5=0;

	while(unknown_int())
	{
		if (unknown_int())
		{
			if (!(p1 >= 0)) 
return 0;

			if (!(p1 <= 0)) 
return 0;

			if (!(barber >= 1)) 
return 0;

			barber = barber-1;
			chair = chair+1;
			p1 = 1;
		}
		else
		{
			if (unknown_int())
			{
				if (!(p2 >= 0)) 
return 0;

				if (!(p2 <= 0)) 
return 0;

				if (!(barber >= 1)) 
return 0;

				barber = barber-1;
				chair = chair+1;
				p2 = 1;
			}
			else
			{
				if (unknown_int())
				{
					if (!(p2 >= 1)) 
return 0;

					if (!(p2 <= 1)) 
return 0;

					if (!(open >=1)) 
return 0;

					open = open -1;
					p2 = 0;
				}
				else
				{
					if (unknown_int())
					{
						if (!(p3>=0)) 
return 0;

						if (!(p3<=0)) 
return 0;

						if (!(barber >=1)) 
return 0;

						barber = barber-1;
						chair = chair +1;
						p3 =1;
					}
					else
					{
						if (unknown_int())
						{
							if (!(p3>=1)) 
return 0;

							if (!(p3<=1)) 
return 0;

							if (!(open >=1)) 
return 0;

							open = open -1;
							p3 =0;
						}
						else
						{
							if (unknown_int())
							{
								if (!(p4 >=0)) 
return 0;

								if (!(p4 <=0)) 
return 0;

								if (!(barber >=1)) 
return 0;

								barber= barber-1;
								chair = chair +1;
								p4 = p4+1;
							}
							else
							{
								if (unknown_int())
								{
									if (! (p4 >=1)) 
return 0;

									if (! (p4 <=1)) 
return 0;

									if (! (open >=1)) 
return 0;

									open = open - 1;
									p4=p4 -1;
								}
								else
								{
									if (unknown_int())
									{
										if (! (p5>=0)) 
return 0;

										if (! (p5<=0)) 
return 0;

										barber=barber+1;
										p5=1;
									}
									else
									{
										if (unknown_int())
										{
											if (! (p5>=1)) 
return 0;

											if (! (p5<=1)) 
return 0;

											if (! (chair >=1)) 
return 0;

											chair= chair -1;
											p5=2;
										}
										else
										{
											if (unknown_int())
											{
												if (! (p5>=2)) 
return 0;

												if (! (p5<=2)) 
return 0;

												open=open +1;
												p5=3;
											}
											else
											{
												if (unknown_int())
												{
													if (! (p5 >= 3)) 
return 0;

													if (! (p5 <= 3)) 
return 0;

													if (! (open == 0)) 
return 0;

													p5=0;
												}
													else
												{
													if (! (p1 >= 1)) 
return 0;

													if (! (p1 <= 1)) 
return 0;

													if (! (open >= 1)) 
return 0;

													open = open-1;
													p1 = 0;
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
		}
	}
	{;
//@ assert(p5 <= 3);
}

	{;
//@ assert(p5 >= open);
}

}
