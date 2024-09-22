// Source: data/benchmarks/non_termination/loop/Adding_Subtracting_Zero_1_T.c
#include <stdlib.h>
#define assume(e) if(!(e)) exit(-1);
extern int unknown_int(void);

int main()
{

    int linesToRead = unknown_int();
    if( linesToRead < 0 )
        return 0;
    int h = unknown_int();
    while( linesToRead && h > 0 )
    {
        if( linesToRead > h )
            linesToRead = h;
        h -= linesToRead;
    }
    return 0;

}