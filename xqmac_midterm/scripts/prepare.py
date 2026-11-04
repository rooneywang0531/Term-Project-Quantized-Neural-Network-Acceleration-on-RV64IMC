#!/usr/bin/env python3
"""Audit original constants, shapes, zero points and expected per-op custom counts."""
import hashlib,json,re,struct
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
def digest(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def prepare(base,require_unit=True):
    for name,expected in json.loads((base/'asset_hashes.json').read_text()).items():
        if digest(base/name)!=expected:raise ValueError('Changed original asset: '+name)
    m=json.loads((base/'model_manifest.json').read_text())
    assert m['model_sha256']=='8fea1acb62829e120b4953b6fbf0f842e0032909254f51c2d989703b66534683'
    assert digest(ROOT/'model/resnet18_int8_channelwise.tflite')==m['model_sha256'],'Changed original TFLite model'
    assert len(m['operators'])==37
    blob=(base/'model_constants.bin').read_bytes();asm=(base/'data.S').read_text()
    offsets={n:int(x) for n,x in re.findall(r'\.set (\w+), model_blob \+ (\d+)',asm)}
    expected={};alignment=[]
    for op in m['operators']:
        counts={'qmac4.ss':0,'qmac4.us':0,'qrequant.dr':0,'qrequant.sr':0}
        kind=op['kind'];index=op['index'];n=op['output_elements']
        if kind=='CONV_2D':
            oc,kh,kw,ic=op['weight_shape'];assert oc%4==0
            assert offsets['weights_%02d'%index]%4==0
            if index==2:
                assert [oc,kh,kw,ic]==[64,7,7,3] and op['input_zero_point']==-14
                assert op['implicit_padding_top_left']==[0,0] and op['strides']==[2,2]
                assert op['output_shape']==[1,112,112,64]
                counts['qmac4.ss']=n*kh*(kw*ic//4)
            else:
                assert ic%4==0 and op['input_zero_point']==-128
                assert op['executed_macs']%4==0
                assert op['arena_offset']%4==0
                counts['qmac4.us']=op['executed_macs']//4
            counts['qrequant.dr']=n
            size=oc
        elif kind=='FULLY_CONNECTED':
            assert index==36 and n==1000 and op['input_zero_point']==-128
            assert offsets['weights_36']%4==0
            counts['qmac4.us']=op['executed_macs']//4;counts['qrequant.sr']=n;size=1000
        elif kind=='ADD':counts['qrequant.dr']=3*n;size=0
        else:size=0
        if size:
            suffix='%02d'%index
            mult=struct.unpack_from('<%di'%size,blob,offsets['mult_'+suffix])
            shifts=struct.unpack_from('<%di'%size,blob,offsets['shift_'+suffix])
            assert all(0<=x<=0x7fffffff for x in mult)
            assert all(-31<=x<=0 for x in shifts)
            alignment.append('weights_'+suffix)
        expected[op['symbol']]=counts
    # Input activation alignment is checked in graph.inc, not inferred from output placement.
    graph=(base/'graph.inc').read_text()
    aligned_inputs=0
    for line in graph.splitlines():
        match=re.search(r'op_(\d+)_\w+\(arena\s*\+\s*(\d+)',line)
        if match and int(match[1]) in [o['index'] for o in m['operators'] if o['kind'] in ('CONV_2D','FULLY_CONNECTED') and o['index']!=2]:
            assert int(match[2])%4==0
            aligned_inputs+=1
    assert aligned_inputs==20,'Not all packed input addresses were audited'
    plan={'manifest':m,'expected_per_operator':expected,'aligned_weight_symbols':alignment,
      'original_constant_sha256':digest(base/'model_constants.bin'),
      'shared_sources_sha256':{n:digest((ROOT/'workload'/n) if n in ['model.c','start.S','link.ld'] else base/n) for n in ['model.c','graph.inc','operators.inc','operators.h','model_data.h','start.S','link.ld','data.S']}}
    if require_unit:
        unit=json.loads((ROOT/'results/unit/unit_pass.json').read_text())
        assert unit['correctness']=='PASS' and unit['sr_custom_counts']['qrequant.sr']>0
        for name,sha in unit['tested_source_sha256'].items():assert digest(ROOT/name)==sha,'Changed tested source '+name
        plugin=ROOT/'build/unit/libxqmac.so';assert digest(plugin)==unit['plugin_sha256'],'Plugin changed after unit tests'
        plan.update(plugin=str(plugin),plugin_sha256=digest(plugin),unit_spike_sha256=unit['spike_sha256'])
    return plan
