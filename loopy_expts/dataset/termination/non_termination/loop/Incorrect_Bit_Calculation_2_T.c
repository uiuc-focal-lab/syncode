// Source: data/benchmarks/non_termination/loop/Incorrect_Bit_Calculation_2_T.c
#include <stdlib.h>
#define assume(e) if(!(e)) exit(-1);
extern int unknown_int(void);

int main()
{
    int a0 = unknown_int();
    int a1 = unknown_int();
    if( ( a0 | a1 ) == 0 )
        return 0;
    while( ( a0 & 1 ) == 0)
    {
        a0 = ( a1 << 31 ) | ( a0 >> 1 );
        a1 = a1 >> 1;
    }
    return 0;
}