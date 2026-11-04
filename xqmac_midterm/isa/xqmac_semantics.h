#ifndef XQMAC_SEMANTICS_H
#define XQMAC_SEMANTICS_H
#include <stdint.h>
/* Portable reference: no signed overflow, no implementation-defined narrowing. */
static inline int32_t xqmac_s8(uint32_t byte)
{
    return (byte & 128u) ? (int32_t)(byte & 255u)-256 : (int32_t)(byte & 255u);
}
static inline uint64_t xqmac_sext32(uint32_t value)
{
    return value & UINT32_C(0x80000000) ? UINT64_C(0xffffffff00000000)|value : value;
}
static inline uint64_t xqmac_ref(uint64_t a,uint64_t w,uint64_t accumulator,int unsigned_a)
{
    int32_t dot=0;
    for(unsigned i=0;i<4;++i){
        uint32_t aa=(uint32_t)(a>>(8*i))&255u;
        uint32_t ww=(uint32_t)(w>>(8*i))&255u;
        int32_t av=unsigned_a?(int32_t)aa:xqmac_s8(aa);
        dot+=av*xqmac_s8(ww);
    }
    /* ISA explicitly defines modular 32-bit accumulation, then sign extension. */
    return xqmac_sext32((uint32_t)accumulator+(uint32_t)dot);
}
#endif
