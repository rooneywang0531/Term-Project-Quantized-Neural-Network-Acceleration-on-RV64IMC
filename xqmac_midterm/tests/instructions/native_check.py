"""Keep numerical validation mandatory; probe optional UBSan independently."""
import os,subprocess

def validate_native(root,build,source="native_test.c",name="native_test"):
    cc=os.environ.get('CC','gcc')
    mode=os.environ.get('NATIVE_UBSAN','auto')
    if mode not in ('auto','required','off'):
        raise ValueError('NATIVE_UBSAN must be auto, required or off')
    sanitizer=['-fsanitize=undefined','-fno-sanitize-recover=undefined']
    enabled=False;state='disabled_by_user'
    if mode!='off':
        probe=build/'ubsan_probe'
        if probe.exists():probe.unlink()
        p=subprocess.run([cc,'-x','c','-']+sanitizer+['-o',str(probe)],
            input='int main(void){return 0;}\n',text=True,capture_output=True)
        diagnostics=p.stdout+p.stderr
        if p.returncode==0:
            try:
                q=subprocess.run([str(probe)],text=True,capture_output=True)
                enabled=q.returncode==0;diagnostics+=q.stdout+q.stderr
            except OSError as e:diagnostics+=str(e)
        (build/'ubsan_probe.log').write_text(diagnostics)
        state='passed' if enabled else 'unavailable'
        if not enabled and mode=='required':
            raise ValueError('UBSan unavailable; see build/ubsan_probe.log. Default auto mode keeps numerical tests mandatory without UBSan.')
    if enabled:
        print('Native validation: UBSan enabled.',flush=True)
    else:
        print('NOTE: UBSan '+state+'; running mandatory native numerical checks without sanitizer.',flush=True)
    # Never retry the real test without UBSan if its compilation or execution fails.
    subprocess.run([cc,'-O2','-std=c11','-I'+str(root.parents[1]/'isa')]+(sanitizer if enabled else [])+
        [str(root/source),'-o',str(build/name)],check=True)
    subprocess.run([str(build/name)],check=True)
    return {'numeric_comparison':'PASS','ubsan':state,'mode':mode,'compiler':cc}
