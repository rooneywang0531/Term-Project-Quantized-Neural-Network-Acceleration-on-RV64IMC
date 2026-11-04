#!/usr/bin/env python3
"""Build against matching Spike headers; independent RQ and prior MAC regression."""
import hashlib,json,os,re,shutil,subprocess,sys
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
R=ROOT/'tests/instructions'
sys.path.insert(0,str(R))
from native_check import validate_native
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def histogram_counts(dis,hist):
    ins={int(m[1],16):int(m[2],16) for m in re.finditer(r'^\s*([0-9a-fA-F]+):\s+([0-9a-fA-F]{4,8})\s+',dis,re.M)}
    expected=None;freq={}
    for line in hist.splitlines():
        if line.startswith('PC Histogram size:'):
            if expected is not None:raise ValueError('Multiple histograms')
            expected=int(line.split(':')[1]);continue
        if expected is not None:
            m=re.fullmatch(r'\s*(?:0x)?([0-9a-fA-F]+)\s+(\d+)\s*',line)
            if m:
                pc,n=int(m[1],16),int(m[2]);assert pc not in freq and n>0;freq[pc]=n
    assert expected is not None and len(freq)==expected,'Incomplete histogram'
    counts={'qmac4.ss':0,'qmac4.us':0,'qrequant.dr':0,'qrequant.sr':0}
    codes={0xb:'qmac4.ss',0x100b:'qmac4.us',0x2b:'qrequant.dr',0x102b:'qrequant.sr'}
    for pc,n in freq.items():
        if pc in ins:
            match=ins[pc]&0x0600707f
            if match in codes:counts[codes[match]]+=n
    return counts
def main():
    for host_tool in ['dtc','timeout']:
        if not shutil.which(host_tool):raise SystemExit('Missing host tool '+host_tool+'; install README setup dependencies or fix PATH.')
    os.chdir(R);b=ROOT/'build/unit';d=ROOT/'results/unit';b.mkdir(parents=True,exist_ok=True);d.mkdir(parents=True,exist_ok=True)
    for n in ['unit_metrics.json','unit_pass.json']:
        p=d/n
        if p.exists():p.unlink()
    def run(cmd,**kw):return subprocess.run([str(x) for x in cmd],check=True,**kw)
    run([sys.executable,R/'generate_tests.py']);run([sys.executable,R/'generate_sr.py']);run([sys.executable,ROOT/'isa/build_extension.py','--output',b])
    cc=shutil.which('riscv64-unknown-elf-gcc');obj=shutil.which('riscv64-unknown-elf-objdump')
    spike=shutil.which(os.environ.get('SPIKE_BIN','spike'))
    if not cc or not obj or not spike:raise SystemExit('Missing RISC-V compiler, objdump or Spike')
    plugin=b/'libxqmac.so'
    flags=['-march=rv64imc','-mabi=lp64','-mcmodel=medany','-msmall-data-limit=0','-O2','-ffreestanding','-fno-builtin','-fno-pie',
      '-fno-ipa-cp','-fno-ipa-sra','-fno-ipa-icf','-fno-unwind-tables','-fno-asynchronous-unwind-tables',
      '-nostdlib','-nostartfiles','-Wl,--no-relax','-I'+str(R),'-I'+str(ROOT/'isa'),'-T',str(R/'link.ld')]
    ext=['--extlib='+str(plugin),'--extension=xqmac','--isa=rv64imc','-p1','-m64']
    def compile_elf(name,sources,extra=()):
        elf=b/(name+'.elf');run([cc]+flags+list(extra)+[str(x) for x in sources]+['-o',elf]);return elf
    def simulate(name,elf,extra=(),extension=True,success=True):
        cmd=['timeout','120s',spike]+(ext if extension else ['--isa=rv64imc','-m64'])+list(extra)+[str(elf)]
        with (b/(name+'.stdout')).open('w') as out,(b/(name+'.log')).open('w') as err:
            status=subprocess.run(cmd,stdout=out,stderr=err).returncode
        if success and status:raise ValueError(name+' failed, status='+str(status)+'; see build/'+name+'.log')
        if not success:
            assert status!=124 and 'trap_illegal_instruction' in (b/(name+'.log')).read_text(),name+' did not trap'
        return status
    native=validate_native(R,b)
    elf=compile_elf('rq_unit',[R/'start.S',R/'rq_unit.c',R/'rq_alias.S'])
    with (b/'rq_unit.dis').open('w') as f:run([obj,'-d','-M','no-aliases',elf],stdout=f)
    simulate('rq_unit',elf,['-g'])
    meta=json.loads((R/'rq_vectors.json').read_text())
    counts=histogram_counts((b/'rq_unit.dis').read_text(),(b/'rq_unit.log').read_text())
    assert counts=={'qmac4.ss':0,'qmac4.us':0,'qrequant.dr':meta['expected_rq_count'],'qrequant.sr':0},counts
    print('PASS:',meta['vectors'],'RQ vectors;',meta['alias_calls'],'explicit alias/x0 calls;',counts,flush=True)
    probe=compile_elf('rq_probe',[R/'rq_probe.S'])
    simulate('rq_logged',probe,['--log-commits','-l'])
    log=(b/'rq_logged.log').read_text();assert 'qrequant.dr' in log
    # The result of -3 * 0.5, then /2 with both original roundings, is -1.
    assert re.search(r'x\s*10\s+0xffffffffffffffff',log),'Logged rd result missing'
    negatives={}
    negatives['extension_absent']=simulate('no_extension',probe,['--instructions=80','-l'],extension=False,success=False)
    for key in ['SHIFT','MULT','FUNCT2','FUNCT3']:
        elf=compile_elf('bad_'+key.lower(),[R/'rq_probe.S'],['-DBAD_'+key])
        negatives[key.lower()]=simulate('bad_'+key.lower(),elf,['--instructions=80','-l'],success=False)
    print('PASS: RQ logged result, missing extension, illegal operands and reserved encoding traps.',flush=True)
    native_sr=validate_native(R,b,source='native_sr.c',name='native_sr')
    srmeta=json.loads((R/'sr_vectors.json').read_text())
    srunit=compile_elf('sr_unit',[R/'start.S',R/'sr_unit.c',R/'sr_alias.S'])
    with (b/'sr_unit.dis').open('w') as f:run([obj,'-d','-M','no-aliases',srunit],stdout=f)
    simulate('sr_unit',srunit,['-g'])
    srcounts=histogram_counts((b/'sr_unit.dis').read_text(),(b/'sr_unit.log').read_text())
    assert srcounts=={'qmac4.ss':0,'qmac4.us':0,'qrequant.dr':0,'qrequant.sr':srmeta['expected_sr_count']},srcounts
    srprobe=compile_elf('sr_probe',[R/'sr_probe.S'])
    simulate('sr_logged',srprobe,['--log-commits','-l'])
    srlog=(b/'sr_logged.log').read_text()
    assert 'qrequant.sr' in srlog and re.search(r'x\s*10\s+0xffffffffffffffff',srlog)
    negatives['sr_extension_absent']=simulate('sr_noext',srprobe,['--instructions=80','-l'],extension=False,success=False)
    for key in ['SHIFT','HIGH_SHIFT','MULT','FUNCT2','FUNCT3']:
        elf=compile_elf('sr_bad_'+key.lower(),[R/'sr_probe.S'],['-DBAD_'+key])
        negatives['sr_'+key.lower()]=simulate('sr_bad_'+key.lower(),elf,['--instructions=80','-l'],success=False)
    print('PASS:',srmeta['vectors'],'SR vectors;',srmeta['alias_calls'],'alias/x0 calls;',srcounts,flush=True)
    # Re-run original MAC vectors and alias suite against the NEW combined plugin.
    stage=ROOT/'tests/mac'
    run([sys.executable,stage/'gen_vectors.py'])
    elf=compile_elf('mac_regression',[stage/'start.S',stage/'unit_test.c',stage/'alias_tests.S'],['-I'+str(stage)])
    with (b/'mac_regression.dis').open('w') as f:run([obj,'-d','-M','no-aliases',elf],stdout=f)
    simulate('mac_regression',elf,['-g'])
    mac=histogram_counts((b/'mac_regression.dis').read_text(),(b/'mac_regression.log').read_text())
    assert mac=={'qmac4.ss':19072,'qmac4.us':9952,'qrequant.dr':0,'qrequant.sr':0},mac
    p=compile_elf('mac_probe',[stage/'negative_probe.S'])
    simulate('mac_logged',p,['--log-commits','-l'])
    assert all(x in (b/'mac_logged.log').read_text() for x in ['qmac4.ss','qmac4.us'])
    for key in ['BAD_ENCODING','BAD_FUNCT2']:
        p=compile_elf('mac_'+key,[stage/'negative_probe.S'],['-D'+key])
        negatives['mac_'+key]=simulate('mac_'+key,p,['--instructions=80','-l'],success=False)
    result={'correctness':'PASS','native_validation':native,'native_sr_validation':native_sr,'sr_vectors':srmeta['vectors'],'sr_alias_calls':srmeta['alias_calls'],'sr_custom_counts':srcounts,'scope':'unit tests only, not model performance','vectors':meta['vectors'],
      'alias_calls':meta['alias_calls'],'rq_custom_counts':counts,'mac_regression_counts':mac,'negative_tests':negatives,
      'plugin_sha256':sha(plugin),'spike_sha256':sha(spike),
      'gcc_version':subprocess.check_output([cc,'--version'],text=True).splitlines()[0],
      'tested_source_sha256':{str(p.relative_to(ROOT)):sha(p) for folder in [ROOT/'isa',ROOT/'tests/instructions',ROOT/'tests/mac'] for p in sorted(folder.iterdir()) if p.is_file() and p.suffix in ['.py','.h','.c','.cc','.S','.json']}}
    (d/'unit_metrics.json').write_text(json.dumps(result,indent=2)+'\n')
    (d/'unit_pass.json').write_text(json.dumps(result,indent=2)+'\n')
    print('PASS: prior MAC semantics, aliases, logged paths and reserved encodings. Combined plugin ready.')
if __name__=='__main__':
    try:main()
    except (ValueError,AssertionError,subprocess.CalledProcessError) as e:raise SystemExit('ERROR: '+str(e))
