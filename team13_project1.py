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


##
# command line decode
# for i in range(len(sys.argv)):
#    if (sys.argv[i] == '-i' and i < (len(sys.argv) - 1)):
#        inputFileName = sys.argv[i + 1]
#        print inputFileName
#   elif (sys.argv[i] == '-o' and i < (len(sys.argv) - 1)):
#        outputFileName = sys.argv[i + 1]
##

##
# rnMask = 0x3E0  # 1st argument ARM Rn
# rmMask = 0x1F0000  # second argument ARM Rm
# rdMask = 0x1F  # destination ARM Rd
# imMask = 0x3FFC00  # ARM I Immediate
# shmtMask = 0xFC00  # ARM ShAMT
# addrMask = 0x1FF000  # ARM address for ld and st
# addr2Mask = 0xFFFFE0  # addr for CB format
# imsftMask = 0x600000  # shift for IM format
# imdataMask = 0x1FFFe0  # data for IM type
# # last5Mask - 0x7C0
##


class Dissassemble:

    def __init__(self):
        self.opcode_dec = []
        self.args_dec = []      # list of tuples containing args
        self.data_dec = []      # list of data values
        self.instr_dec = []

    def get_opcode_dec(self):
        self.opcode_dec = [(0xFFE00000 & i) >> 21 for i in self.instr_dec]

    def run(self):
        filename = 'test2_bin.txt'

        with open(filename) as f:
            self.instr_dec = [int(line.rstrip('\n'), 2) for line in f]

        self.get_opcode_dec()

        print(self.instr_dec)      #debug to console
        print(self.opcode_dec)     #debug to console

        self.output()

    def output(self):
        with open('team13_out_dis.txt', 'w') as f:
            for i in self.instr_dec:
                f.write('{}\n'.format(i))
        


if __name__ == "__main__":

    d = Dissassemble()
    d.run()


