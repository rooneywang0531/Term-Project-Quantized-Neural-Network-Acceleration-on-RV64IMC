.text
.globl sr_alias_0
sr_alias_0:
    .insn r4 0x2b, 1, 0, t0, a0, a1, a2
    mv a0, t0
    ret
.globl sr_alias_1
sr_alias_1:
    .insn r4 0x2b, 1, 0, a0, a0, a1, a2
    mv a0, a0
    ret
.globl sr_alias_2
sr_alias_2:
    .insn r4 0x2b, 1, 0, a1, a0, a1, a2
    mv a0, a1
    ret
.globl sr_alias_3
sr_alias_3:
    .insn r4 0x2b, 1, 0, a2, a0, a1, a2
    mv a0, a2
    ret
.globl sr_alias_4
sr_alias_4:
    .insn r4 0x2b, 1, 0, zero, a0, a1, a2
    mv a0, zero
    ret
.globl sr_alias_5
sr_alias_5:
    .insn r4 0x2b, 1, 0, t0, zero, a1, a2
    mv a0, t0
    ret
.globl sr_alias_6
sr_alias_6:
    .insn r4 0x2b, 1, 0, t0, a0, zero, a2
    mv a0, t0
    ret
.globl sr_alias_7
sr_alias_7:
    .insn r4 0x2b, 1, 0, t0, a0, a1, zero
    mv a0, t0
    ret
.globl sr_alias_8
sr_alias_8:
    .insn r4 0x2b, 1, 0, t0, a0, a0, a2
    mv a0, t0
    ret
.globl sr_alias_9
sr_alias_9:
    .insn r4 0x2b, 1, 0, t0, a0, a1, a1
    mv a0, t0
    ret
.globl sr_alias_10
sr_alias_10:
    .insn r4 0x2b, 1, 0, t0, a2, a1, a2
    mv a0, t0
    ret
.globl sr_alias_11
sr_alias_11:
    .insn r4 0x2b, 1, 0, a0, a0, a0, a0
    mv a0, a0
    ret
