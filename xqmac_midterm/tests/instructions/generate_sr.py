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
    assert m<1<<31 and 31<=r<=62
    return ((x*m+(1<<(r-1)))>>r)&MASK
ALIASES=[('t0','a0','a1','a2'),('a0','a0','a1','a2'),
 ('a1','a0','a1','a2'),('a2','a0','a1','a2'),('zero','a0','a1','a2'),
 ('t0','zero','a1','a2'),('t0','a0','zero','a2'),('t0','a0','a1','zero'),
 ('t0','a0','a0','a2'),('t0','a0','a1','a1'),('t0','a2','a1','a2'),
 ('a0','a0','a0','a0')]
def generate():
    rng=random.Random(20261104)
    xs=[-(1<<31),(1<<31)-1,-(1<<30),1<<30,-65537,-65536,-3,-2,-1,0,1,2,3,65535,65536]
    ms=[0,1,2,3,(1<<30)-1,1<<30,(1<<30)+1,(1<<31)-1]
    triples={(x,m,r) for x in xs for m in ms for r in range(31,63)}
    # Single-rounding ties and adjacent x for power-of-two multipliers.
    for r in range(31,63):
        for m in [1,1<<30]:
            for k in [0,1,3]:
                for sign in [-1,1]:
                    center=sign*((k<<r)+(1<<(r-1)))//m
                    for delta in [-1,0,1]:
                        x=center+delta
                        if -(1<<31)<=x<(1<<31):triples.add((x,m,r))
    for _ in range(8192):triples.add((rng.randrange(-(1<<31),1<<31),rng.randrange(1<<31),rng.randrange(31,63)))
    lines=['#include <stdint.h>','struct sr_vector { uint64_t x,m,r,expected; };',
           'static const struct sr_vector sr_vectors[]={']
    def row(values):return '{'+','.join('UINT64_C(0x%016x)'%(v&MASK) for v in values)+'},'
    for x,m,r in sorted(triples):
        raw=[(rng.getrandbits(32)<<32)|(v&0xffffffff) for v in [x,m,r]]
        lines.append(row(raw+[oracle(x,m,r)]))
    lines+=['};','#define SR_VECTOR_COUNT %d'%len(triples)]
    assembly=['.text']
    for i,(rd,a,m,r) in enumerate(ALIASES):
        assembly+=['.globl sr_alias_%d'%i,'sr_alias_%d:'%i,
          '    .insn r4 0x2b, 1, 0, %s, %s, %s, %s'%(rd,a,m,r),'    mv a0, '+rd,'    ret']
    (ROOT/'sr_alias.S').write_text('\n'.join(assembly)+'\n')
    for i in range(len(ALIASES)):lines.append('extern uint64_t sr_alias_%d(uint64_t,uint64_t,uint64_t);'%i)
    lines+=['static uint64_t (*const sr_aliases[])(uint64_t,uint64_t,uint64_t)={'+','.join('sr_alias_%d'%i for i in range(len(ALIASES)))+'};',
      'struct sr_alias_vector { uint64_t x,m,r,expected; unsigned kind; };',
      'static const struct sr_alias_vector sr_alias_vectors[]={']
    n_alias=0
    candidates=[(-2147483648,2147483647,62),(2147483647,1073741824,31),(-3,1073741824,31),(0,0,31)]+[(x,m,r) for x in [0,1,31,32,62] for m in [0,1,31,62] for r in [31,32,47,62]]
    for x,m,r in candidates:
        regs={'zero':0,'a0':(rng.getrandbits(32)<<32)|(x&0xffffffff),
          'a1':(rng.getrandbits(32)<<32)|m,'a2':(rng.getrandbits(32)<<32)|r}
        for i,(rd,a,b,c) in enumerate(ALIASES):
            if regs[b]&0xffffffff>=1<<31 or not 31<=regs[c]&0xffffffff<=62:continue
            expected=0 if rd=='zero' else oracle(regs[a],regs[b],regs[c])
            vals=[regs['a0'],regs['a1'],regs['a2'],expected]
            lines.append('{'+','.join('UINT64_C(0x%016x)'%v for v in vals)+',%d},'%i);n_alias+=1
    lines+=['};','#define SR_ALIAS_VECTOR_COUNT %d'%n_alias]
    (ROOT/'sr_vectors.h').write_text('\n'.join(lines)+'\n')
    meta={'oracle':'Python unbounded (x*m + 2**(r-1)) // 2**r, single rounding ties toward +infinity',
      'seed':20261104,'vectors':len(triples),'alias_calls':n_alias,'expected_sr_count':2*len(triples)+n_alias,'alias_cases':ALIASES}
    (ROOT/'sr_vectors.json').write_text(json.dumps(meta,indent=2)+'\n')
    print('Generated',len(triples),'SR vectors and',n_alias,'alias/x0 calls')
if __name__=='__main__':generate()
