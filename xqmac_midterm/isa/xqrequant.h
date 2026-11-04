#ifndef XQREQUANT_H
#define XQREQUANT_H
#include <stdint.h>
/* custom-1 R4; low32(x) signed, low32(m) in [0,INT32_MAX], low32(r) in [0,31]. */
static inline __attribute__((always_inline)) uint64_t xqrequant_dr_raw(uint64_t x,uint64_t m,uint64_t r)
{
    uint64_t result;
    __asm__ volatile (".insn r4 0x2b, 0, 0, %0, %1, %2, %3"
                      : "=r"(result) : "r"(x),"r"(m),"r"(r));
    return result;
}
static inline __attribute__((always_inline)) int32_t xqrequant_dr(int32_t x,int32_t m,uint32_t r)
{
    return (int32_t)xqrequant_dr_raw((uint64_t)(int64_t)x,(uint64_t)(int64_t)m,r);
}
static inline __attribute__((always_inline)) uint64_t xqrequant_sr_raw(uint64_t x,uint64_t m,uint64_t r)
{
    uint64_t result;
    __asm__ volatile (".insn r4 0x2b, 1, 0, %0, %1, %2, %3"
                      : "=r"(result) : "r"(x),"r"(m),"r"(r));
    return result;
}
static inline __attribute__((always_inline)) int32_t xqrequant_sr(int32_t x,int32_t m,uint32_t r)
{
    return (int32_t)xqrequant_sr_raw((uint64_t)(int64_t)x,(uint64_t)(int64_t)m,r);
}
#endif
