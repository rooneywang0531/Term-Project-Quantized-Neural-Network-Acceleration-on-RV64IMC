#include <stdio.h>
#include "rq_semantics.h"
#include "rq_vectors.h"
/* Original scalar function, independent of plugin magnitude formulation. */
static int32_t original(int32_t x,int32_t m,unsigned exponent)
{
    int64_t product=(int64_t)x*m;
    int64_t nudge=product>=0?((int64_t)1<<30):1-((int64_t)1<<30);
    int32_t high=(int32_t)((product+nudge)/((int64_t)1<<31));
    if(!exponent)return high;
    uint32_t mask=((uint32_t)1<<exponent)-1;
    uint32_t remainder=(uint32_t)high&mask;
    uint32_t threshold=(mask>>1)+(high<0);
    return (high>>exponent)+(remainder>threshold);
}
int main(void)
{
    for(unsigned i=0;i<RQ_VECTOR_COUNT;++i){
        const struct rq_vector *v=&rq_vectors[i];
        if(!rq_valid(v->m,v->r) || rq_ref(v->x,v->m,v->r)!=v->expected ||
          (uint64_t)(int64_t)original((int32_t)v->x,(int32_t)v->m,(uint32_t)v->r)!=v->expected){printf("FAIL %u\n",i);return 1;}
    }
    if(rq_valid(0x80000000,0)||rq_valid(1,32))return 2;
    puts("PASS: Python oracle, original scalar C and portable plugin semantics.");return 0;
}
