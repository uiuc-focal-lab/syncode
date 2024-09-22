// Source: data/benchmarks/non_termination/loop/Type_Conversion_in_Comparison_2_T.c
#include <stdlib.h>
#define assume(e) if(!(e)) exit(-1);
extern char unknown_char(void);
extern unsigned char unknown_uchar(void);

int main()
{
	unsigned char c1 = unknown_uchar();
	char c2 =  unknown_char();
	unsigned char ac;
	for( ac = (unsigned char)c1 ; ac != (unsigned char)c2 ; ac++ )
	{
        
	}
	return 0;
 }