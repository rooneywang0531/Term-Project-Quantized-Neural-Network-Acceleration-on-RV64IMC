.text
.globl rq_alias_0
rq_alias_0:
    .insn r4 0x2b, 0, 0, t0, a0, a1, a2
    mv a0, t0
    ret
.globl rq_alias_1
rq_alias_1:
    .insn r4 0x2b, 0, 0, a0, a0, a1, a2
    mv a0, a0
    ret
.globl rq_alias_2
rq_alias_2:
    .insn r4 0x2b, 0, 0, a1, a0, a1, a2
    mv a0, a1
    ret
.globl rq_alias_3
rq_alias_3:
    .insn r4 0x2b, 0, 0, a2, a0, a1, a2
    mv a0, a2
    ret
.globl rq_alias_4
rq_alias_4:
    .insn r4 0x2b, 0, 0, zero, a0, a1, a2
    mv a0, zero
    ret
.globl rq_alias_5
rq_alias_5:
    .insn r4 0x2b, 0, 0, t0, zero, a1, a2
    mv a0, t0
    ret
.globl rq_alias_6
rq_alias_6:
    .insn r4 0x2b, 0, 0, t0, a0, zero, a2
    mv a0, t0
    ret
.globl rq_alias_7
rq_alias_7:
    .insn r4 0x2b, 0, 0, t0, a0, a1, zero
    mv a0, t0
    ret
.globl rq_alias_8
rq_alias_8:
    .insn r4 0x2b, 0, 0, t0, a0, a0, a2
    mv a0, t0
    ret
.globl rq_alias_9
rq_alias_9:
    .insn r4 0x2b, 0, 0, t0, a0, a1, a1
    mv a0, t0
    ret
.globl rq_alias_10
rq_alias_10:
    .insn r4 0x2b, 0, 0, t0, a2, a1, a2
    mv a0, t0
    ret
.globl rq_alias_11
rq_alias_11:
    .insn r4 0x2b, 0, 0, a0, a0, a0, a0
    mv a0, a0
    ret
