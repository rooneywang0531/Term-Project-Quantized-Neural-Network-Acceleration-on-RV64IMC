#!/usr/bin/env python3
"""Export the SHA-guarded, static INT8 ResNet18 graph; no ML runtime on target."""
import argparse, hashlib, json, math
from pathlib import Path
import numpy as np
import tflite
from ai_edge_litert.interpreter import Interpreter, OpResolverType
SHA='8fea1acb62829e120b4953b6fbf0f842e0032909254f51c2d989703b66534683'

def qm(x):
    f,s=math.frexp(float(x));m=math.floor(f*(1<<31)+0.5)
    if m==1<<31:m//=2;s+=1
    if s < -31: m,s=0,0  # TFLite QuantizeMultiplier flushes tiny multipliers.
    assert -31<=s<=0,(x,s)
    return m,s

def export(path,dest):
    dest.mkdir(parents=True,exist_ok=True)
    raw=path.read_bytes();assert hashlib.sha256(raw).hexdigest()==SHA
    model=tflite.Model.GetRootAsModel(raw,0);sg=model.Subgraphs(0)
    def shape(t):return list(map(int,sg.Tensors(t).ShapeAsNumpy()))
    def size(t):return math.prod(shape(t))
    def q(t):
        z=sg.Tensors(t).Quantization();return np.asarray(z.ScaleAsNumpy(),dtype=np.float64),np.asarray(z.ZeroPointAsNumpy(),dtype=np.int64)
    def scale(t):return float(q(t)[0][0])
    def zp(t):return int(q(t)[1][0])
    def const(t):
        z=sg.Tensors(t);dtype={tflite.TensorType.INT8:np.int8,tflite.TensorType.INT32:np.dtype('<i4')}[z.Type()]
        return np.frombuffer(model.Buffers(z.Buffer()).DataAsNumpy().tobytes(),dtype=dtype).reshape(shape(t))
    def opts(o,cls):
        tab=o.BuiltinOptions();v=cls();v.Init(tab.Bytes,tab.Pos);return v
    names={v:k for k,v in vars(tflite.BuiltinOperator).items() if isinstance(v,int)}
    ops=[]
    for i in range(sg.OperatorsLength()):
        o=sg.Operators(i);kind=names[model.OperatorCodes(o.OpcodeIndex()).BuiltinCode()]
        ins=list(map(int,o.InputsAsNumpy()));out=int(o.Outputs(0));assert sg.Tensors(out).Type()==tflite.TensorType.INT8
        ops.append(dict(index=i,kind=kind,inputs=ins,output=out,output_shape=shape(out),output_elements=size(out),symbol='op_%02d_%s'%(i,kind.lower()),dense_macs=0,executed_macs=0))
    # First-fit static arena allocation, outputs allocated BEFORE inputs expire.
    last={85:0}
    for op in ops:
        for t in op['inputs']:last[t]=op['index']
    offsets={};live={};peak=0
    def alloc(t):
        nonlocal peak
        n=(size(t)+15)//16*16;pos=0
        for p,k in sorted(live.values()):
            if pos+n<=p:break
            pos=max(pos,p+k)
        live[t]=(pos,n);offsets[t]=pos;peak=max(peak,pos+n)
    alloc(85)
    for op in ops:
        alloc(op['output'])
        for t in list(live):
            if last.get(t,-1)<=op['index']:del live[t]
    blob=bytearray();decl=[];asm=['.section .rodata.model,"a",@progbits','.balign 16','.globl model_blob','model_blob:', '.incbin "model_constants.bin"']
    def array(name,a):
        a=np.asarray(a);alignment=8
        while len(blob)%alignment:blob.append(0)
        off=len(blob);blob.extend(a.tobytes());typ='int8_t' if a.dtype==np.int8 else 'int32_t'
        decl.append('extern const %s %s[%d];'%(typ,name,a.size))
        asm.extend(['.globl '+name,'.set %s, model_blob + %d'%(name,off)])
        return name
    wrappers=[];calls=[];protos=[];goff=0
    def act(f,out):
        assert f in (0,1)
        return (max(-128,zp(out)) if f==1 else -128,127)
    for op in ops:
        i=op['index'];o=sg.Operators(i);kind=op['kind'];ins=op['inputs'];t=ins[0];out=op['output'];ish=shape(t);osh=shape(out);sym=op['symbol'];a='input';b='skip';y='output'
        op['arena_offset']=offsets[out];op['golden_offset']=goff;goff+=size(out)
        op['input_scale']=scale(t);op['input_zero_point']=zp(t)
        op['output_scale']=scale(out);op['output_zero_point']=zp(out)
        if kind in ('CONV_2D','FULLY_CONNECTED'):
            w,bias=ins[1:];ws=shape(w);assert set(q(w)[1].tolist())=={0}
            assert np.allclose(q(bias)[0],scale(t)*q(w)[0],rtol=2e-6,atol=1e-12)
            assert np.all(q(bias)[1]==0)
            weights=array('weights_%02d'%i,const(w));bs=array('bias_%02d'%i,const(bias))
            pairs=[qm(v) for v in scale(t)*q(w)[0]/scale(out)]
            mult=array('mult_%02d'%i,np.array([p[0] for p in pairs],dtype='<i4'));shift=array('shift_%02d'%i,np.array([p[1] for p in pairs],dtype='<i4'))
            if kind=='CONV_2D':
                p=opts(o,tflite.Conv2DOptions);sh,sw=int(p.StrideH()),int(p.StrideW());assert p.DilationHFactor()==p.DilationWFactor()==1
                oc,kh,kw,ic=ws;ih,iw=ish[1:3];oh,ow=osh[1:3]
                ph=max(0,(oh-1)*sh+kh-ih)//2 if p.Padding()==tflite.Padding.SAME else 0
                pw=max(0,(ow-1)*sw+kw-iw)//2 if p.Padding()==tflite.Padding.SAME else 0
                amin,amax=act(p.FusedActivationFunction(),out)
                args=[weights,bs,mult,shift,ih,iw,ic,oh,ow,oc,kh,kw,sh,sw,ph,pw,zp(t),zp(out),amin,amax]
                body='conv(input, output, '+', '.join(map(str,args))+');'
                op['dense_macs']=oh*ow*oc*kh*kw*ic
                valid=sum(0<=oy*sh+ky-ph<ih and 0<=ox*sw+kx-pw<iw for oy in range(oh) for ox in range(ow) for ky in range(kh) for kx in range(kw))
                op['executed_macs']=valid*oc*ic
                op['fused_activation']=int(p.FusedActivationFunction());op['weight_shape']=ws
                op['strides']=[sh,sw];op['implicit_padding_top_left']=[ph,pw]
                op['weight_scales']=q(w)[0].tolist();op['requantization_shifts']=[p[1] for p in pairs]
            else:
                p=opts(o,tflite.FullyConnectedOptions);assert p.FusedActivationFunction()==0 and ws==[1000,512]
                body='fc(input, output, %s, %s, %s, %s, %d, %d);'%(weights,bs,mult,shift,zp(t),zp(out));op['dense_macs']=op['executed_macs']=512000
        elif kind=='ADD':
            p=opts(o,tflite.AddOptions);assert shape(ins[0])==shape(ins[1])==osh
            twice=2*max(scale(t),scale(ins[1]));pairs=[qm(scale(t)/twice),qm(scale(ins[1])/twice),qm(twice/((1<<20)*scale(out)))]
            amin,amax=act(p.FusedActivationFunction(),out)
            args=[size(out),zp(t),zp(ins[1]),zp(out)]+[v for pair in pairs for v in pair]+[amin,amax]
            body='add(input, skip, output, '+', '.join(map(str,args))+');'
        elif kind=='TRANSPOSE':
            assert const(ins[1]).tolist()==[0,2,3,1] and ish==[1,3,224,224]
            body='transpose(input, output);';assert scale(t)==scale(out) and zp(t)==zp(out)
        elif kind=='PAD':
            pads=const(ins[1]);assert pads[0].tolist()==[0,0] and pads[3].tolist()==[0,0]
            assert scale(t)==scale(out) and zp(t)==zp(out)
            args=[ish[1],ish[2],ish[3],osh[1],osh[2],int(pads[1,0]),int(pads[2,0]),zp(t)]
            body='pad(input, output, '+', '.join(map(str,args))+');'
        elif kind in ('MAX_POOL_2D','AVERAGE_POOL_2D'):
            p=opts(o,tflite.Pool2DOptions);assert p.Padding()==tflite.Padding.VALID and p.FusedActivationFunction()==0
            assert scale(t)==scale(out) and zp(t)==zp(out)
            args=[ish[1],ish[2],ish[3],osh[1],osh[2],int(p.FilterHeight()),int(p.FilterWidth()),int(p.StrideH()),int(p.StrideW()),int(kind=='AVERAGE_POOL_2D')]
            body='pool(input, output, '+', '.join(map(str,args))+');'
        else:raise ValueError(kind)
        proto='void %s(const int8_t *input, const int8_t *skip, int8_t *output)'%sym
        protos.append(proto+';')
        wrappers.append('KERNEL(%s)\n%s\n{\n    (void)skip; %s\n}\n'%(sym,proto,body))
        skip='arena + %d'%offsets[ins[1]] if kind=='ADD' else '(const int8_t *)0'
        calls.extend(['    current_operator = %d;'%i,'    %s(arena + %d, %s, arena + %d);'%(sym,offsets[t],skip,offsets[out]),
                      '    if (check_output(%d, arena + %d, golden + %d, %d)) return %d;'%(i,offsets[out],op['golden_offset'],size(out),i+1)])
    (dest/'model_constants.bin').write_bytes(blob)
    (dest/'model_data.h').write_text('#ifndef MODEL_DATA_H\n#define MODEL_DATA_H\n#include <stdint.h>\n'+'\n'.join(decl)+f'\n#define ARENA_BYTES {peak}\n#define INPUT_BYTES {size(85)}\n#define GOLDEN_BYTES {goff}\n#define INPUT_OFFSET {offsets[85]}\n#define OUTPUT_OFFSET {offsets[41]}\n#endif\n')
    (dest/'operators.inc').write_text('/* Generated static graph wrappers. */\n'+'\n'.join(wrappers))
    (dest/'graph.inc').write_text('/* Generated call graph. Every consumer reads actual C output. */\n'+'\n'.join(calls)+'\n')
    (dest/'operators.h').write_text('#include <stdint.h>\n'+'\n'.join(protos)+'\n')
    asm+=['.section .rodata.fixture,"a",@progbits','.balign 16','.globl fixture_input','fixture_input:', '#if CASE_ID == 1','.incbin "fixtures/real_zero.bin"','#elif CASE_ID == 2','.incbin "fixtures/maximum.bin"','#else','.incbin "fixtures/random.bin"','#endif','.globl fixture_golden',f'.set fixture_golden, fixture_input + {size(85)}', '.section .note.GNU-stack,"",@progbits']
    (dest/'data.S').write_text('\n'.join(asm)+'\n')
    (dest/'fixtures').mkdir(exist_ok=True)
    runtime=Interpreter(model_content=raw,num_threads=1,experimental_preserve_all_tensors=True,experimental_op_resolver_type=OpResolverType.BUILTIN_REF)
    runtime.allocate_tensors();cases={}
    for name in ('random','real_zero','maximum'):
        x=(np.random.default_rng(20261024).integers(-128,128,size=shape(85),dtype=np.int8) if name=='random' else np.full(shape(85),zp(85) if name=='real_zero' else 127,dtype=np.int8))
        runtime.set_tensor(85,x);runtime.invoke();fixture=x.tobytes()+b''.join(runtime.get_tensor(op['output']).tobytes() for op in ops)
        (dest/'fixtures'/f'{name}.bin').write_bytes(fixture)
        logits=runtime.get_tensor(41).reshape(-1);cases[name]={'sha256':hashlib.sha256(fixture).hexdigest(),'bytes':len(fixture),'top1_index':int(logits.argmax())}
        print('Exported',name,'all 37 reference outputs',len(fixture),'bytes',flush=True)
    info={'model_sha256':SHA,'model_bytes':len(raw),'reference':'ai-edge-litert 2.3.0 BUILTIN_REF; one thread; preserve tensors; no delegates',
          'input_shape':shape(85),'input_scale':scale(85),'input_zero_point':zp(85),'output_shape':shape(41),'output_scale':scale(41),'output_zero_point':zp(41),
          'seed':20261024,'test_purpose':'Synthetic correctness tests, not classification accuracy evaluation',
          'arena_bytes':peak,'golden_bytes':goff,'constants_bytes':len(blob),'cases':cases,'operators':ops,
          'dense_macs':sum(o['dense_macs'] for o in ops),'executed_macs':sum(o['executed_macs'] for o in ops),
          'rounding':'Conv and ADD: double rounding; FC: single rounding; int8 AVG_POOL: sign-aware rounded integer division',
          'mac_note':'executed_macs excludes implicit SAME-padding taps only; explicit PAD buffers are materialized and their MACs execute'}
    (dest/'model_manifest.json').write_text(json.dumps(info,indent=2)+'\n')
    assets=['model_constants.bin','model_data.h','operators.inc','operators.h','graph.inc','data.S','model_manifest.json']+['fixtures/'+n+'.bin' for n in cases]
    (dest/'asset_hashes.json').write_text(json.dumps({n:hashlib.sha256((dest/n).read_bytes()).hexdigest() for n in assets},indent=2)+'\n')
    print('Static arena:',peak,'dense MACs:',info['dense_macs'],'executed MACs:',info['executed_macs'])

if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('model',type=Path);p.add_argument('--output',type=Path,default=Path(__file__).resolve().parent);a=p.parse_args();export(a.model,a.output)
