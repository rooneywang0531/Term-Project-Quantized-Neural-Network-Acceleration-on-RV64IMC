#!/usr/bin/env python3
"""Build an out-of-tree plugin against the installed Spike's ORIGINAL source/build.
Never edits Spike, never guesses an unsupported API, never installs over B0 Spike.
"""
import argparse,hashlib,json,os,re,subprocess
from pathlib import Path

def build(src,builddir,cxx,outdir):
    root=Path(__file__).resolve().parent;out=outdir;out.mkdir(parents=True,exist_ok=True)
    ext=(src/'riscv/extension.h').read_text();proc=(src/'riscv/processor.h').read_text()
    body=re.search(r'struct insn_desc_t\s*\{(.*?)\n\};',proc,re.S)
    if not body:raise SystemExit('Unsupported Spike insn_desc_t layout; supply headers for review')
    fields=re.findall(r'insn_func_t\s+(\w+)\s*;',body[1])
    if not fields or any(not any(x in f for x in ('rv32','rv64')) for f in fields):raise SystemExit('Unsupported Spike function slots: '+repr(fields))
    def signature(method):
        m=re.search(r'virtual\s+std::vector<[^\n]+>\s+'+method+r'\(([^)]*)\)',ext)
        if not m:raise SystemExit('Unsupported Spike extension signature: '+method)
        args=m[1].split('=')[0].strip()
        if args and 'processor_t' not in args:raise SystemExit('Unsupported argument list: '+args)
        return method+'('+args+') override'
    lines=['std::vector<insn_desc_t> '+signature('get_instructions')+' {','    return {']
    for name,match in [('ss',0x0b),('us',0x100b),('rq',0x2b),('sr',0x102b)]:
        callbacks=[]
        for f in fields:
            callbacks.append('unavailable' if 'rv32' in f or 'rv64e' in f else name+('_logged' if 'logged' in f else '_fast'))
        lines.append('        {0x%08x, 0x0600707f, %s},'%(match,', '.join(callbacks)))
    lines+=['    };','}', 'std::vector<disasm_insn_t *> '+signature('get_disasms')+' {','    return {',
            '        new disasm_insn_t("qmac4.ss", 0x0000000b, 0x0600707f, {&arg_rd,&arg_a,&arg_w,&arg_acc}),',
            '        new disasm_insn_t("qmac4.us", 0x0000100b, 0x0600707f, {&arg_rd,&arg_a,&arg_w,&arg_acc}),','        new disasm_insn_t("qrequant.dr", 0x0000002b, 0x0600707f, {&arg_rd,&arg_a,&arg_w,&arg_acc}),','        new disasm_insn_t("qrequant.sr", 0x0000102b, 0x0600707f, {&arg_rd,&arg_a,&arg_w,&arg_acc}),','    };','}']
    (out/'spike_adapter.inc').write_text('\n'.join(lines)+'\n')
    includes=[root,out,src,builddir,src/'riscv',src/'disasm',src/'fesvr',src/'softfloat']
    cmd=[cxx,'-std=c++17','-O2','-fPIC','-shared','-Wall','-Wextra','-Wno-unused-parameter']
    for inc in includes:cmd+=['-I',str(inc)]
    cmd+=[str(root/'spike_extension.cc'),'-o',str(out/'libxqmac.so')]
    print('Building plugin from matching Spike headers:',src,flush=True);subprocess.run(cmd,check=True)
    try:rev=subprocess.check_output(['git','-C',str(src),'rev-parse','HEAD'],universal_newlines=True).strip()
    except subprocess.CalledProcessError:rev='not a git checkout'
    info={'spike_source':str(src),'spike_build':str(builddir),'source_revision':rev,'insn_function_slots':fields,'compiler_command':cmd,
          'compiler_version':subprocess.check_output([cxx,'--version'],universal_newlines=True).splitlines()[0],
          'library_sha256':hashlib.sha256((out/'libxqmac.so').read_bytes()).hexdigest()}
    (out/'extension_build.json').write_text(json.dumps(info,indent=2)+'\n')
    print('Built:',out/'libxqmac.so')
if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--source',type=Path,default=Path(os.environ.get('SPIKE_SRC',str(Path(__file__).resolve().parents[1]/'.deps/spike'))));p.add_argument('--build',type=Path,default=Path(os.environ['SPIKE_BUILD']) if 'SPIKE_BUILD' in os.environ else None);p.add_argument('--output',type=Path,default=Path(__file__).resolve().parents[1]/'build/unit');p.add_argument('--cxx',default=os.environ.get('CXX','g++'));a=p.parse_args();src=a.source.resolve();build(src,(a.build or src/'build').resolve(),a.cxx,a.output.resolve())
