// Source: data/benchmarks/sv-benchmarks/loops/terminator_02-2.c
#include <stdlib.h>
#define assume(e) if(!(e)) exit(-1);
extern int unknown_int(void);
extern _Bool unknown_bool(void);

int main()
{
    int x=unknown_int();
    int z=unknown_int();
    if (!(x>-100)) return 0;
    if (!(x<200)) return 0;
    if (!(z>100)) return 0;
    if (!(z<200)) return 0;
    while(x<100 && z>100) 
    {
        _Bool tmp=unknown_bool();
        if (tmp) {
            x++;
        } else {
            x--;
            z--;
        }
    }                       

    {;
//@ assert(x>=100 || z<=100);
}

    return 0;
}
