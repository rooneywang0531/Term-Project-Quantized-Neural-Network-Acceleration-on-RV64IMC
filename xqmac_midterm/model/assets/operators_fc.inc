KERNEL(op_36_fully_connected)
void op_36_fully_connected(const int8_t *input, const int8_t *skip, int8_t *output)
{
    (void)skip; fc(input, output, weights_36, bias_36, mult_36, shift_36, -128, -61);
}
