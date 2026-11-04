#!/usr/bin/env python3
import argparse,json
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
def main(scope,case):
    rows=[json.loads((ROOT/'results'/(scope+'_'+c+'_'+case)/'metrics.json').read_text()) for c in ['B0','B1','X1_MAC','X1_RQ']]
    for r in rows:
        assert r['correctness']==rows[0]['correctness'] and r['correctness']['all_selected_operators_exact']
        for k in ['scope','case_name','gcc_version','common_compiler_flags','spike_sha256','fixture_sha256','model_constants_sha256','harness_sha256']:assert r['run'][k]==rows[0]['run'][k],k
        assert r['dense_macs']==rows[0]['dense_macs'] and r['executed_macs']==rows[0]['executed_macs']
    assert rows[2]['run']['plugin_sha256']==rows[3]['run']['plugin_sha256']
    assert rows[2]['run']['kernel_sha256']==rows[3]['run']['kernel_sha256']
    text=['# '+scope+' four-configuration comparison','',rows[0]['measurement'],'',
      '| Metric | B0 | B1 | X1_MAC | X1_RQ |','|---|---:|---:|---:|---:|']
    for k in ['dynamic_instructions','operator_code_bytes','dynamic_memory_instructions','custom_dynamic_total','custom_instruction_utilization','dense_mac_per_instruction','executed_mac_per_instruction','mac_coverage_by_custom_instructions']:
        text.append('| '+k+' | '+' | '.join(str(r[k]) for r in rows)+' |')
    for k in sorted(set().union(*(r['instruction_mix'] for r in rows))):text.append('| '+k+' | '+' | '.join(str(r['instruction_mix'].get(k,0)) for r in rows)+' |')
    text+=['','| Operator | B0 | B1 | X1_MAC | X1_RQ |','|---|---:|---:|---:|---:|']
    for i,o in enumerate(rows[0]['operators']):text.append('| '+o['symbol']+' | '+' | '.join(str(r['operators'][i]['dynamic_instructions']) for r in rows)+' |')
    ratio=rows[1]['dynamic_instructions']/rows[3]['dynamic_instructions'];text+=['','B1 / X1_RQ instruction-count ratio: {:.3f}x.'.format(ratio),
      'Not a cycle or wall-time speedup. No CV-Wally/PPA claim.']
    if scope=='fc':text+=['FC microbenchmark: 512 inputs, 1000 outputs, 512000 model MACs. >=2x dynamic-instruction target: '+('PASS' if ratio>=2 else 'NOT MET')]
    out=ROOT/'results'/('comparison_'+scope+'_'+case+'.md');out.write_text('\n'.join(text)+'\n');print(out.read_text())
if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('scope',choices=['fc','block','full']);p.add_argument('--case',choices=['random','real_zero','maximum'],default='random');a=p.parse_args();main(a.scope,a.case)
