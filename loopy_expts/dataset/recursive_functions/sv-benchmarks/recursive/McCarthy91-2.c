// Source: data/benchmarks/sv-benchmarks/recursive/McCarthy91-2.c
#include <stdlib.h>
#define assume(e) if(!(e)) exit(-1);
#define abort() exit(-2);
extern int unknown_int(void);


/* Function_f91 */
int f91(int x) {
    if (x > 100)
        return x -10;
    else {
        return f91(f91(x+11));
    }
}


/* Function_main */
int main() {
    int x = unknown_int();
    int result = f91(x);
    if (result == 91 || x > 101 && result == x - 10) {
        return 0;
    } else {
        { ERROR: {; 
//@ assert(\false);
}
}
    }
}