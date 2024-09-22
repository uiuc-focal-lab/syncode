// Source: data/benchmarks/non_termination/loop/Signed_Overflow_Error_3_T.c
#include <stdlib.h>
#define assume(e) if(!(e)) exit(-1);
extern unsigned int unknown_uint(void);

int main()
{
    unsigned int number = unknown_uint();
    int width;
    for( width = 1; number >= 10 ; width++ )
        number /= 10;
    return 0;
}