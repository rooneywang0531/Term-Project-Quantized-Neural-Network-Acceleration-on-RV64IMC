#ifndef XQMAC_H
#define XQMAC_H
#include <stdint.h>
/* R4: custom-0 opcode=0x0b, funct2=0, funct3=0(ss) or 1(us).
 * rs3 is explicit in encoding; wrappers tie rd=rs3 for ordinary accumulation.
 * A single instruction reads all three old values before writing rd.
 */
static inline __attribute__((always_inline)) int32_t xqmac4_ss(uint32_t a,uint32_t w,int32_t acc)
{
    __asm__ volatile (".insn r4 0x0b, 0, 0, %0, %1, %2, %0"
                      : "+r"(acc) : "r"(a),"r"(w));
    return acc;
}
static inline __attribute__((always_inline)) int32_t xqmac4_us(uint32_t a,uint32_t w,int32_t acc)
{
    __asm__ volatile (".insn r4 0x0b, 1, 0, %0, %1, %2, %0"
                      : "+r"(acc) : "r"(a),"r"(w));
    return acc;
}
/* Raw-register interfaces test ignored upper bits and RV64 sign extension. */
static inline __attribute__((always_inline)) uint64_t xqmac4_ss_raw(uint64_t a,uint64_t w,uint64_t acc)
{
    uint64_t result;
    __asm__ volatile (".insn r4 0x0b, 0, 0, %0, %1, %2, %3"
                      : "=r"(result) : "r"(a),"r"(w),"r"(acc));
    return result;
}
static inline __attribute__((always_inline)) uint64_t xqmac4_us_raw(uint64_t a,uint64_t w,uint64_t acc)
{
    uint64_t result;
    __asm__ volatile (".insn r4 0x0b, 1, 0, %0, %1, %2, %3"
                      : "=r"(result) : "r"(a),"r"(w),"r"(acc));
    return result;
}
/* Block input z=-128: for each lane, (signed8(raw)+128)==unsigned8(raw^0x80).
 * One XOR per 4 activations; its result can be reused across output channels.
 * All conversion/load cost stays in the future benchmarked kernel.
 */
static inline __attribute__((always_inline)) uint32_t xqmac_center_z128(uint32_t packed_raw)
{
    return packed_raw ^ UINT32_C(0x80808080);
}
/* General zero-point path for a full group of four VALID taps.
 * z=-128: use unsigned lanes after XOR. z=0: signed path directly.
 * Other z: sum(raw*w)-z*sum(w), explicitly modular 32-bit correction.
 * On padding boundaries only valid taps may participate; never apply the
 * whole-filter correction after skipping taps. Tail handling remains scalar.
 */
static inline __attribute__((always_inline)) int32_t xqmac_i32(uint32_t x)
{
    return x <= UINT32_C(0x7fffffff) ? (int32_t)x : -1-(int32_t)(~x);
}
/* Precondition: zp is an INT8 tensor zero point in [-128,127]. */
static inline __attribute__((always_inline)) int32_t xqmac4_centered(uint32_t raw,uint32_t w,int32_t acc,int zp)
{
    if(zp==-128)return xqmac4_us(xqmac_center_z128(raw),w,acc);
    int32_t result=xqmac4_ss(raw,w,acc);
    if(zp==0)return result;
    int32_t sum=0;
    for(unsigned i=0;i<4;++i){
        uint32_t b=(w>>(8*i))&255u;
        sum+=b>=128u?(int32_t)b-256:(int32_t)b;
    }
    return xqmac_i32((uint32_t)result-(uint32_t)(zp*sum));
}
#endif
