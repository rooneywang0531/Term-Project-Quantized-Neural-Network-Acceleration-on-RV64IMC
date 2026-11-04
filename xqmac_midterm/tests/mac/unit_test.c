#include <stdint.h>
#include "xqmac.h"
#include "test_vectors.h"
#include "alias_tests.h"
volatile uint32_t test_phase=0,test_index=0,test_mode=0,test_alias=0;
volatile uint64_t test_actual=0,test_expected=0;
volatile uint32_t passed_vectors=0,passed_alias_calls=0;

static int mismatch(uint64_t actual,uint64_t expected)
{
    if(actual==expected)return 0;
    test_actual=actual;test_expected=expected;return 1;
}
static uint64_t widen(int32_t x){return (uint64_t)(int64_t)x;}
int main(void)
{
    test_phase=1;
    for(uint32_t i=0;i<VECTOR_COUNT;++i){
        test_index=i;const struct test_vector *v=&vectors[i];
        test_mode=0;if(mismatch(xqmac4_ss_raw(v->a,v->w,v->acc),v->ss))return 1;
        test_mode=1;if(mismatch(xqmac4_us_raw(v->a,v->w,v->acc),v->us))return 2;
        int32_t acc=xqmac_i32((uint32_t)v->acc);
        test_mode=2;if(mismatch(widen(xqmac4_centered((uint32_t)v->a,(uint32_t)v->w,acc,-128)),v->z128))return 3;
        test_mode=3;if(mismatch(widen(xqmac4_centered((uint32_t)v->a,(uint32_t)v->w,acc,-14)),v->z14))return 4;
        test_mode=4;if(mismatch(widen(xqmac4_centered((uint32_t)v->a,(uint32_t)v->w,acc,0)),v->ss))return 5;
        test_mode=5;if(mismatch(widen(xqmac4_centered((uint32_t)v->a,(uint32_t)v->w,acc,127)),v->z127))return 6;
        ++passed_vectors;
    }
    test_phase=2;
    for(uint32_t i=0;i<ALIAS_VECTOR_COUNT;++i){
        test_index=i;const struct test_vector *v=&vectors[alias_vector_indices[i]];
        for(uint32_t mode=0;mode<2;++mode)for(uint32_t kind=0;kind<ALIAS_CASE_COUNT;++kind){
            test_mode=mode;test_alias=kind;
            if(mismatch(alias_functions[mode][kind](v->a,v->w,v->acc),alias_expected[i][mode][kind]))return 7;
            ++passed_alias_calls;
        }
    }
    test_phase=3;return 0;
}
