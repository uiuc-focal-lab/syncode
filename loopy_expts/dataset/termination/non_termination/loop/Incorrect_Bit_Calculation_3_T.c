// Source: data/benchmarks/non_termination/loop/Incorrect_Bit_Calculation_3_T.c
#include <stdlib.h>
#define assume(e) if(!(e)) exit(-1);
extern int unknown_int(void);

int main()
{
    int wc = unknown_int();
    int mask = ( 1 << 26 ) - 1;
    do{
        
    }while( (wc = ( wc >> 6 ) & mask) );
    return 0;
}