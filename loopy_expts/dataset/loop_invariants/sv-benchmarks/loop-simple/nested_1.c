// Source: data/benchmarks/sv-benchmarks/loop-simple/nested_1.c
#include <stdlib.h>
#define assume(e) if(!(e)) exit(-1);

int main() {
	int a = 6;

	for(a = 0; a < 6; ++a) {

	}
	if(!(a == 6 )) {
		{; 
//@ assert(\false);
};
	}
	return 1;
}