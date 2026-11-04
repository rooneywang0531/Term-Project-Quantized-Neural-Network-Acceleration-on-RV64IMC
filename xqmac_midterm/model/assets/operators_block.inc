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
