#include <stdint.h>
#include "model_data.h"
#define INLINE static inline __attribute__((always_inline))
#define KERNEL(name) __attribute__((noinline,noclone,section(".text.kernel." #name)))
/* Audited model: multipliers >=0, shifts in [-31,0]. GCC arithmetic right shift. */
INLINE int32_t requantize(int32_t x, int32_t multiplier, int shift)
{
    int64_t product = (int64_t)x * multiplier;
    int64_t nudge = product >= 0 ? ((int64_t)1 << 30) : 1 - ((int64_t)1 << 30);
    int32_t high = (int32_t)((product + nudge) / ((int64_t)1 << 31));
    int exponent = -shift;
    if (!exponent) return high;
    uint32_t mask = ((uint32_t)1 << exponent) - 1;
    uint32_t remainder = (uint32_t)high & mask;
    uint32_t threshold = (mask >> 1) + (high < 0);
    return (high >> exponent) + (remainder > threshold);
}
INLINE int8_t clip(int32_t v,int amin,int amax)
{
    if(v<amin)v=amin;
    if(v>amax)v=amax;
    return (int8_t)v;
}
INLINE void conv(const int8_t *input,int8_t *output,const int8_t *weights,
    const int32_t *bias,const int32_t *multipliers,const int32_t *shifts,
    int ih,int iw,int ic,int oh,int ow,int oc,int kh,int kw,int sh,int sw,
    int ph,int pw,int iz,int oz,int amin,int amax)
{
    for(int oy=0;oy<oh;++oy) for(int ox=0;ox<ow;++ox) for(int c=0;c<oc;++c){
        int32_t acc=bias[c];
        for(int ky=0;ky<kh;++ky){
            int iy=oy*sh+ky-ph;
            if(iy<0 || iy>=ih)continue;
            for(int kx=0;kx<kw;++kx){
                int ix=ox*sw+kx-pw;
                if(ix<0 || ix>=iw)continue;
                const int8_t *a=input+(iy*iw+ix)*ic;
                const int8_t *w=weights+((c*kh+ky)*kw+kx)*ic;
                for(int k=0;k<ic;++k) acc+=((int32_t)a[k]-iz)*(int32_t)w[k];
            }
        }
        output[(oy*ow+ox)*oc+c]=clip(requantize(acc,multipliers[c],shifts[c])+oz,amin,amax);
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
    for(int c=0;c<1000;++c){
        int32_t acc=bias[c];
        for(int k=0;k<512;++k)acc+=((int32_t)input[k]-iz)*(int32_t)weights[c*512+k];
        int shift=31-shifts[c];
        int64_t product=(int64_t)acc*multipliers[c];
        int32_t value=(int32_t)((product+((int64_t)1<<(shift-1)))>>shift);
        output[c]=clip(value+oz,-128,127);
    }
}
#if defined(SCOPE_FC)
#include "operators_fc.inc"
#elif defined(SCOPE_BLOCK)
#include "operators_block.inc"
#else
#include "operators.inc"
#endif
