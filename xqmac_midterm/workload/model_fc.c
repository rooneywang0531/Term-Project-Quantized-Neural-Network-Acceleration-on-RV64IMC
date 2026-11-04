#include <stdint.h>
#include "model_data.h"
#include "operators.h"
static int8_t arena[1536] __attribute__((aligned(16)));
extern const int8_t fixture_golden[];
volatile int32_t first_bad_index=-1,first_bad_actual,first_bad_expected;
int main(void)
{
    /* Isolated FC fixture setup, outside the measured op36 symbol.
     * The input is a reference boundary activation, not a C consumer output
     * inside the full model. Full inference always computes its own inputs. */
    for(int i=0;i<512;++i)arena[i]=fixture_golden[4974060+i];
    op_36_fully_connected(arena,(const int8_t *)0,arena+512);
    for(int i=0;i<1000;++i)if(arena[512+i]!=fixture_golden[4974572+i]){
        first_bad_index=i;first_bad_actual=arena[512+i];first_bad_expected=fixture_golden[4974572+i];return 37;
    }
    return 0;
}
