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
# MOVZ        | 110100101   | 9         |  1648    | 1687     | I
# MOVK        | 111100101   | 9         |  1940    | 1943     | I
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

# CONSIDER INVALID INSTRUCTIONS - output sys error of some sort, say what the invalid instruction was, what line, etc


class Dissassemble:

    def __init__(self):
        self.opcode_dec = []
        self.args_dec = []      # list of tuples containing args
        self.data_dec = []      # list of data values
        self.inst_dec = []

        self.opcode_dict = {
            (160, 191)  : 'B',
            (1104, 1104): 'R',
            (1112, 1112): 'R',
            (1160, 1161): 'I',
            (1360, 1360): 'R',
            (1440, 1447): 'CB',
            (1448, 1455): 'CB',
            (1624, 1624): 'R',
            (1672, 1673): 'I',
            (1648, 1687): 'I',
            (1940, 1943): 'I',
            (1690, 1690): 'R',
            (1691, 1691): 'R',
            (1984, 1984): 'R',
            (1986, 1986): 'D'
        }

    @staticmethod
    def get_opcode_dec(inst_dec):
        return (0xFFE00000 & inst_dec) >> 21

    def process_instructions(self):
        for i in self.inst_dec:
            # calculate and add opcodes to list
            opcode_dec = self.get_opcode_dec(i)
            self.opcode_dec.append(opcode_dec)

            # loop through known opcodes
            for (low, high), inst_type in self.opcode_dict.items():
                # call appropriate instruction type function
                if low <= opcode_dec <= high:
                    f = getattr(self, 'process_' + inst_type)
                    f(i)

    @staticmethod
    def process_R(inst_dec):
        print('R')

    @staticmethod
    def process_D(inst_dec):
        print('D')

    @staticmethod
    def process_I(inst_dec):
        print('I')

    @staticmethod
    def process_B(inst_dec):
        print('B')

    @staticmethod
    def process_CB(inst_dec):
        print('CB')

    def run(self):
        filename = 'test2_bin.txt'

        with open(filename) as f:
            self.inst_dec = [int(line.rstrip('\n'), 2) for line in f]

        # print(self.inst_dec)      #debug to console
        # print(self.opcode_dec)     #debug to console
        #
        # self.output()

        self.process_instructions()

    def output(self):
        with open('team13_out_dis.txt', 'w') as f:
            for i in self.inst_dec:
                f.write('{}\n'.format(i))


if __name__ == "__main__":

    d = Dissassemble()
    d.run()
