"""RV64IMC instruction-bit classifier."""
def classify(bits):
    if bits & 3 != 3:
        q, f3 = bits & 3, (bits >> 13) & 7
        if q in (0, 2) and f3 in (2, 3):
            return "load"
        if q in (0, 2) and f3 in (6, 7):
            return "store"
        if q == 1 and f3 in (5, 6, 7):
            return "branch_jump"
        if q == 2 and f3 == 4 and ((bits >> 2) & 31) == 0:
            return "branch_jump" if ((bits >> 7) & 31) else "other"
        return "integer_alu"
    opcode, f7, f3 = bits & 127, (bits >> 25) & 127, (bits >> 12) & 7
    if opcode == 0x03:
        return "load"
    if opcode == 0x23:
        return "store"
    if opcode in (0x63, 0x67, 0x6f):
        return "branch_jump"
    if opcode in (0x33, 0x3b) and f7 == 1:
        return "multiply" if f3 <= 3 else "divide_remainder"
    if opcode in (0x13, 0x1b, 0x33, 0x3b, 0x37, 0x17):
        return "integer_alu"
    if opcode in (0x07, 0x27, 0x43, 0x47, 0x4b, 0x4f, 0x53):
        return "floating_or_vector"
    if opcode == 0x73:
        return "system"
    return "other"
