class CPU:
    def __init__(self, mem_size=256):
        self.mem = [0]*mem_size
        self.A = self.B = self.PC = self.OUT = 0
        self.Z = self.C = self.N = 0
        self.halt = False

    def flags_from(self, val, carry=0):
        self.Z = int((val & 0xFF) == 0)
        self.N = (val >> 7) & 1
        self.C = carry & 1

    def fetch(self):
        op = self.mem[self.PC]; self.PC = (self.PC+1) & 0xFF
        return op

    def step(self):
        op = self.fetch()
        if op == 0x00:  # NOP
            pass
        elif op == 0x01:  # LDI A,#imm
            self.A = self.fetch(); self.flags_from(self.A)
        elif op == 0x02:  # LDI B,#imm
            self.B = self.fetch(); self.flags_from(self.B)
        elif op == 0x03:  # LDA addr
            addr = self.fetch(); self.A = self.mem[addr]; self.flags_from(self.A)
        elif op == 0x04:  # STA addr
            addr = self.fetch(); self.mem[addr] = self.A
        elif op == 0x05:  # ADD B
            s = self.A + self.B
            self.A = s & 0xFF; self.flags_from(self.A, carry=(s>>8))
        elif op == 0x06:  # SUB B
            s = (self.A - self.B) & 0x1FF
            self.A = s & 0xFF; self.flags_from(self.A, carry=(s>>8))
        elif op == 0x07:  # AND B
            self.A &= self.B; self.flags_from(self.A)
        elif op == 0x08:  # OR B
            self.A |= self.B; self.flags_from(self.A)
        elif op == 0x09:  # XOR B
            self.A ^= self.B; self.flags_from(self.A)
        elif op == 0x0A:  # NOT A
            self.A = (~self.A) & 0xFF; self.flags_from(self.A)
        elif op == 0x0B:  # JMP addr
            self.PC = self.fetch()
        elif op == 0x0C:  # JZ addr
            addr = self.fetch(); 
            if self.Z: self.PC = addr
        elif op == 0x0D:  # JC addr
            addr = self.fetch(); 
            if self.C: self.PC = addr
        elif op == 0x0E:  # IN
            self.A = 0  # stub; replace with input device
            self.flags_from(self.A)
        elif op == 0x0F:  # OUT
            self.OUT = self.A
        elif op == 0xFF:  # HLT
            self.halt = True
        else:
            raise ValueError(f"Unknown opcode {op:#02x}")

    def run(self, max_steps=10000):
        steps = 0
        while not self.halt and steps < max_steps:
            self.step(); steps += 1
        return steps

# demo program: count 0..255 on OUT
prog = [
    0x01, 0x00,       # LDI A,#0
    0x0F,             # OUT
    0x05,             # ADD B (B will be 1 after we init it)
    0x0F,             # OUT
    0x0B, 0x03        # JMP 3
]
# insert LDI B,#1 at start
prog = [0x02, 0x01] + prog

cpu = CPU()
cpu.mem[:len(prog)] = prog
cpu.run(200)
print("OUT =", cpu.OUT, "A =", cpu.A)
