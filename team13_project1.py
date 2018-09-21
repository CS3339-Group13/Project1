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
# MOVZ        | 110100101   | 9         |  1684    | 1687     | IM
# MOVK        | 111100101   | 9         |  1940    | 1943     | IM
# LSR         | 11010011010 | 11        |  1690    |          | R
# LSL         | 11010011011 | 11        |  1691    |          | R
# STUR        | 11111000000 | 11        |  1984    |          | D
# LDUR        | 11111000010 | 11        |  1986    |          | D
# BREAK         1 11111 10110 11110 11111 11111 100111

##
# command line decode
# for i in range(len(sys.argv)):
#    if (sys.argv[i] == '-i' and i < (len(sys.argv) - 1)):
#        inputFileName = sys.argv[i + 1]
#        print inputFileName
#   elif (sys.argv[i] == '-o' and i < (len(sys.argv) - 1)):
#        outputFileName = sys.argv[i + 1]
##

# CONSIDER INVALID INSTRUCTIONS - output sys error of some sort, say what the invalid instruction was, what line, etc


class Disassemble:
    inst_spacing = [0, 8, 11, 16, 21, 26, 32]

    def __init__(self):
        self.opcode_dec = []
        self.args_dec = []      # list of tuples containing args
        self.data_dec = []      # list of data values
        self.lines_dec = []
        self.address_start = 96

        self.opcode_dict = {
            (160, 191)  : ['B', 'B'],
            (1104, 1104): ['R', 'AND'],
            (1112, 1112): ['R', 'ADD'],
            (1160, 1161): ['I', 'ADDI'],
            (1360, 1360): ['R', 'ORR'],
            (1440, 1447): ['CB', 'CBZ'],
            (1448, 1455): ['CB', 'CBNZ'],
            (1624, 1624): ['R', 'SUB'],
            (1672, 1673): ['I', 'SUBI'],
            (1684, 1687): ['IM', 'MOVZ'],
            (1940, 1943): ['IM', 'MOVK'],
            (1690, 1690): ['R', 'LSR'],
            (1691, 1691): ['R', 'LSL'],
            (1984, 1984): ['D', 'STUR'],
            (1986, 1986): ['D', 'LDUR'],
            (2038, 2038): ['BREAK', 'BREAK']
        }

    def run(self):
        self.__read_file('custom_input.txt')

        self.__process_instructions()

    def __read_file(self, filename):
        with open(filename) as f:
            self.lines_dec = [int(line.rstrip('\n'), 2) for line in f]

    def __process_instructions(self):
        data = False
        address = self.address_start
        for c, i in enumerate(self.lines_dec):
            if not data:
                print(Disassemble.get_bin_spaced(i) + '\t' + str(address) + '\t', end='')

                # calculate and add opcodes to list
                opcode_dec = self.get_bits_range(31, 21, i)
                self.opcode_dec.append(opcode_dec)

                # loop through known opcodes
                for (low, high), inst_info in self.opcode_dict.items():
                    # call appropriate instruction type function
                    if low <= opcode_dec <= high:
                        f = getattr(self, 'process_' + inst_info[0])
                        print(f(i, inst_info[1]))

                if i == int('0xFEDEFFE7', 16):
                    data = True
            else:
                bin_str = '{0:032b}'.format(i)
                print('{}\t{}\t{}'.format(bin_str, address, Disassemble.tc_to_dec(bin_str)))

            address += 4

    @staticmethod
    def tc_to_dec(bin_str):
        dec = int(bin_str, 2)
        # if positive, just convert to decimal
        if bin_str[0] == 0:
            return dec
        # if negative, flip bits and add 1, then multiply decimal by -1
        else:
            return -1 * ((dec ^ 0xFFFFFFFF) + 1)

    @staticmethod
    def get_bits_range(high, low, inst):
        mask_str = '0' * (31 - high) + '1' * (high - low + 1) + '0' * low
        mask_int = int(mask_str, 2)
        return (inst & mask_int) >> low

    @staticmethod
    def get_bin_spaced(inst_dec):
        inst_bin = '{0:032b}'.format(inst_dec)
        inst_spaced = ''
        for start, stop in zip(Disassemble.inst_spacing, Disassemble.inst_spacing[1:]):
            inst_spaced += inst_bin[start:stop] + ' '
        return inst_spaced

    # opcode    Rm  shamt   Rn  Rd
    # 11        5   6       5   5
    @staticmethod
    def process_R(inst_dec, inst_name):
        opcode = Disassemble.get_bits_range(31, 21, inst_dec)
        Rm = Disassemble.get_bits_range(20, 16, inst_dec)
        shamt = Disassemble.get_bits_range(15, 10, inst_dec)
        Rn = Disassemble.get_bits_range(9, 5, inst_dec)
        Rd = Disassemble.get_bits_range(4, 0, inst_dec)

        if inst_name == 'LSL' or inst_name == 'LSR':
            inst_str = '{}\tR{}, R{}, R{}'.format(inst_name, Rd, Rn, shamt)
        else:
            inst_str = '{}\tR{}, R{}, R{}'.format(inst_name, Rd, Rn, Rm)

        return inst_str

    # opcode    offset  op2 Rn  Rt
    # 11        9       2   5   5
    @staticmethod
    def process_D(inst_dec, inst_name):
        # opcode = Disassemble.get_bits_range(31, 21, inst_dec)
        offset = Disassemble.get_bits_range(20, 12, inst_dec)
        # op2 = Disassemble.get_bits_range(11, 10, inst_dec)
        Rn = Disassemble.get_bits_range(9, 5, inst_dec)
        Rt = Disassemble.get_bits_range(4, 0, inst_dec)
        return '{}\tR{}, [R{}, #{}]'.format(inst_name, Rt, Rn, offset)

    # opcode    immediate   Rn  Rd
    # 10        12          5   5
    @staticmethod
    def process_I(inst_dec, inst_name):
        # opcode = Disassemble.get_bits_range(31, 22, inst_dec)
        immediate = Disassemble.get_bits_range(21, 10, inst_dec)
        Rn = Disassemble.get_bits_range(9, 5, inst_dec)
        Rd = Disassemble.get_bits_range(4, 0, inst_dec)
        return '{}\tR{}, R{}, #{}'.format(inst_name, Rd, Rn, immediate)

    # opcode    address
    # 6         26
    @staticmethod
    def process_B(inst_dec, inst_name):
        # opcode = Disassemble.get_bits_range(31, 24, inst_dec)
        address = Disassemble.get_bits_range(23, 0, inst_dec)
        return '{}\t#{}'.format(inst_name, address)

    # opcode    offset      Rt
    # 8         19          5
    @staticmethod
    def process_CB(inst_dec, inst_name):
        # opcode = Disassemble.get_bits_range(31, 24, inst_dec)
        offset = Disassemble.get_bits_range(23, 5, inst_dec)
        Rt = Disassemble.get_bits_range(4, 0, inst_dec)
        return '{}\tR{}, R{}'.format(inst_name, Rt, offset)

    # opcode        immediate   Rd
    # 9         2   18          5
    @staticmethod
    def process_IM(inst_dec, inst_name):
        # opcode = Disassemble.get_bits_range(31, 23, inst_dec)
        shift = Disassemble.get_bits_range(22, 21, inst_dec)
        immediate = Disassemble.get_bits_range(20, 5, inst_dec)
        Rd = Disassemble.get_bits_range(4, 0, inst_dec)
        return '{}\tR{}, {}, LSL {}'.format(inst_name, Rd, immediate, shift * 16)

    @staticmethod
    def process_BREAK(inst_dec, inst_name):
        return inst_name

    def __output(self):
        with open('team13_out_dis.txt', 'w') as f:
            for i in self.lines_dec:
                f.write('{}\n'.format(i))


if __name__ == "__main__":
    d = Disassemble()
    d.run()
