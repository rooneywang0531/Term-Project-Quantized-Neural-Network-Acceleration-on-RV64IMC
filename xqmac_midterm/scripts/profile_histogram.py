#!/usr/bin/env python3
"""Exact weighted PC counts for all 37 operator symbols; no giant trace file."""
import argparse,csv,json,re
from collections import Counter
from pathlib import Path
from instruction_classify import classify

def analyze(histogram,symbols,disassembly,manifest):
    ops=manifest['operators'];wanted={o['symbol'] for o in ops};ranges={}
    for line in symbols.splitlines():
        p=line.split()
        if len(p)==4 and p[3] in wanted:
            start,size=int(p[0],16),int(p[1],16)
            if not size:raise ValueError('Empty operator symbol')
            ranges[p[3]]=(start,start+size)
    if set(ranges)!=wanted:raise ValueError('Missing sized operator symbols in nm -S output')
    bounds=sorted(ranges.values())
    if any(a[1]>b[0] for a,b in zip(bounds,bounds[1:])):raise ValueError('Overlapping operator symbols')
    instructions={}
    for line in disassembly.splitlines():
        m=re.match(r'^\s*([0-9a-fA-F]+):\s+([0-9a-fA-F]{4,8})\s+(\S+)(.*)$',line)
        if m:instructions[int(m[1],16)]=(int(m[2],16),m[3],m[4].strip())
    freq={};started=False;expected=None
    for line in histogram.splitlines():
        if line.startswith('PC Histogram size:'):
            if started:raise ValueError('Expected exactly one hart histogram')
            started=True;expected=int(line.split(':',1)[1]);continue
        if started:
            m=re.fullmatch(r'\s*(?:0x)?([0-9a-fA-F]+)\s+(\d+)\s*',line)
            if m:
                pc,count=int(m[1],16),int(m[2])
                if pc in freq:raise ValueError('Duplicate PC record')
                if count<=0:raise ValueError('Nonpositive execution count')
                freq[pc]=count
    if not started or len(freq)!=expected:raise ValueError('Missing/incomplete PC histogram')
    results=[];combined=Counter();bytype=Counter()
    for op in ops:
        name=op['symbol'];start,end=ranges[name]
        if freq.get(start)!=1:raise ValueError(name+' did not enter exactly once')
        mix=Counter();mnemonics=Counter()
        for pc,count in freq.items():
            if not start<=pc<end:continue
            if pc not in instructions:raise ValueError('Missing disassembly at '+hex(pc))
            bits,mnemonic,operands=instructions[pc]
            # Functions must be self-contained, so per-operator totals are complete.
            if bits&3==3 and bits&127==0x6f:
                if ((bits>>7)&31)!=0:raise ValueError('Out-of-line call in '+name)
                target=re.match(r'(?:zero,)?\s*([0-9a-fA-F]+)\s*<',operands)
                if target and not start<=int(target[1],16)<end:raise ValueError('Tail call outside '+name)
            if mnemonic in ('jalr','c.jalr') and not (mnemonic=='jalr' and operands.replace(' ','') in ('zero,0(ra)','zero,ra,0')):
                raise ValueError('Indirect call/jump in '+name)
            if mnemonic=='c.jr' and operands!='ra':raise ValueError('Indirect compressed jump in '+name)
            if bits & 0x0600707f == 0x0000102b:
                kind='custom_requant';mnemonic='qrequant.sr'
            elif bits & 0x0600707f == 0x0000002b:
                kind='custom_requant';mnemonic='qrequant.dr'
            elif bits & 0x0600707f == 0x0000000b:
                kind='custom_mac';mnemonic='qmac4.ss'
            elif bits & 0x0600707f == 0x0000100b:
                kind='custom_mac';mnemonic='qmac4.us'
            else:
                kind=classify(bits)
            if kind in ('floating_or_vector','system','other'):raise ValueError('Unexpected '+kind+' in '+name)
            mix[kind]+=count;mnemonics[mnemonic]+=count
        total=sum(mix.values())
        if not total:raise ValueError('Empty operator histogram')
        row=dict(op);row.update(dynamic_instructions=total,code_bytes=end-start,instruction_mix=dict(sorted(mix.items())),mnemonics=dict(mnemonics.most_common()),
                              instructions_per_output=total/op['output_elements'],dense_mac_per_instruction=op['dense_macs']/total if op['dense_macs'] else None,
                              executed_mac_per_instruction=op['executed_macs']/total if op['executed_macs'] else None,
                              load_store_per_executed_mac=(mix['load']+mix['store'])/op['executed_macs'] if op['executed_macs'] else None)
        results.append(row);combined.update(mix);bytype[op['kind']]+=total
    total=sum(combined.values())
    for row in results:row['instruction_share']=row['dynamic_instructions']/total
    return {'configuration':'B0 complete static ResNet18; scalar RV64IMC O2',
            'measurement':'Sum of executed instructions inside all 37 sized operator symbols, including prologues/returns. Excludes startup, input copy, caller dispatch and validation. This is the full-model OPERATOR total, not the entire ELF or a cycle count.',
            'model_sha256':manifest['model_sha256'],'dense_macs':manifest['dense_macs'],'executed_macs':manifest['executed_macs'],
            'mac_note':manifest['mac_note'],'dynamic_instructions':total,'instruction_mix':dict(sorted(combined.items())),
            'by_operator_type':dict(bytype.most_common()),'dense_mac_per_instruction':manifest['dense_macs']/total,
            'executed_mac_per_instruction':manifest['executed_macs']/total,'operator_code_bytes':sum(r['code_bytes'] for r in results),
            'activation_arena_bytes':manifest['arena_bytes'],'operators':results,'cycle_count':None,
            'histogram_total_instructions':sum(freq.values()),
            'outside_operator_instructions':sum(freq.values())-total,
            'histogram_pc_entries':len(freq),
            'histogram_total_note':'All PCs reported by Spike, including boot, startup, fixture setup, dispatch and golden checks; not a model-only performance denominator.'}

if __name__=='__main__':
    raise SystemExit('Use python3 scripts/benchmark.py --scope fc|block|full --config B0|B1|X1_MAC|X1_RQ; this module supplies the shared analyzer.')
