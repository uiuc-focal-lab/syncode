// Source: data/benchmarks/non_termination/loop/Signed_Overflow_Error_1_T.c
#include <stdlib.h>
#define assume(e) if(!(e)) exit(-1);

int main()
{
    long i;
    for( i = 1 ; i <= 0xFFFFFFFF ; i <<= 1 )
    {
        if( i == ( (long)1 << 31 ))
            break;
    }
    return 0;
}