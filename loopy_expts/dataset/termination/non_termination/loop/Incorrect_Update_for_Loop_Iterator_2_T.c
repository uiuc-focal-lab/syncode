// Source: data/benchmarks/non_termination/loop/Incorrect_Update_for_Loop_Iterator_2_T.c
#include <stdlib.h>
#define assume(e) if(!(e)) exit(-1);
extern unsigned char unknown_uchar(void);

int main()
{
    unsigned char l = unknown_uchar();

    while( l-- )
    {
        if( l && l-- )
        {
            
        }
    }
    return 0;
}