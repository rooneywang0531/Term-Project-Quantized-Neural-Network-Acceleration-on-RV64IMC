#!/usr/bin/env python3
"""Regression for weighted counts, scope and exact custom encodings."""
from profile_histogram import analyze

def test():
    manifest = dict(operators=[dict(index=5, kind='CONV_2D', symbol='op_05_test',
        output_elements=1, dense_macs=28, executed_macs=28)], model_sha256='synthetic',
        dense_macs=28, executed_macs=28, mac_note='synthetic', arena_bytes=16)
    symbols = '80001000 00000010 T op_05_test'
    dis = '\n'.join(['80001000: 00050513 addi a0,a0,0',
        '80001004: 0000100b .4byte 0x100b',
        '80001008: 0000000b .4byte 0xb',
        '8000100c: 00008067 jalr zero,0(ra)'])
    hist = 'PC Histogram size: 5\n80001000 1\n80001004 5\n80001008 2\n8000100c 1\n80010000 999999\n'
    r = analyze(hist, symbols, dis, manifest)
    assert r['dynamic_instructions'] == 9
    assert r['instruction_mix'] == {'branch_jump': 1, 'custom_mac': 7, 'integer_alu': 1}
    assert r['operators'][0]['mnemonics']['qmac4.us'] == 5
    assert r['operators'][0]['mnemonics']['qmac4.ss'] == 2
    assert r['operator_code_bytes'] == 16
    # RQ is a separate category, decoded by bits even with stock objdump.
    rq_dis = dis.replace('0000100b', '0000002b')
    rq = analyze(hist, symbols, rq_dis, manifest)
    assert rq['instruction_mix'] == {'branch_jump': 1, 'custom_mac': 2, 'custom_requant': 5, 'integer_alu': 1}
    assert rq['operators'][0]['mnemonics']['qrequant.dr'] == 5
    sr = analyze(hist, symbols, dis.replace('0000100b', '0000102b'), manifest)
    assert sr['operators'][0]['mnemonics']['qrequant.sr'] == 5
    assert sr['instruction_mix']['custom_requant'] == 5
    invalid = [
        (hist.replace('size: 5', 'size: 6'), dis),
        (hist + 'PC Histogram size: 0\n', dis),
        (hist.replace('80001000 1', '80001000 2'), dis),
        (hist, dis.replace('0000100b', '0200100b')),
        (hist, dis.replace('0000100b', '0000200b')),
        (hist, dis.replace('0000100b', '0200002b')),
        (hist, dis.replace('0000100b', '0000202b')),
        (hist, dis.replace('00050513 addi a0,a0,0', '000000ef jal ra,80010000 <helper>')),
    ]
    for h, d in invalid:
        try:
            analyze(h, symbols, d, manifest)
        except ValueError:
            pass
        else:
            raise AssertionError('Invalid histogram/opcode/helper accepted')
    print('PASS: custom encodings, weighted counts, scope, completeness, entries and helper rejection.')

if __name__ == '__main__':
    test()
