.section .rodata.model,"a",@progbits
.balign 16
.globl model_blob
model_blob:
.incbin "model_constants.bin"
.globl weights_02
.set weights_02, model_blob + 0
.globl bias_02
.set bias_02, model_blob + 9408
.globl mult_02
.set mult_02, model_blob + 9664
.globl shift_02
.set shift_02, model_blob + 9920
.globl weights_05
.set weights_05, model_blob + 10176
.globl bias_05
.set bias_05, model_blob + 47040
.globl mult_05
.set mult_05, model_blob + 47296
.globl shift_05
.set shift_05, model_blob + 47552
.globl weights_06
.set weights_06, model_blob + 47808
.globl bias_06
.set bias_06, model_blob + 84672
.globl mult_06
.set mult_06, model_blob + 84928
.globl shift_06
.set shift_06, model_blob + 85184
.globl weights_08
.set weights_08, model_blob + 85440
.globl bias_08
.set bias_08, model_blob + 122304
.globl mult_08
.set mult_08, model_blob + 122560
.globl shift_08
.set shift_08, model_blob + 122816
.globl weights_09
.set weights_09, model_blob + 123072
.globl bias_09
.set bias_09, model_blob + 159936
.globl mult_09
.set mult_09, model_blob + 160192
.globl shift_09
.set shift_09, model_blob + 160448
.globl weights_12
.set weights_12, model_blob + 160704
.globl bias_12
.set bias_12, model_blob + 234432
.globl mult_12
.set mult_12, model_blob + 234944
.globl shift_12
.set shift_12, model_blob + 235456
.globl weights_13
.set weights_13, model_blob + 235968
.globl bias_13
.set bias_13, model_blob + 383424
.globl mult_13
.set mult_13, model_blob + 383936
.globl shift_13
.set shift_13, model_blob + 384448
.globl weights_14
.set weights_14, model_blob + 384960
.globl bias_14
.set bias_14, model_blob + 393152
.globl mult_14
.set mult_14, model_blob + 393664
.globl shift_14
.set shift_14, model_blob + 394176
.globl weights_16
.set weights_16, model_blob + 394688
.globl bias_16
.set bias_16, model_blob + 542144
.globl mult_16
.set mult_16, model_blob + 542656
.globl shift_16
.set shift_16, model_blob + 543168
.globl weights_17
.set weights_17, model_blob + 543680
.globl bias_17
.set bias_17, model_blob + 691136
.globl mult_17
.set mult_17, model_blob + 691648
.globl shift_17
.set shift_17, model_blob + 692160
.globl weights_20
.set weights_20, model_blob + 692672
.globl bias_20
.set bias_20, model_blob + 987584
.globl mult_20
.set mult_20, model_blob + 988608
.globl shift_20
.set shift_20, model_blob + 989632
.globl weights_21
.set weights_21, model_blob + 990656
.globl bias_21
.set bias_21, model_blob + 1580480
.globl mult_21
.set mult_21, model_blob + 1581504
.globl shift_21
.set shift_21, model_blob + 1582528
.globl weights_22
.set weights_22, model_blob + 1583552
.globl bias_22
.set bias_22, model_blob + 1616320
.globl mult_22
.set mult_22, model_blob + 1617344
.globl shift_22
.set shift_22, model_blob + 1618368
.globl weights_24
.set weights_24, model_blob + 1619392
.globl bias_24
.set bias_24, model_blob + 2209216
.globl mult_24
.set mult_24, model_blob + 2210240
.globl shift_24
.set shift_24, model_blob + 2211264
.globl weights_25
.set weights_25, model_blob + 2212288
.globl bias_25
.set bias_25, model_blob + 2802112
.globl mult_25
.set mult_25, model_blob + 2803136
.globl shift_25
.set shift_25, model_blob + 2804160
.globl weights_28
.set weights_28, model_blob + 2805184
.globl bias_28
.set bias_28, model_blob + 3984832
.globl mult_28
.set mult_28, model_blob + 3986880
.globl shift_28
.set shift_28, model_blob + 3988928
.globl weights_29
.set weights_29, model_blob + 3990976
.globl bias_29
.set bias_29, model_blob + 6350272
.globl mult_29
.set mult_29, model_blob + 6352320
.globl shift_29
.set shift_29, model_blob + 6354368
.globl weights_30
.set weights_30, model_blob + 6356416
.globl bias_30
.set bias_30, model_blob + 6487488
.globl mult_30
.set mult_30, model_blob + 6489536
.globl shift_30
.set shift_30, model_blob + 6491584
.globl weights_32
.set weights_32, model_blob + 6493632
.globl bias_32
.set bias_32, model_blob + 8852928
.globl mult_32
.set mult_32, model_blob + 8854976
.globl shift_32
.set shift_32, model_blob + 8857024
.globl weights_33
.set weights_33, model_blob + 8859072
.globl bias_33
.set bias_33, model_blob + 11218368
.globl mult_33
.set mult_33, model_blob + 11220416
.globl shift_33
.set shift_33, model_blob + 11222464
.globl weights_36
.set weights_36, model_blob + 11224512
.globl bias_36
.set bias_36, model_blob + 11736512
.globl mult_36
.set mult_36, model_blob + 11740512
.globl shift_36
.set shift_36, model_blob + 11744512
.section .rodata.fixture,"a",@progbits
.balign 16
.globl fixture_input
fixture_input:
#if CASE_ID == 1
.incbin "fixtures/real_zero.bin"
#elif CASE_ID == 2
.incbin "fixtures/maximum.bin"
#else
.incbin "fixtures/random.bin"
#endif
.globl fixture_golden
.set fixture_golden, fixture_input + 150528
.section .note.GNU-stack,"",@progbits
