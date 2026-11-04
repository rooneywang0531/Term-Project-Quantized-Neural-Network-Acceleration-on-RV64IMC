#!/usr/bin/env python3
"""Independent Python oracle using the original signed nudge/floor formulation."""
import json, random
from pathlib import Path
ROOT=Path(__file__).resolve().parent
MASK=(1<<64)-1
def signed(x):
    x=x&0xffffffff
    return x if x<1<<31 else x-(1<<32)
def oracle(x,m,r):
    x=signed(x);m=m&0xffffffff;r=r&0xffffffff
    assert m<1<<31 and r<=31
    p=x*m;nudge=(1<<30) if p>=0 else 1-(1<<30)
    n=p+nudge
    high=abs(n)//(1<<31)*(-1 if n<0 else 1)
    if r:
        mask=(1<<r)-1;threshold=(mask>>1)+(high<0)
        high=(high>>r)+((high&mask)>threshold)
    return high&MASK
ALIASES=[('t0','a0','a1','a2'),('a0','a0','a1','a2'),
 ('a1','a0','a1','a2'),('a2','a0','a1','a2'),('zero','a0','a1','a2'),
 ('t0','zero','a1','a2'),('t0','a0','zero','a2'),('t0','a0','a1','zero'),
 ('t0','a0','a0','a2'),('t0','a0','a1','a1'),('t0','a2','a1','a2'),
 ('a0','a0','a0','a0')]
def generate():
    rng=random.Random(20261104)
    xs=[-(1<<31),(1<<31)-1,-(1<<30),1<<30,-65537,-65536,-3,-2,-1,0,1,2,3,65535,65536]
    ms=[0,1,2,3,(1<<30)-1,1<<30,(1<<30)+1,(1<<31)-1]
    triples={(x,m,r) for x in xs for m in ms for r in range(32)}
    # Force second-rounding ties and neighbours with multiplier=2^30.
    for r in range(1,31):
        for k in [0,1,3]:
            for sign in [-1,1]:
                for delta in [-1,0,1]:
                    x=sign*((k<<r)+(1<<(r-1)))*2+delta
                    if -(1<<31)<=x<(1<<31):triples.add((x,1<<30,r))
    for _ in range(8192):triples.add((rng.randrange(-(1<<31),1<<31),rng.randrange(1<<31),rng.randrange(32)))
    lines=['#include <stdint.h>','struct rq_vector { uint64_t x,m,r,expected; };',
           'static const struct rq_vector rq_vectors[]={']
    def row(values):return '{'+','.join('UINT64_C(0x%016x)'%(v&MASK) for v in values)+'},'
    for x,m,r in sorted(triples):
        raw=[(rng.getrandbits(32)<<32)|(v&0xffffffff) for v in [x,m,r]]
        lines.append(row(raw+[oracle(x,m,r)]))
    lines+=['};','#define RQ_VECTOR_COUNT %d'%len(triples)]
    assembly=['.text']
    for i,(rd,a,m,r) in enumerate(ALIASES):
        assembly+=['.globl rq_alias_%d'%i,'rq_alias_%d:'%i,
          '    .insn r4 0x2b, 0, 0, %s, %s, %s, %s'%(rd,a,m,r),'    mv a0, '+rd,'    ret']
    (ROOT/'rq_alias.S').write_text('\n'.join(assembly)+'\n')
    for i in range(len(ALIASES)):lines.append('extern uint64_t rq_alias_%d(uint64_t,uint64_t,uint64_t);'%i)
    lines+=['static uint64_t (*const rq_aliases[])(uint64_t,uint64_t,uint64_t)={'+','.join('rq_alias_%d'%i for i in range(len(ALIASES)))+'};',
      'struct alias_vector { uint64_t x,m,r,expected; unsigned kind; };',
      'static const struct alias_vector alias_vectors[]={']
    n_alias=0
    candidates=[(-2147483648,2147483647,31),(2147483647,1073741824,0),(-3,1073741824,1),(0,0,0)]+[(x,m,r) for x in [0,1,2,15,31] for m in [0,1,15,31] for r in [0,1,15,31]]
    for x,m,r in candidates:
        regs={'zero':0,'a0':(rng.getrandbits(32)<<32)|(x&0xffffffff),
          'a1':(rng.getrandbits(32)<<32)|m,'a2':(rng.getrandbits(32)<<32)|r}
        for i,(rd,a,b,c) in enumerate(ALIASES):
            if regs[b]&0xffffffff>=1<<31 or regs[c]&0xffffffff>31:continue
            expected=0 if rd=='zero' else oracle(regs[a],regs[b],regs[c])
            vals=[regs['a0'],regs['a1'],regs['a2'],expected]
            lines.append('{'+','.join('UINT64_C(0x%016x)'%v for v in vals)+',%d},'%i);n_alias+=1
    lines+=['};','#define ALIAS_VECTOR_COUNT %d'%n_alias]
    (ROOT/'rq_vectors.h').write_text('\n'.join(lines)+'\n')
    meta={'oracle':'original C nudge, signed truncating divide, arithmetic shift and remainder threshold; Python unbounded integers',
      'seed':20261104,'vectors':len(triples),'alias_calls':n_alias,'expected_rq_count':2*len(triples)+n_alias,'alias_cases':ALIASES}
    (ROOT/'rq_vectors.json').write_text(json.dumps(meta,indent=2)+'\n')
    print('Generated',len(triples),'RQ vectors and',n_alias,'alias/x0 calls')
if __name__=='__main__':generate()
