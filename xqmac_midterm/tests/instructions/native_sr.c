#include <stdio.h>
#include "rq_semantics.h"
#include "sr_vectors.h"
int main(void)
{
    for(unsigned i=0;i<SR_VECTOR_COUNT;++i){
        const struct sr_vector *v=&sr_vectors[i];
        int64_t x=(int32_t)v->x,m=(uint32_t)v->m;
        unsigned r=(uint32_t)v->r;
        uint64_t original=(uint64_t)((x*m+((int64_t)1<<(r-1)))>>r);
        if(!sr_valid(v->m,v->r)||sr_ref(v->x,v->m,v->r)!=v->expected||original!=v->expected){printf("FAIL SR %u\n",i);return 1;}
    }
    if(sr_valid(1,30)||sr_valid(1,63)||sr_valid(0x80000000,31))return 2;
    puts("PASS: SR Python oracle, original C and portable instruction semantics.");return 0;
}
