// Source: data/benchmarks/non_termination/loop/Incorrect_Bit_Calculation_1_T.c
#include <stdlib.h>
#define assume(e) if(!(e)) exit(-1);
extern int unknown_int(void);

int main()
{
    int mask= unknown_int();
    while( mask  > 1 )
    {
        mask >>= 1;
    }
    return 0;
}