# Instruction | OPCODE      | OP Size   | 11 bit OPCODE range | Instruction
#             |             | (base 10) | Start    | End      | Format
# ------------|-------------|-----------|----------|----------|-------------
# B           | 000101      | 6         |  160     | 191      | B
# AND         | 10001010000 | 11        |  1104    |          | R
# ADD         | 10001011000 | 11        |  1112    |          | R
# ADDI        | 1001000100  | 10        |  1160    | 1161     | I
# ORR         | 10101010000 | 11        |  1360    |          | R
# CBZ         | 10110100    | 8         |  1440    | 1447     | CB
# CBNZ        | 10110101    | 8         |  1448    | 1455     | CB
# SUB         | 11001011000 | 11        |  1624    |          | R
# SUBI        | 1101000100  | 10        |  1672    | 1673     | I
# MOVZ        | 110100101   | 9         |  1648    | 1687     | IM
# MOVK        | 111100101   | 9         |  1940    | 1943     | IM
# LSR         | 11010011010 | 11        |  1690    |          | R
# LSL         | 11010011011 | 11        |  1691    |          | R
# STUR        | 11111000000 | 11        |  1984    |          | D
# LDUR        | 11111000010 | 11        |  1986    |          | D
#
# BREAK         1 11111 10110 11110 11111 11111 100111 ???

# R
# opcode    Rm  shamt   Rn  Rd
# 11        5   6       5   5

# D
# opcode    address op2 Rn  Rt
# 11        9       2   5   5

# I
# opcode    immediate   Rn  Rd
# 10        12          5   5

# B
# opcode    address
# 6         26

# CB
# opcode    address     Rt
# 8         19          5


class Disassembler:

    # |0000 0000 000|0 0000 0000 0000 0000 0000
    @staticmethod
    def get_opcode(inst):
        return (0xFFE00000 & inst) >> 21

    def run(self):
        filename = 'test2_bin.txt'

        with open(filename) as f:
            lines = [int(line.rstrip('\n'), 2) for line in f]

        for line in lines:
            print(self.get_opcode(line))


d = Disassembler()
d.run()

