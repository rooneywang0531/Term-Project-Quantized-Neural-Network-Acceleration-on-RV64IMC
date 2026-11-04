/* Generated static graph wrappers. */
KERNEL(op_00_transpose)
void op_00_transpose(const int8_t *input, const int8_t *skip, int8_t *output)
{
    (void)skip; transpose(input, output);
}

KERNEL(op_01_pad)
void op_01_pad(const int8_t *input, const int8_t *skip, int8_t *output)
{
    (void)skip; pad(input, output, 224, 224, 3, 230, 230, 3, 3, -14);
}

KERNEL(op_02_conv_2d)
void op_02_conv_2d(const int8_t *input, const int8_t *skip, int8_t *output)
{
    (void)skip; conv(input, output, weights_02, bias_02, mult_02, shift_02, 230, 230, 3, 112, 112, 64, 7, 7, 2, 2, 0, 0, -14, -128, -128, 127);
}

KERNEL(op_03_pad)
void op_03_pad(const int8_t *input, const int8_t *skip, int8_t *output)
{
    (void)skip; pad(input, output, 112, 112, 64, 114, 114, 1, 1, -128);
}

KERNEL(op_04_max_pool_2d)
void op_04_max_pool_2d(const int8_t *input, const int8_t *skip, int8_t *output)
{
    (void)skip; pool(input, output, 114, 114, 64, 56, 56, 3, 3, 2, 2, 0);
}

KERNEL(op_05_conv_2d)
void op_05_conv_2d(const int8_t *input, const int8_t *skip, int8_t *output)
{
    (void)skip; conv(input, output, weights_05, bias_05, mult_05, shift_05, 56, 56, 64, 56, 56, 64, 3, 3, 1, 1, 1, 1, -128, -128, -128, 127);
}

KERNEL(op_06_conv_2d)
void op_06_conv_2d(const int8_t *input, const int8_t *skip, int8_t *output)
{
    (void)skip; conv(input, output, weights_06, bias_06, mult_06, shift_06, 56, 56, 64, 56, 56, 64, 3, 3, 1, 1, 1, 1, -128, 19, -128, 127);
}

KERNEL(op_07_add)
void op_07_add(const int8_t *input, const int8_t *skip, int8_t *output)
{
    (void)skip; add(input, skip, output, 200704, 19, -128, -128, 1073741824, 0, 2036368814, -2, 1109708414, -17, -128, 127);
}

KERNEL(op_08_conv_2d)
void op_08_conv_2d(const int8_t *input, const int8_t *skip, int8_t *output)
{
    (void)skip; conv(input, output, weights_08, bias_08, mult_08, shift_08, 56, 56, 64, 56, 56, 64, 3, 3, 1, 1, 1, 1, -128, -128, -128, 127);
}

KERNEL(op_09_conv_2d)
void op_09_conv_2d(const int8_t *input, const int8_t *skip, int8_t *output)
{
    (void)skip; conv(input, output, weights_09, bias_09, mult_09, shift_09, 56, 56, 64, 56, 56, 64, 3, 3, 1, 1, 1, 1, -128, 19, -128, 127);
}

KERNEL(op_10_add)
void op_10_add(const int8_t *input, const int8_t *skip, int8_t *output)
{
    (void)skip; add(input, skip, output, 200704, 19, -128, -128, 1073741824, 0, 1947895543, -2, 1655772493, -18, -128, 127);
}

KERNEL(op_11_pad)
void op_11_pad(const int8_t *input, const int8_t *skip, int8_t *output)
{
    (void)skip; pad(input, output, 56, 56, 64, 58, 58, 1, 1, -128);
}

KERNEL(op_12_conv_2d)
void op_12_conv_2d(const int8_t *input, const int8_t *skip, int8_t *output)
{
    (void)skip; conv(input, output, weights_12, bias_12, mult_12, shift_12, 58, 58, 64, 28, 28, 128, 3, 3, 2, 2, 0, 0, -128, -128, -128, 127);
}

KERNEL(op_13_conv_2d)
void op_13_conv_2d(const int8_t *input, const int8_t *skip, int8_t *output)
{
    (void)skip; conv(input, output, weights_13, bias_13, mult_13, shift_13, 28, 28, 128, 28, 28, 128, 3, 3, 1, 1, 1, 1, -128, -21, -128, 127);
}

KERNEL(op_14_conv_2d)
void op_14_conv_2d(const int8_t *input, const int8_t *skip, int8_t *output)
{
    (void)skip; conv(input, output, weights_14, bias_14, mult_14, shift_14, 56, 56, 64, 28, 28, 128, 1, 1, 2, 2, 0, 0, -128, 25, -128, 127);
}

KERNEL(op_15_add)
void op_15_add(const int8_t *input, const int8_t *skip, int8_t *output)
{
    (void)skip; add(input, skip, output, 100352, -21, 25, -128, 1073741824, 0, 1664492222, -1, 1546400375, -18, -128, 127);
}

KERNEL(op_16_conv_2d)
void op_16_conv_2d(const int8_t *input, const int8_t *skip, int8_t *output)
{
    (void)skip; conv(input, output, weights_16, bias_16, mult_16, shift_16, 28, 28, 128, 28, 28, 128, 3, 3, 1, 1, 1, 1, -128, -128, -128, 127);
}

KERNEL(op_17_conv_2d)
void op_17_conv_2d(const int8_t *input, const int8_t *skip, int8_t *output)
{
    (void)skip; conv(input, output, weights_17, bias_17, mult_17, shift_17, 28, 28, 128, 28, 28, 128, 3, 3, 1, 1, 1, 1, -128, 13, -128, 127);
}

KERNEL(op_18_add)
void op_18_add(const int8_t *input, const int8_t *skip, int8_t *output)
{
    (void)skip; add(input, skip, output, 100352, 13, -128, -128, 1073741824, 0, 1590340872, -1, 1562532668, -18, -128, 127);
}

KERNEL(op_19_pad)
void op_19_pad(const int8_t *input, const int8_t *skip, int8_t *output)
{
    (void)skip; pad(input, output, 28, 28, 128, 30, 30, 1, 1, -128);
}

KERNEL(op_20_conv_2d)
void op_20_conv_2d(const int8_t *input, const int8_t *skip, int8_t *output)
{
    (void)skip; conv(input, output, weights_20, bias_20, mult_20, shift_20, 30, 30, 128, 14, 14, 256, 3, 3, 2, 2, 0, 0, -128, -128, -128, 127);
}

KERNEL(op_21_conv_2d)
void op_21_conv_2d(const int8_t *input, const int8_t *skip, int8_t *output)
{
    (void)skip; conv(input, output, weights_21, bias_21, mult_21, shift_21, 14, 14, 256, 14, 14, 256, 3, 3, 1, 1, 1, 1, -128, -34, -128, 127);
}

KERNEL(op_22_conv_2d)
void op_22_conv_2d(const int8_t *input, const int8_t *skip, int8_t *output)
{
    (void)skip; conv(input, output, weights_22, bias_22, mult_22, shift_22, 28, 28, 128, 14, 14, 256, 1, 1, 2, 2, 0, 0, -128, 18, -128, 127);
}

KERNEL(op_23_add)
void op_23_add(const int8_t *input, const int8_t *skip, int8_t *output)
{
    (void)skip; add(input, skip, output, 50176, -34, 18, -128, 1073741824, 0, 1593879619, -2, 1892973398, -18, -128, 127);
}

KERNEL(op_24_conv_2d)
void op_24_conv_2d(const int8_t *input, const int8_t *skip, int8_t *output)
{
    (void)skip; conv(input, output, weights_24, bias_24, mult_24, shift_24, 14, 14, 256, 14, 14, 256, 3, 3, 1, 1, 1, 1, -128, -128, -128, 127);
}

KERNEL(op_25_conv_2d)
void op_25_conv_2d(const int8_t *input, const int8_t *skip, int8_t *output)
{
    (void)skip; conv(input, output, weights_25, bias_25, mult_25, shift_25, 14, 14, 256, 14, 14, 256, 3, 3, 1, 1, 1, 1, -128, 18, -128, 127);
}

KERNEL(op_26_add)
void op_26_add(const int8_t *input, const int8_t *skip, int8_t *output)
{
    (void)skip; add(input, skip, output, 50176, 18, -128, -128, 1073741824, 0, 1955656968, -2, 1395414883, -18, -128, 127);
}

KERNEL(op_27_pad)
void op_27_pad(const int8_t *input, const int8_t *skip, int8_t *output)
{
    (void)skip; pad(input, output, 14, 14, 256, 16, 16, 1, 1, -128);
}

KERNEL(op_28_conv_2d)
void op_28_conv_2d(const int8_t *input, const int8_t *skip, int8_t *output)
{
    (void)skip; conv(input, output, weights_28, bias_28, mult_28, shift_28, 16, 16, 256, 7, 7, 512, 3, 3, 2, 2, 0, 0, -128, -128, -128, 127);
}

KERNEL(op_29_conv_2d)
void op_29_conv_2d(const int8_t *input, const int8_t *skip, int8_t *output)
{
    (void)skip; conv(input, output, weights_29, bias_29, mult_29, shift_29, 7, 7, 512, 7, 7, 512, 3, 3, 1, 1, 1, 1, -128, -10, -128, 127);
}

KERNEL(op_30_conv_2d)
void op_30_conv_2d(const int8_t *input, const int8_t *skip, int8_t *output)
{
    (void)skip; conv(input, output, weights_30, bias_30, mult_30, shift_30, 14, 14, 256, 7, 7, 512, 1, 1, 2, 2, 0, 0, -128, -7, -128, 127);
}

KERNEL(op_31_add)
void op_31_add(const int8_t *input, const int8_t *skip, int8_t *output)
{
    (void)skip; add(input, skip, output, 25088, -10, -7, -128, 1073741824, 0, 1271968949, -1, 1556217327, -18, -128, 127);
}

KERNEL(op_32_conv_2d)
void op_32_conv_2d(const int8_t *input, const int8_t *skip, int8_t *output)
{
    (void)skip; conv(input, output, weights_32, bias_32, mult_32, shift_32, 7, 7, 512, 7, 7, 512, 3, 3, 1, 1, 1, 1, -128, -128, -128, 127);
}

KERNEL(op_33_conv_2d)
void op_33_conv_2d(const int8_t *input, const int8_t *skip, int8_t *output)
{
    (void)skip; conv(input, output, weights_33, bias_33, mult_33, shift_33, 7, 7, 512, 7, 7, 512, 3, 3, 1, 1, 1, 1, -128, -56, -128, 127);
}

KERNEL(op_34_add)
void op_34_add(const int8_t *input, const int8_t *skip, int8_t *output)
{
    (void)skip; add(input, skip, output, 25088, -56, -128, -128, 1073741824, 0, 1338787806, -3, 1361180810, -18, -128, 127);
}

KERNEL(op_35_average_pool_2d)
void op_35_average_pool_2d(const int8_t *input, const int8_t *skip, int8_t *output)
{
    (void)skip; pool(input, output, 7, 7, 512, 1, 1, 7, 7, 7, 7, 1);
}

KERNEL(op_36_fully_connected)
void op_36_fully_connected(const int8_t *input, const int8_t *skip, int8_t *output)
{
    (void)skip; fc(input, output, weights_36, bias_36, mult_36, shift_36, -128, -61);
}
