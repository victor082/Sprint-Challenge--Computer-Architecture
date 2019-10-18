import sys


class CPU:

    def __init__(self):
        self.register = [0] * 8  # making 8 registers (R0 - R7)
        self.pc = 0  # program counter
        self.IR = 0
        self.ram = [0] * 256
        self.SP = 7  # used for stack pointer
        self.opcodes = {
            'LDI': 0b10000010,
            'PRN': 0b01000111,
            'HLT': 0b00000001,
            'MUL': 0b10100010,
            'PUSH': 0b01000101,
            'POP': 0b01000110,
            'CALL': 0b01010000,
            'RET': 0b00010001,
            'ADD': 0b10100000,
            'CMP': 0b10100111,
            'JMP': 0b01010100,
            'JEQ': 0b01010101,
            'JNE': 0b01010110,

        }  # operation codes
        self.flag = 0b00000000  # changes based on the operands given to the CMP opcode

    def load(self, file_name):

        address = 0

        program = []

        if file_name is None:
            print("Error: File not working.")
            sys.exit(1)

        try:
            with open(file_name, 'r') as f:
                for line in f:
                    comment_split = line.split('#')
                    num = comment_split[0]

                    try:
                        x = int(num, 2)
                    except ValueError:
                        continue
                    print(f"{x:08b}: {x:d}")
                    program.append(x)
        except ValueError:
            print(f"File not found")

        for instruction in program:
            self.ram[address] = instruction
            address += 1

    def alu(self, op, reg_a, reg_b):

        if op == self.opcodes['ADD']:  # ADD
            self.register[reg_a] += self.register[reg_b]
            self.pc += 3

        elif op == self.opcodes['MUL']:  # MUL
            self.register[reg_a] *= self.register[reg_b]
            self.pc += 3

        elif op == self.opcodes['CMP']:  # CMP
            # E (Equal) set the first from the right to 1
            # G (Greater than) set second from the right to 1
            # L (Less than) set third from the right to 1

            self.flag = 0b00000000

            if reg_a == reg_b:  # if a == b, set E to 1
                self.flag = 0b00000001

            elif reg_a < reg_b:  # if a < b, set L to 1
                self.flag = 0b00000100

            elif reg_a > reg_b:  # if a > b, set G to 1
                self.flag = 0b00000010

            # else:  # else, set to 0
            #     self.flag = 0b00000000

        else:
            raise Exception("Unspoorted ALU operation")

    def trace(self):

        print(f"TRACE: %02X | %02X %02X %02X |" % (
            self.pc,
            # self.fl,
            # self.ie,
            self.ram_read(self.pc),
            self.ram_read(self.pc + 1),
            self.ram_read(self.pc + 2)
        ), end='')

        for i in range(8):
            print(" %02X" % self.reg[i], end='')

        print()

    def run(self):
        running = True

        while running:

            # Instruction register, ccontains a copy of the currently executing instruction
            IR = self.ram[self.pc]

            if IR == self.opcodes['LDI']:  # LDI
                num = self.ram[self.pc + 1]
                reg = self.ram[self.pc + 2]

                self.register[num] = reg
                self.pc += 3

            elif IR == self.opcodes['PRN']:  # PRN
                reg = self.ram[self.pc + 1]
                print(self.register[reg])
                self.pc += 2

            elif IR == self.opcodes['HLT']:  # HLT
                running = False
                self.pc += 1

            elif IR == self.opcodes['CALL']:
                # we want to push the return address on the stack
                self.register[self.SP] -= 1  # the stack push
                self.ram[self.register[self.SP]] = self.pc + 2

                # The program counter is set to the address stored in the given register
                reg = self.ram[self.pc + 1]
                # We then jump to that location in the RAM and execute the first instruction
                self.pc = self.register[reg]

            elif IR == self.opcodes['RET']:
                # return the subroutine
                self.pc = self.ram[self.register[self.SP]]
                # pop the value from the top of the stack
                self.register[self.SP] += 1

            elif IR == self.opcodes['PUSH']:
                reg = self.ram[self.pc + 1]
                val = self.register[reg]
                #  Got to decrement the Stack pointer.
                self.register[self.SP] -= 1
                # Copy the value in the given register to the address pointed to by Stack pointer
                self.ram[self.register[self.SP]] = val
                self.pc += 2

            elif IR == self.opcodes['POP']:
                reg = self.ram[self.pc + 1]
                val = self.ram[self.register[self.SP]]
                # Copy the value from the address pointed to by Stack pointer to the given register
                self.register[reg] = val
                # Increment SP
                self.register[self.SP] += 1
                self.pc += 2

            elif IR == self.opcodes['ADD']:
                reg_a = self.ram[self.pc + 1]
                reg_b = self.ram[self.pc + 2]
                self.alu(IR, reg_a, reg_b)

            elif IR == self.opcodes['MUL']:
                reg_a = self.ram[self.pc + 1]
                reg_b = self.ram[self.pc + 2]
                self.alu(IR, reg_a, reg_b)

            elif IR == self.opcodes['CMP']:
                num = self.ram[self.pc + 1]
                reg = self.ram[self.pc + 2]
                self.alu(IR, num, reg)
                self.pc += 3

            elif IR == self.opcodes['JMP']:
                # Jump to the address stored in the given register
                # Set the program count to the address stored in the given register
                op_a = self.ram[self.pc + 1]

                self.pc = self.register[op_a]

            elif IR == self.opcodes['JEQ']:
                # if the E (very right) is true, jump to the address stored in the given register
                op_a = self.ram[self.pc + 1]

                if self.flag == 0b00000001:
                    self.pc = self.register[op_a]
                else:
                    self.pc += 2

            elif IR == self.opcodes['JNE']:
                # if the E (very right) is false, jump to the address stored in the given register
                # Asking if the E flag is clear specfically, which means equal to 0 or false
                op_a = self.ram[self.pc + 1]

                if ((self.flag == 0b00000001) == 0):
                    self.pc = self.register[op_a]
                else:
                    self.pc += 2
            else:
                print(f"Unknown IR: {IR}")
                sys.exit(1)

    def ram_read(self, MAR):
        # Read from RAM
        # Accepts the address to read and return the value stored there
        return self.ram[MAR]

    # accept a value to write, and the addres to write it to
    def ram_write(self, MAR, MDR):
        self.ram[MAR] = MDR
