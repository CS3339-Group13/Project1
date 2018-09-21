# Instruction | OPCODE      | OP Size   | 11 bit OPCODE range | Instruction
#             |             | (base 10) | Start    | End      | Format
# ------------|-------------|-----------|----------|----------|-------------
# B           | 000101      | 6         |  160     | 191      | B
# AND         | 10001010000 | 11        |  1104    |          | R
# ADD         | 10001011000 | 11        |  1112    |          | R
# ADDI        | 1001000100  | 10        |  1160    | 1161     | I
# ORR         | 10101010000 | 11        |  1360    |          | R
# EOR         | 11101010000 | 11        |  1616    |          | R
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

# CONSIDER INVALID INSTRUCTIONS - output sys error of some sort, say what the invalid instruction was, what line, etc
from __future__ import print_function
import sys


class Disassemble:
    inst_spacing = [0, 8, 11, 16, 21, 26, 32]

    def __init__(self, input_file, output_file):
        self.input_file = input_file
        self.output_file = output_file

        self.processed_inst = {}
        self.processed_data = {}

        self.lines_dec = []     # holds raw line in decimal
        self.address = 96

        self.opcode_dict = {
            (0, 0)      : ['NOP', 'NOP'],
            (160, 191)  : ['B', 'B'],
            (1104, 1104): ['R', 'AND'],
            (1112, 1112): ['R', 'ADD'],
            (1160, 1161): ['I', 'ADDI'],
            (1360, 1360): ['R', 'ORR'],
            (1440, 1447): ['CB', 'CBZ'],
            (1448, 1455): ['CB', 'CBNZ'],
            (1616, 1616): ['R', 'EOR'],
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
        try:
            self.__read_file()
            self.__process_instructions()
        except ValueError as ve:
            print(ve, file=sys.stderr)

    def __read_file(self):
        line_num = 0
        with open(self.input_file) as f:
            for line in f:
                line = line.rstrip('\n')
                line_num += 1
                if len(line) != 32:
                    raise ValueError('Invalid instruction on line {}: \'{}\''.format(line_num, line))
                self.lines_dec.append(int(line, 2))

    def __process_instructions(self):
        out = open(self.output_file + '_dis.txt', 'w')
        data = False
        for line_num, line in enumerate(self.lines_dec):
            valid = False
            if not data:
                out.write(Disassemble.get_bin_spaced(line) + '\t' + str(self.address) + '\t')

                # calculate and add opcodes to list
                opcode_dec = self.get_bits_range(31, 21, line)

                # loop through known opcodes
                for (low, high), inst_info in self.opcode_dict.items():
                    # call appropriate instruction type function
                    if low <= opcode_dec <= high:
                        valid = True
                        f = getattr(self, 'process_' + inst_info[0])
                        out.write(f(line, inst_info[1]) + '\n')

                if not valid:
                    raise ValueError('Invalid instruction on line {}: \'{}\''.format(line_num, line))

                if line == int('0xFEDEFFE7', 16):
                    data = True

            else:
                out.write(self.process_data(line) + '\n')

            self.address += 4

    @staticmethod
    def tc_to_dec(bin_str):
        dec = int(bin_str, 2)
        # if positive, just convert to decimal
        if bin_str[0] == '0':
            return dec
        # if negative, flip bits and add 1, then multiply decimal by -1
        else:
            mask_str = '1' * len(bin_str)
            return -1 * ((dec ^ int(mask_str, 2)) + 1)

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
    def process_R(self, inst_dec, inst_name):
        opcode = Disassemble.get_bits_range(31, 21, inst_dec)
        Rm = Disassemble.get_bits_range(20, 16, inst_dec)
        shamt = Disassemble.get_bits_range(15, 10, inst_dec)
        Rn = Disassemble.get_bits_range(9, 5, inst_dec)
        Rd = Disassemble.get_bits_range(4, 0, inst_dec)

        self.processed_inst[self.address] = {
            'name': inst_name,
            'opcode': opcode,
            'Rm': Rm,
            'shamt': shamt,
            'Rn': Rn,
            'Rd': Rd
        }

        if inst_name == 'LSL' or inst_name == 'LSR':
            inst_str = '{}\tR{}, R{}, {}'.format(inst_name, Rd, Rn, shamt)
        else:
            inst_str = '{}\tR{}, R{}, R{}'.format(inst_name, Rd, Rn, Rm)

        return inst_str

    # opcode    offset  op2 Rn  Rt
    # 11        9       2   5   5
    def process_D(self, inst_dec, inst_name):
        opcode = Disassemble.get_bits_range(31, 21, inst_dec)
        offset = Disassemble.get_bits_range(20, 12, inst_dec)
        op2 = Disassemble.get_bits_range(11, 10, inst_dec)
        Rn = Disassemble.get_bits_range(9, 5, inst_dec)
        Rt = Disassemble.get_bits_range(4, 0, inst_dec)

        self.processed_inst[self.address] = {
            'name': inst_name,
            'opcode': opcode,
            'offset': offset,
            'op2': op2,
            'Rn': Rn,
            'Rt': Rt
        }

        return '{}\tR{}, [R{}, #{}]'.format(inst_name, Rt, Rn, offset)

    # opcode    immediate   Rn  Rd
    # 10        12          5   5
    def process_I(self, inst_dec, inst_name):
        opcode = Disassemble.get_bits_range(31, 22, inst_dec)
        immediate = Disassemble.tc_to_dec('{0:012b}'.format(Disassemble.get_bits_range(21, 10, inst_dec)))
        Rn = Disassemble.get_bits_range(9, 5, inst_dec)
        Rd = Disassemble.get_bits_range(4, 0, inst_dec)

        self.processed_inst[self.address] = {
            'name': inst_name,
            'opcode': opcode,
            'immediate': immediate,
            'Rn': Rn,
            'Rd': Rd
        }

        return '{}\tR{}, R{}, #{}'.format(inst_name, Rd, Rn, immediate)

    # opcode    address
    # 6         26
    def process_B(self, inst_dec, inst_name):
        opcode = Disassemble.get_bits_range(31, 24, inst_dec)
        address = Disassemble.get_bits_range(23, 0, inst_dec)

        self.processed_inst[self.address] = {
            'name': inst_name,
            'opcode': opcode,
            'address': address
        }

        return '{}\t#{}'.format(inst_name, address)

    # opcode    offset      Rt
    # 8         19          5
    def process_CB(self, inst_dec, inst_name):
        opcode = Disassemble.get_bits_range(31, 24, inst_dec)
        offset = Disassemble.get_bits_range(23, 5, inst_dec)
        Rt = Disassemble.get_bits_range(4, 0, inst_dec)

        self.processed_inst[self.address] = {
            'name': inst_name,
            'opcode': opcode,
            'offset': offset,
            'Rt': Rt
        }

        return '{}\tR{}, R{}'.format(inst_name, Rt, offset)

    # opcode        immediate   Rd
    # 9         2   18          5
    def process_IM(self, inst_dec, inst_name):
        opcode = Disassemble.get_bits_range(31, 23, inst_dec)
        shift = Disassemble.get_bits_range(22, 21, inst_dec)
        immediate = Disassemble.get_bits_range(20, 5, inst_dec)
        Rd = Disassemble.get_bits_range(4, 0, inst_dec)

        self.processed_inst[self.address] = {
            'name': inst_name,
            'opcode': opcode,
            'shift': shift,
            'immediate': immediate,
            'Rd': Rd
        }

        return '{}\tR{}, {}, LSL {}'.format(inst_name, Rd, immediate, shift * 16)

    def process_NOP(self, inst_dec, inst_name):
        bin_str = '{0:032b}'.format(inst_dec)
        if inst_dec != 0:
            raise ValueError('Invalid instruction on line {}: \'{}\''.format((self.address-96)/4, bin_str))
        self.processed_inst[self.address] = {
            'name': inst_name
        }
        return inst_name

    def process_BREAK(self, inst_dec, inst_name):
        self.processed_inst[self.address] = {
            'name': inst_name
        }

        return inst_name

    def process_data(self, dec):
        bin_str = '{0:032b}'.format(dec)
        tc_dec = Disassemble.tc_to_dec(bin_str)

        self.processed_data[self.address] = tc_dec

        return '{}\t{}\t{}'.format(bin_str, self.address, tc_dec)


if __name__ == "__main__":
    infile = ''
    outfile = ''

    for i in range(len(sys.argv)):
        if sys.argv[i] == '-i':
            infile = sys.argv[i + 1]
        elif sys.argv[i] == '-o':
            outfile = sys.argv[i + 1]

    d = Disassemble(infile, outfile)
    d.run()
