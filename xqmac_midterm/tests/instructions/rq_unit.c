#include <stdint.h>
#include "xqrequant.h"
#include "rq_vectors.h"
volatile uint32_t test_index,test_phase;
volatile uint64_t test_actual,test_expected;
static int check(uint64_t actual,uint64_t expected)
{
    if(actual==expected)return 0;
    test_actual=actual;test_expected=expected;return 1;
}
int main(void)
{
    for(unsigned i=0;i<RQ_VECTOR_COUNT;++i){
        test_index=i;const struct rq_vector *v=&rq_vectors[i];
        test_phase=1;
        if(check(xqrequant_dr_raw(v->x,v->m,v->r),v->expected))return 1;
        test_phase=2;
        if(check((uint64_t)(int64_t)xqrequant_dr((int32_t)v->x,(int32_t)v->m,(uint32_t)v->r),v->expected))return 2;
    }
    test_phase=3;
    for(unsigned i=0;i<ALIAS_VECTOR_COUNT;++i){
        test_index=i;const struct alias_vector *v=&alias_vectors[i];
        if(check(rq_aliases[v->kind](v->x,v->m,v->r),v->expected))return 3;
    }
    test_phase=4;return 0;
}
