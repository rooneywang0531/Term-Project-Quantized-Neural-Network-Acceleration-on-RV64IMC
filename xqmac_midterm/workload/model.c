#include <stdint.h>
#include "model_data.h"
#include "operators.h"
#ifdef HOST_TEST
#include <stdio.h>
#endif
static int8_t arena[ARENA_BYTES] __attribute__((aligned(16)));
volatile int32_t current_operator=-1;
volatile int32_t checked_operators=0;
volatile int32_t first_bad_index=-1,first_bad_actual=0,first_bad_expected=0;
volatile uint32_t mismatches=0;
/* Validation is outside all .text.kernel.* ranges. Never copies golden to arena. */
static __attribute__((noinline)) int check_output(int op,const int8_t *actual,const int8_t *expected,int n)
{
    uint32_t count=0;
    for(int i=0;i<n;++i)if(actual[i]!=expected[i]){
        if(!count){first_bad_index=i;first_bad_actual=actual[i];first_bad_expected=expected[i];}
        ++count;
    }
    mismatches=count;
#ifdef HOST_TEST
    if(count)printf("FAIL op %02d: %u mismatches; first[%d]: got %d expected %d\n",op,count,(int)first_bad_index,(int)first_bad_actual,(int)first_bad_expected);
    else printf("PASS op %02d: all %d outputs matched.\n",op,n);
    fflush(stdout);
#else
    (void)op;
#endif
    if(!count)++checked_operators;
    return count!=0;
}
int model_run(const int8_t *input,const int8_t *golden)
{
    current_operator=-1;checked_operators=0;first_bad_index=-1;mismatches=0;
    for(int i=0;i<INPUT_BYTES;++i)arena[INPUT_OFFSET+i]=input[i];
#include "graph.inc"
    return 0;
}
const int8_t *model_output(void){return arena+OUTPUT_OFFSET;}
#ifndef MODEL_LIBRARY
extern const int8_t fixture_input[],fixture_golden[];
int main(void){return model_run(fixture_input,fixture_golden);}
#endif
