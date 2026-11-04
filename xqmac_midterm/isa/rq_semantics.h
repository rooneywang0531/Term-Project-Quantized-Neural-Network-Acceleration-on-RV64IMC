#ifndef RQ_SEMANTICS_H
#define RQ_SEMANTICS_H
#include <stdint.h>
/* Portable magnitude formulation: no negative signed shift, no overflow. */
static inline int rq_valid(uint64_t m,uint64_t r)
{
    return (uint32_t)m<=UINT32_C(0x7fffffff) && (uint32_t)r<=31;
}
static inline uint64_t rq_ref(uint64_t x,uint64_t multiplier,uint64_t right_shift)
{
    uint32_t lo=(uint32_t)x;
    int64_t sx=lo<=UINT32_C(0x7fffffff)?(int64_t)lo:(int64_t)lo-INT64_C(4294967296);
    int64_t product=sx*(uint32_t)multiplier;
    uint64_t mag=(uint64_t)(product<0?-product:product);
    /* First rounding matches truncation toward zero of the signed nudge. */
    uint64_t high=(mag+(product<0?UINT64_C(1073741823):UINT64_C(1073741824)))>>31;
    unsigned e=(uint32_t)right_shift;
    if(e)high=(high+(UINT64_C(1)<<(e-1)))>>e;
    int64_t answer=product<0?-(int64_t)high:(int64_t)high;
    return (uint64_t)answer; /* Exact RV64 sign extension of the INT32 result. */
}
static inline int sr_valid(uint64_t m,uint64_t r)
{
    return (uint32_t)m<=UINT32_C(0x7fffffff) && (uint32_t)r>=31 && (uint32_t)r<=62;
}
static inline uint64_t sr_ref(uint64_t x,uint64_t multiplier,uint64_t right_shift)
{
    uint32_t lo=(uint32_t)x;
    int64_t sx=lo<=UINT32_C(0x7fffffff)?(int64_t)lo:(int64_t)lo-INT64_C(4294967296);
    unsigned r=(uint32_t)right_shift;
    int64_t n=sx*(uint32_t)multiplier+(INT64_C(1)<<(r-1));
    int64_t divisor=INT64_C(1)<<r;
    int64_t y=n>=0?n/divisor:-((-n+divisor-1)/divisor);
    return (uint64_t)y;
}
#endif
