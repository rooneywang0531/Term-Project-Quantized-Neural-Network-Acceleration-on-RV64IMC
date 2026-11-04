OUTPUT_ARCH(riscv)
ENTRY(_start)
MEMORY {
    RAM (rwx) : ORIGIN = 0x80000000, LENGTH = 64M
}
PHDRS {
    code PT_LOAD FLAGS(5);
    constants PT_LOAD FLAGS(4);
    writable PT_LOAD FLAGS(6);
}
SECTIONS {
    .text : {
        KEEP(*(.text.init))
        *(.text.kernel.*)
        *(.text .text.*)
    } > RAM :code
    .rodata ALIGN(4096) : {
        *(.rodata .rodata.*)
        *(.srodata .srodata.*)
    } > RAM :constants
    .data ALIGN(4096) : {
        *(.data .data.*)
        *(.sdata .sdata.*)
    } > RAM :writable
    .tohost ALIGN(64) : {
        KEEP(*(.tohost))
    } > RAM :writable
    .bss (NOLOAD) : {
        . = ALIGN(8);
        __bss_start = .;
        *(.bss .bss.*)
        *(.sbss .sbss.*)
        *(COMMON)
        . = ALIGN(8);
        __bss_end = .;
    } > RAM :writable
    .stack (NOLOAD) : {
        . = ALIGN(16);
        . += 65536;
        __stack_top = .;
    } > RAM :writable
    /DISCARD/ : { *(.comment) *(.note*) *(.eh_frame*) }
}
