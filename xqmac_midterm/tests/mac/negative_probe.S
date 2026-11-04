.section .text.init
.globl _start
_start:
#ifdef BAD_FUNCT2
    .insn r4 0x0b, 1, 1, a0, a1, a2, a3
#elif defined(BAD_ENCODING)
    .insn r4 0x0b, 2, 0, a0, a1, a2, a3
#else
    .insn r4 0x0b, 1, 0, a0, a1, a2, a3
    .insn r4 0x0b, 0, 0, a0, a1, a2, a3
#endif
    la t0,tohost
    li t1,1
    sd t1,0(t0)
1:  j 1b
.section .tohost,"aw",@progbits
.balign 64
.globl tohost
tohost: .dword 0
.balign 64
.globl fromhost
fromhost: .dword 0
