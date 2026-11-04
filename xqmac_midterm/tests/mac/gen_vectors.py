#!/usr/bin/env python3
"""Independent Python integer oracle; target C never uses the plugin helper."""
import json,random
from pathlib import Path
ROOT=Path(__file__).resolve().parent
MASK=(1<<32)-1
NAMES=['rd_a','rd_w','rd_acc','a_w','acc_a','acc_w','all_a','rd_zero','all_zero','rd_separate','a_zero','w_zero','acc_zero']
def signed8(x):return x-256 if x>=128 else x
def sext(x):
 x&=MASK
 return x|0xffffffff00000000 if x&0x80000000 else x

def oracle(a,w,c,us=False,zp=None):
 dot=0
 for i in range(4):
  aa=(a>>(8*i))&255;ww=signed8((w>>(8*i))&255)
  av=signed8(aa)-zp if zp is not None else aa if us else signed8(aa)
  dot+=av*ww
 return sext(c+dot)

def alias(a,w,c,kind,us):
 if kind=='a_w':w=a
 elif kind=='acc_a':c=a
 elif kind=='acc_w':c=w
 elif kind=='all_a':w=c=a
 elif kind=='rd_zero':return 0
 elif kind=='all_zero':a=w=c=0
 elif kind=='a_zero':a=0
 elif kind=='w_zero':w=0
 elif kind=='acc_zero':c=0
 return oracle(a,w,c,us)

def main():
 values=[0,0x01010101,0x7f7f7f7f,0x80808080,0xffffffff,0x807fff01,0x010080ff,0x80000000]
 accs=[0,1,0xffffffff,0x7fffffff,0x80000000,0x1234567887654321,0xffffffff00000000]
 rows=[(a,w,c) for a in values for w in values for c in accs]
 # Explicit lane-to-byte ordering and all lane cross-pairs.
 for i in range(4):
  for j in range(4):rows.append((0xff<<(i*8),0x80<<(j*8),0))
 rng=random.Random(20261104)
 rows += [(rng.getrandbits(64),rng.getrandbits(64),rng.getrandbits(64)) for _ in range(4096)]
 lines=['/* Generated independent Python oracle; fixed seed 20261104. */',
 '#ifndef XQMAC_VECTORS_H','#define XQMAC_VECTORS_H','#include <stdint.h>',
 'struct test_vector { uint64_t a,w,acc,ss,us,z128,z14,z127; };',
 'static const struct test_vector vectors[] = {']
 serial=[]
 for a,w,c in rows:
  row=[a,w,c,oracle(a,w,c),oracle(a,w,c,True),oracle(a,w,c,zp=-128),oracle(a,w,c,zp=-14),oracle(a,w,c,zp=127)]
  serial.append(row);lines.append('    {'+', '.join('UINT64_C(0x%016x)'%x for x in row)+'},')
 lines+=['};','#define VECTOR_COUNT (sizeof(vectors)/sizeof(vectors[0]))',
         '#define ALIAS_CASE_COUNT %d'%len(NAMES),'#define ALIAS_VECTOR_COUNT 64',
         'static const uint32_t alias_vector_indices[64] = {']
 indices=[i*(len(rows)-1)//63 for i in range(64)];lines.append(','.join(map(str,indices))+'};')
 lines+=['static const uint64_t alias_expected[64][2][ALIAS_CASE_COUNT] = {']
 for i in indices:
  a,w,c=rows[i];lines.append('    {')
  for us in (False,True):lines.append('        {'+', '.join('UINT64_C(0x%016x)'%alias(a,w,c,k,us) for k in NAMES)+'},')
  lines.append('    },')
 lines+=['};','#endif']
 (ROOT/'test_vectors.h').write_text('\n'.join(lines)+'\n')
 meta={'seed':20261104,'vector_count':len(rows),'alias_vectors':64,'alias_cases':NAMES,
       'oracle':'Python arbitrary-precision integers, explicit lane extraction, mod2^32, RV64 sign extension',
       'expected_qmac_calls':len(rows)*6+64*len(NAMES)*2}
 # 2 raw + z=-128 + z=-14 + z=0 + z=127: exactly six custom instructions/vector.
 (ROOT/'test_vectors.json').write_text(json.dumps(meta,indent=2)+'\n')
 asm=['.section .text.alias,"ax",@progbits']
 for us in (False,True):
  mode='us' if us else 'ss';funct=1 if us else 0
  forms={'rd_a':('a0','a0','a1','a2'),'rd_w':('a1','a0','a1','a2'),'rd_acc':('a2','a0','a1','a2'),
         'a_w':('t0','a0','a0','a2'),'acc_a':('t0','a0','a1','a0'),'acc_w':('t0','a0','a1','a1'),
         'all_a':('a0','a0','a0','a0'),'rd_zero':('zero','a0','a1','a2'),'all_zero':('a0','zero','zero','zero'),
         'rd_separate':('t0','a0','a1','a2'),'a_zero':('a0','zero','a1','a2'),'w_zero':('a0','a0','zero','a2'),
         'acc_zero':('a0','a0','a1','zero')}
  for kind in NAMES:
   name='alias_'+mode+'_'+kind;rd,a,w,c=forms[kind]
   asm+=['.balign 2','.globl '+name,'.type '+name+',@function',name+':',
         '    .insn r4 0x0b, %d, 0, %s, %s, %s, %s'%(funct,rd,a,w,c),'    mv a0, '+rd,'    ret','.size '+name+', .-'+name]
 asm+=['.section .note.GNU-stack,"",@progbits']
 (ROOT/'alias_tests.S').write_text('\n'.join(asm)+'\n')
 hdr=['typedef uint64_t (*alias_fn)(uint64_t,uint64_t,uint64_t);']
 for mode in ('ss','us'):
  hdr+=['extern uint64_t alias_'+mode+'_'+n+'(uint64_t,uint64_t,uint64_t);' for n in NAMES]
 hdr+=['static const alias_fn alias_functions[2][ALIAS_CASE_COUNT] = {']
 for mode in ('ss','us'):hdr.append('    {'+', '.join('alias_'+mode+'_'+n for n in NAMES)+'},')
 hdr+=['};']
 (ROOT/'alias_tests.h').write_text('\n'.join(hdr)+'\n')
 print('Generated',len(rows),'vectors;',meta['expected_qmac_calls'],'expected custom instruction executions.')
if __name__=='__main__':main()
