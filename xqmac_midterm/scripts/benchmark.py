#!/usr/bin/env python3
"""Portable single-repository bare-metal benchmark: FC micro, block or full."""
import argparse,json,os,shutil,subprocess,time
from pathlib import Path
from prepare import ROOT,prepare,digest
def run(config,scope,case,build_only=False):
    assets=ROOT/'model/assets';work=ROOT/'workload';isa=ROOT/'isa';plan=prepare(assets)
    allops=plan['manifest']['operators'];ids=list(range(37)) if scope=='full' else [5,6,7] if scope=='block' else [36]
    plan['manifest']['operators']=[o for o in allops if o['index'] in ids]
    plan['manifest']['dense_macs']=sum(o['dense_macs'] for o in plan['manifest']['operators'])
    plan['manifest']['executed_macs']=sum(o['executed_macs'] for o in plan['manifest']['operators'])
    if scope=='fc':plan['manifest']['arena_bytes']=1536
    name=['random','real_zero','maximum'][case];tag=scope+'_'+config+'_'+name
    b=ROOT/'build'/tag;d=ROOT/'results'/tag;b.mkdir(parents=True,exist_ok=True);d.mkdir(parents=True,exist_ok=True)
    for f in ['metrics.json','operators.csv','exit_status.txt']:
        p=d/f
        if p.exists():p.unlink()
    def tool(n):
        p=shutil.which(n)
        if not p:raise ValueError('Missing '+n+'; see README environment setup')
        return p
    cc=tool('riscv64-unknown-elf-gcc');spike=tool(os.environ.get('SPIKE_BIN','spike'))
    assert digest(spike)==plan['unit_spike_sha256'],'Spike changed since scripts/run_unit.py'
    flags=['-march=rv64imc','-mabi=lp64','-mcmodel=medany','-msmall-data-limit=0','-O2','-ffreestanding','-fno-builtin','-fno-pie',
      '-fno-ipa-cp','-fno-ipa-sra','-fno-ipa-icf','-fno-unwind-tables','-fno-asynchronous-unwind-tables','-fstack-usage',
      '-DCASE_ID='+str(case),'-I'+str(assets),'-I'+str(isa)]
    if scope!='full':flags+=['-DSCOPE_'+scope.upper()]
    defines=['-DUSE_RQ'] if config=='X1_RQ' else []
    kernel=work/('kernels_'+config.lower()+'.c' if config in ['B0','B1'] else 'kernels_x1.c')
    model=work/('model.c' if scope=='full' else 'model_'+scope+'.c');elf=b/'model.elf'
    cmd=[cc]+flags+defines+['-nostdlib','-nostartfiles','-Wl,--no-relax','-Wl,-Map,'+str(b/'model.map'),
      '-T',str(work/'link.ld'),str(work/'start.S'),str(model),str(kernel),str(assets/'data.S'),'-o',str(elf)]
    print('Building '+tag+'...',flush=True);subprocess.run(cmd,cwd=assets,check=True)
    for name,args,out in [('riscv64-unknown-elf-nm',['-S','-n'],b/'symbols.txt'),('riscv64-unknown-elf-objdump',['-d','-M','no-aliases'],b/'model.dis'),('riscv64-unknown-elf-size',['-A'],d/'sections.txt')]:
        with out.open('w') as f:subprocess.run([tool(name)]+args+[str(elf)],stdout=f,check=True)
    addresses={p[-1]:int(p[0],16) for line in (b/'symbols.txt').read_text().splitlines() if len(p:=line.split())>=3}
    for symbol in ['arena']+plan['aligned_weight_symbols']:assert symbol in addresses and addresses[symbol]%4==0,symbol
    record={'configuration':config,'scope':scope,'case_name':['random','real_zero','maximum'][case],
      'gcc_version':subprocess.check_output([cc,'--version'],text=True).splitlines()[0],
      'common_compiler_flags':flags,'variant_defines':defines,'spike_sha256':digest(spike),
      'plugin_sha256':plan['plugin_sha256'] if config.startswith('X1') else None,
      'enabled_extension':'xqmac_v0.3' if config.startswith('X1') else None,
      'fixture_sha256':digest(assets/'fixtures'/(['random','real_zero','maximum'][case]+'.bin')),
      'model_constants_sha256':digest(assets/'model_constants.bin'),'kernel_sha256':digest(kernel),'harness_sha256':digest(model),
      'elf_sha256':digest(elf),'rgb_version':'v2 runtime packing; all preprocessing inside op02' if config.startswith('X1') else 'original scalar',
      'input_note':'Reference boundary activation for isolated FC/block' if scope!='full' else 'Full model consumes actual C producer outputs'}
    (d/'run.json').write_text(json.dumps(record,indent=2)+'\n');(d/'build_command.json').write_text(json.dumps(cmd,indent=2)+'\n')
    if build_only:return
    sim=[tool('timeout'),os.environ.get('TIMEOUT_SEC','7200')+'s',spike]
    if config.startswith('X1'):sim+=['--extlib='+plan['plugin'],'--extension=xqmac']
    sim+=['--isa=rv64imc','-p1','-m128','-g',str(elf)]
    print('Running '+tag+'; PC histogram, not cycle timing. Wait for completion...',flush=True);start=time.monotonic()
    with (b/'stdout.log').open('w') as out,(b/'spike.hist').open('w') as err:status=subprocess.run(sim,stdout=out,stderr=err).returncode
    record['simulator_wall_seconds']=time.monotonic()-start;(d/'run.json').write_text(json.dumps(record,indent=2)+'\n');(d/'exit_status.txt').write_text(str(status)+'\n')
    if status:raise ValueError('Spike status '+str(status)+'; inspect '+str(b/'spike.hist')+' (124=timeout)')
    from profile_histogram import analyze
    r=analyze((b/'spike.hist').read_text(),(b/'symbols.txt').read_text(),(b/'model.dis').read_text(),plan['manifest'])
    counts={k:0 for k in ['qmac4.ss','qmac4.us','qrequant.dr','qrequant.sr']}
    for op in r['operators']:
        got={k:op['mnemonics'].get(k,0) for k in counts};want=plan['expected_per_operator'][op['symbol']].copy()
        if config in ['B0','B1']:want={k:0 for k in counts}
        elif config=='X1_MAC':want['qrequant.dr']=want['qrequant.sr']=0
        assert got==want,op['symbol']+' wrong custom counts'
        op['custom_dynamic_counts']=got
        for k in counts:counts[k]+=got[k]
        print('PASS op {:02d} {}: {} outputs matched LiteRT.'.format(op['index'],op['kind'],op['output_elements']))
    r.update(configuration=config,run=record,correctness={'all_selected_operators_exact':True,'checked_operators':len(ids),'checked_elements':sum(o['output_elements'] for o in r['operators'])},
      custom_dynamic_counts=counts,custom_dynamic_total=sum(counts.values()),custom_instruction_utilization=sum(counts.values())/r['dynamic_instructions'],
      dynamic_memory_instructions=r['instruction_mix'].get('load',0)+r['instruction_mix'].get('store',0),
      measurement='Sum inside selected operator symbols, including prologue/return, runtime packing, correction, tails, spills and rounding. Excludes startup, fixture setup, dispatch and golden checks. Not whole-ELF instructions or cycles.')
    r['mac_coverage_by_custom_instructions']=4*(counts['qmac4.ss']+counts['qmac4.us'])/r['executed_macs']
    (d/'metrics.json').write_text(json.dumps(r,indent=2)+'\n')
    import csv
    with (d/'operators.csv').open('w',newline='') as f:
        fields=['index','kind','symbol','dynamic_instructions','instruction_share','code_bytes','executed_macs'];w=csv.DictWriter(f,fieldnames=fields,extrasaction='ignore');w.writeheader();w.writerows(r['operators'])
    print('PASS '+tag+': '+str(r['dynamic_instructions'])+' operator instructions; custom='+repr(counts))
    print('Saved:',d/'metrics.json')
if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--config',choices=['B0','B1','X1_MAC','X1_RQ'],default='X1_RQ');p.add_argument('--scope',choices=['fc','block','full'],default='full');p.add_argument('--case',type=int,choices=[0,1,2],default=0);p.add_argument('--build-only',action='store_true');a=p.parse_args()
    try:run(a.config,a.scope,a.case,a.build_only)
    except (ValueError,AssertionError,subprocess.CalledProcessError) as e:raise SystemExit('ERROR: '+str(e))
