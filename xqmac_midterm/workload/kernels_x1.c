/* Full ResNet-18 X1: packed MAC, optional exact DR/SR requantization. */
#include <stdint.h>
#include "model_data.h"
#include "isa_ops.h"
#define INLINE static inline __attribute__((always_inline))
#define KERNEL(name) __attribute__((noinline,noclone,section(".text.kernel." #name)))
/* Audited model: multipliers >=0, shifts in [-31,0]. GCC arithmetic right shift. */
INLINE int32_t requantize(int32_t x, int32_t multiplier, int shift)
{
#ifdef USE_RQ
    return RQ_DR(x,multiplier,(uint32_t)(-shift));
#else
    int64_t product = (int64_t)x * multiplier;
    int64_t nudge = product >= 0 ? ((int64_t)1 << 30) : 1 - ((int64_t)1 << 30);
    int32_t high = (int32_t)((product + nudge) / ((int64_t)1 << 31));
    int exponent = -shift;
    if (!exponent) return high;
    uint32_t mask = ((uint32_t)1 << exponent) - 1;
    uint32_t remainder = (uint32_t)high & mask;
    uint32_t threshold = (mask >> 1) + (high < 0);
    return (high >> exponent) + (remainder > threshold);
#endif
}
INLINE int8_t clip(int32_t v,int amin,int amax)
{
    if(v<amin)v=amin;
    if(v>amax)v=amax;
    return (int8_t)v;
}

/* Full-model packed kernels: original NHWC activations/OHWI weights.
 * prepare.py audits all shapes, zero points and linked alignment.
 * The common path uses aligned words; RGB has a separate safe byte-load path.
 * Explicit memcpy + alignment promise avoids strict-aliasing violations.
 */
#if __BYTE_ORDER__ != __ORDER_LITTLE_ENDIAN__
#error "This packed load mapping requires the audited little-endian target"
#endif

INLINE uint64_t load4_aligned(const int8_t *p)
{
    int32_t word;
    __builtin_memcpy(&word, __builtin_assume_aligned(p,4), sizeof(word));
    return (uint64_t)(int64_t)word;
}
INLINE int32_t low32_signed(uint64_t value)
{
    uint32_t low=(uint32_t)value;
    int32_t signed_low;
    __builtin_memcpy(&signed_low,&low,sizeof(low));
    return signed_low;
}
/* RGB first layer has explicit PAD and no skipped taps. Compute correction
 * INSIDE the operator once, not offline. Each 7-pixel row has 21 bytes:
 * five 4-lane signed dot products plus one scalar raw tail element. */
INLINE uint64_t load4_bytes(const int8_t *p)
{
    int32_t word;
    __builtin_memcpy(&word,p,4);
    return (uint64_t)(int64_t)word;
}
/* RGB v2: original model data is converted at runtime INSIDE op02.
 * Each spatial patch is packed once and reused by all 16 output-channel tiles.
 * 35 full groups + 7 scalar tails preserve the v1 custom MAC counts. */
INLINE uint32_t pack4_registers(const int8_t *p)
{
    return (uint32_t)(uint8_t)p[0]
        | ((uint32_t)(uint8_t)p[1]<<8)
        | ((uint32_t)(uint8_t)p[2]<<16)
        | ((uint32_t)(uint8_t)p[3]<<24);
}
INLINE void conv_rgb(const int8_t *input,int8_t *output,const int8_t *weights,
    const int32_t *bias,const int32_t *multipliers,const int32_t *shifts,
    int iw,int oh,int ow,int oc,int kh,int kw,int sh,int sw,int iz,int oz,int amin,int amax)
{
    if(iw!=230 || oh!=112 || ow!=112 || oc!=64 || kh!=7 || kw!=7 || sh!=2 || sw!=2 || iz!=-14)
        __builtin_trap();
    uint32_t packed_weights[16][35][4] __attribute__((aligned(16)));
    int8_t tail_weights[16][7][4];
    int32_t correction[64];
    uint32_t packed_patch[35] __attribute__((aligned(16)));
    int8_t tail_patch[7];
    /* Original OHWI constants remain unchanged. All conversion is measured. */
    for(int c=0;c<64;++c){
        int32_t sum=0;
        for(int i=0;i<147;++i)sum+=weights[c*147+i];
        correction[c]=-iz*sum;
    }
    for(int tile=0;tile<16;++tile)for(int ky=0;ky<7;++ky)for(int q=0;q<4;++q){
        const int8_t *w=weights+(tile*4+q)*147+ky*21;
        for(int g=0;g<5;++g)packed_weights[tile][ky*5+g][q]=pack4_registers(w+g*4);
        tail_weights[tile][ky][q]=w[20];
    }
    for(int oy=0;oy<112;++oy)for(int ox=0;ox<112;++ox){
        for(int ky=0;ky<7;++ky){
            const int8_t *a=input+((oy*2+ky)*230+ox*2)*3;
            for(int g=0;g<5;++g)packed_patch[ky*5+g]=pack4_registers(a+g*4);
            tail_patch[ky]=a[20];
        }
        for(int tile=0;tile<16;++tile){
            int c=tile*4;
            uint64_t acc0=(uint64_t)(int64_t)bias[c]+(uint64_t)(int64_t)correction[c];
            uint64_t acc1=(uint64_t)(int64_t)bias[c+1]+(uint64_t)(int64_t)correction[c+1];
            uint64_t acc2=(uint64_t)(int64_t)bias[c+2]+(uint64_t)(int64_t)correction[c+2];
            uint64_t acc3=(uint64_t)(int64_t)bias[c+3]+(uint64_t)(int64_t)correction[c+3];
            for(int g=0;g<35;++g){
                uint64_t a=packed_patch[g];
                const uint32_t *w=packed_weights[tile][g];
                acc0=QMAC_SS(a,w[0],acc0);
                acc1=QMAC_SS(a,w[1],acc1);
                acc2=QMAC_SS(a,w[2],acc2);
                acc3=QMAC_SS(a,w[3],acc3);
            }
            for(int ky=0;ky<7;++ky){
                int32_t a=tail_patch[ky];
                acc0+=(uint64_t)(int64_t)(a*tail_weights[tile][ky][0]);
                acc1+=(uint64_t)(int64_t)(a*tail_weights[tile][ky][1]);
                acc2+=(uint64_t)(int64_t)(a*tail_weights[tile][ky][2]);
                acc3+=(uint64_t)(int64_t)(a*tail_weights[tile][ky][3]);
            }
            output[(oy*ow+ox)*oc+c]  =clip(requantize(low32_signed(acc0),multipliers[c],shifts[c])+oz,amin,amax);
            output[(oy*ow+ox)*oc+c+1]=clip(requantize(low32_signed(acc1),multipliers[c+1],shifts[c+1])+oz,amin,amax);
            output[(oy*ow+ox)*oc+c+2]=clip(requantize(low32_signed(acc2),multipliers[c+2],shifts[c+2])+oz,amin,amax);
            output[(oy*ow+ox)*oc+c+3]=clip(requantize(low32_signed(acc3),multipliers[c+3],shifts[c+3])+oz,amin,amax);
        }
    }
}
INLINE void conv(const int8_t *input,int8_t *output,const int8_t *weights,
    const int32_t *bias,const int32_t *multipliers,const int32_t *shifts,
    int ih,int iw,int ic,int oh,int ow,int oc,int kh,int kw,int sh,int sw,
    int ph,int pw,int iz,int oz,int amin,int amax)
{
    if(ic==3){
        conv_rgb(input,output,weights,bias,multipliers,shifts,iw,oh,ow,oc,kh,kw,sh,sw,iz,oz,amin,amax);
        return;
    }
    /* Remaining audited Conv layers have IC multiple of 4 and iz=-128. */
    if (iz != -128 || ic % 4 || oc % 4) __builtin_trap();
    const int weight_stride=kh*kw*ic;
    for(int oy=0;oy<oh;++oy) for(int ox=0;ox<ow;++ox)
    for(int c=0;c<oc;c+=4){
        /* Full-width register containers avoid per-MAC C int32 canonicalization.
         * ISA still accumulates low32 modulo 2^32 and sign-extends its result. */
        uint64_t acc0=(uint64_t)(int64_t)bias[c];
        uint64_t acc1=(uint64_t)(int64_t)bias[c+1];
        uint64_t acc2=(uint64_t)(int64_t)bias[c+2];
        uint64_t acc3=(uint64_t)(int64_t)bias[c+3];
        for(int ky=0;ky<kh;++ky){
            int iy=oy*sh+ky-ph;
            if(iy<0 || iy>=ih)continue;
            for(int kx=0;kx<kw;++kx){
                int ix=ox*sw+kx-pw;
                if(ix<0 || ix>=iw)continue;
                const int8_t *a=input+(iy*iw+ix)*ic;
                const int8_t *w0=weights+((c*kh+ky)*kw+kx)*ic;
                const int8_t *w1=w0+weight_stride;
                const int8_t *w2=w1+weight_stride;
                const int8_t *w3=w2+weight_stride;
                for(int k=0;k<ic;k+=4){
                    /* Low 32 bits XOR 0x80808080; upper bits are ignored by ISA. */
                    uint64_t packed_a=load4_aligned(a+k)^UINT64_C(0xffffffff80808080);
                    acc0=QMAC_US(packed_a,load4_aligned(w0+k),acc0);
                    acc1=QMAC_US(packed_a,load4_aligned(w1+k),acc1);
                    acc2=QMAC_US(packed_a,load4_aligned(w2+k),acc2);
                    acc3=QMAC_US(packed_a,load4_aligned(w3+k),acc3);
                }
            }
        }
        output[(oy*ow+ox)*oc+c]  =clip(requantize(low32_signed(acc0),multipliers[c],shifts[c])+oz,amin,amax);
        output[(oy*ow+ox)*oc+c+1]=clip(requantize(low32_signed(acc1),multipliers[c+1],shifts[c+1])+oz,amin,amax);
        output[(oy*ow+ox)*oc+c+2]=clip(requantize(low32_signed(acc2),multipliers[c+2],shifts[c+2])+oz,amin,amax);
        output[(oy*ow+ox)*oc+c+3]=clip(requantize(low32_signed(acc3),multipliers[c+3],shifts[c+3])+oz,amin,amax);
    }
}
INLINE void add(const int8_t *input,const int8_t *skip,int8_t *output,int n,
    int iz,int sz,int oz,int m1,int s1,int m2,int s2,int mo,int so,int amin,int amax)
{
    for(int i=0;i<n;++i){
        int32_t a=((int32_t)input[i]-iz)*(1<<20);
        int32_t b=((int32_t)skip[i]-sz)*(1<<20);
        int32_t sum=requantize(a,m1,s1)+requantize(b,m2,s2);
        output[i]=clip(requantize(sum,mo,so)+oz,amin,amax);
    }
}
INLINE void transpose(const int8_t *input,int8_t *output)
{
    for(int y=0;y<224;++y) for(int x=0;x<224;++x) for(int c=0;c<3;++c)
        output[(y*224+x)*3+c]=input[(c*224+y)*224+x];
}
INLINE void pad(const int8_t *input,int8_t *output,int ih,int iw,int c,
    int oh,int ow,int top,int left,int zero)
{
    for(int y=0;y<oh;++y) for(int x=0;x<ow;++x) for(int k=0;k<c;++k){
        int iy=y-top,ix=x-left;
        output[(y*ow+x)*c+k]=(iy>=0 && iy<ih && ix>=0 && ix<iw)? input[(iy*iw+ix)*c+k]:(int8_t)zero;
    }
}
INLINE void pool(const int8_t *input,int8_t *output,int ih,int iw,int c,
    int oh,int ow,int kh,int kw,int sh,int sw,int average)
{
    (void)ih; /* All audited pool windows are VALID and fully in bounds. */
    for(int y=0;y<oh;++y) for(int x=0;x<ow;++x) for(int k=0;k<c;++k){
        int32_t acc=average?0:-128;
        for(int ky=0;ky<kh;++ky) for(int kx=0;kx<kw;++kx){
            int32_t v=input[((y*sh+ky)*iw+x*sw+kx)*c+k];
            if(average)acc+=v; else if(v>acc)acc=v;
        }
        if(average){
            int n=kh*kw;
            acc=acc>0?(acc+n/2)/n:(acc-n/2)/n;
        }
        output[(y*ow+x)*c+k]=(int8_t)acc;
    }
}

INLINE void fc(const int8_t *input,int8_t *output,const int8_t *weights,
    const int32_t *bias,const int32_t *multipliers,const int32_t *shifts,int iz,int oz)
{
    if(iz!=-128)__builtin_trap();
    for(int c=0;c<1000;c+=4){
        uint64_t acc0=(uint64_t)(int64_t)bias[c];
        uint64_t acc1=(uint64_t)(int64_t)bias[c+1];
        uint64_t acc2=(uint64_t)(int64_t)bias[c+2];
        uint64_t acc3=(uint64_t)(int64_t)bias[c+3];
        for(int k=0;k<512;k+=4){
            uint64_t packed=load4_aligned(input+k)^UINT64_C(0xffffffff80808080);
            acc0=QMAC_US(packed,load4_aligned(weights+c*512+k),acc0);
            acc1=QMAC_US(packed,load4_aligned(weights+(c+1)*512+k),acc1);
            acc2=QMAC_US(packed,load4_aligned(weights+(c+2)*512+k),acc2);
            acc3=QMAC_US(packed,load4_aligned(weights+(c+3)*512+k),acc3);
        }
        {
            int exponent=31-shifts[c+0];
#ifdef USE_RQ
            int32_t value=RQ_SR(low32_signed(acc0),multipliers[c+0],(uint32_t)exponent);
#else
            int64_t product=(int64_t)low32_signed(acc0)*multipliers[c+0];
            int32_t value=(int32_t)((product+((int64_t)1<<(exponent-1)))>>exponent);
#endif
            output[c+0]=clip(value+oz,-128,127);
        }
        {
            int exponent=31-shifts[c+1];
#ifdef USE_RQ
            int32_t value=RQ_SR(low32_signed(acc1),multipliers[c+1],(uint32_t)exponent);
#else
            int64_t product=(int64_t)low32_signed(acc1)*multipliers[c+1];
            int32_t value=(int32_t)((product+((int64_t)1<<(exponent-1)))>>exponent);
#endif
            output[c+1]=clip(value+oz,-128,127);
        }
        {
            int exponent=31-shifts[c+2];
#ifdef USE_RQ
            int32_t value=RQ_SR(low32_signed(acc2),multipliers[c+2],(uint32_t)exponent);
#else
            int64_t product=(int64_t)low32_signed(acc2)*multipliers[c+2];
            int32_t value=(int32_t)((product+((int64_t)1<<(exponent-1)))>>exponent);
#endif
            output[c+2]=clip(value+oz,-128,127);
        }
        {
            int exponent=31-shifts[c+3];
#ifdef USE_RQ
            int32_t value=RQ_SR(low32_signed(acc3),multipliers[c+3],(uint32_t)exponent);
#else
            int64_t product=(int64_t)low32_signed(acc3)*multipliers[c+3];
            int32_t value=(int32_t)((product+((int64_t)1<<(exponent-1)))>>exponent);
#endif
            output[c+3]=clip(value+oz,-128,127);
        }
    }
}
#if defined(SCOPE_FC)
#include "operators_fc.inc"
#elif defined(SCOPE_BLOCK)
#include "operators_block.inc"
#else
#include "operators.inc"
#endif
