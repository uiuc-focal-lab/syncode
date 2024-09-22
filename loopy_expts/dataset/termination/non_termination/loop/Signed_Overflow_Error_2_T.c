// Source: data/benchmarks/non_termination/loop/Signed_Overflow_Error_2_T.c
#include <stdlib.h>
#define assume(e) if(!(e)) exit(-1);
extern int unknown_int(void);

int main()
{
    int needed =  unknown_int();
    int smallest = 1;
    while( smallest <= needed )
    {
        if( smallest == 0 )
            return 0;
        smallest <<= 1;
    }
    return 0;
}