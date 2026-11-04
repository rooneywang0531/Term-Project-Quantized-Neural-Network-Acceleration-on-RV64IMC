.section .text.init
.globl _start
_start:
    li a0,-3
    li a1,0x40000000
    li a2,31
#if defined(BAD_SHIFT)
    li a2,30
#elif defined(BAD_HIGH_SHIFT)
    li a2,63
#elif defined(BAD_MULT)
    li a1,0x80000000
#endif
#if defined(BAD_FUNCT2)
    .insn r4 0x2b,1,1,a0,a0,a1,a2
#elif defined(BAD_FUNCT3)
    .insn r4 0x2b,2,0,a0,a0,a1,a2
#else
    .insn r4 0x2b,1,0,a0,a0,a1,a2
#endif
    li t1,-1
    bne a0,t1,fail
    li t1,1
    j finish
fail:
    li t1,3
finish:
    la t0,tohost
    sd t1,0(t0)
1:  j 1b
.section .tohost,"aw",@progbits
.balign 64
.globl tohost
tohost: .dword 0
.balign 64
.globl fromhost
fromhost: .dword 0
