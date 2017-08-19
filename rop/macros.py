include("../ropdb/DB.py")

def garbage(n):
    for i in range(n):
        add_word(0xDEAC0DE)

def memcpy(dest, src, size):
    SET_LR(NOP)
    pop(r0=dest, r1=src, r2=size)
    add_word(MEMCPY)

def memcmp(buf1, buf2, size):
    SET_LR(NOP)
    pop(r0=buf1, r1=buf2, r2=size)
    add_word(MEMCMP)

@pop_macro
def POP_R0(r0):
    add_word(POP_R0PC)
    add_word(r0)

@pop_macro
def POP_R1(r1):
    add_word(POP_R1PC)
    add_word(r1)

@pop_macro
def POP_R4(r4):
    add_word(POP_R4PC)
    add_word(r4)

@pop_macro
def POP_R2R3R4R5R6(r2, r3, r4, r5, r6):
    add_word(POP_R2R3R4R5R6PC)
    add_word(r2)
    add_word(r3)
    add_word(r4)
    add_word(r5)
    add_word(r6)

def SET_LR(lr):
    POP_R1(NOP)
    add_word(POP_R4LR_BX_R1)
    add_word(0xDEADC0DE) #r4 garbage
    add_word(lr)

def deref_to_r0(addr):
    POP_R0(addr)
    add_word(LDR_R0R0_POP_R4PC)
    add_word(0xDEADC0DE)

def add_r0(value):
    POP_R1(value)
    add_word(ADD_R0R0R1_POP_R4PC)
    add_word(0xDEADC0DE)

def compare_r0_0():
    add_word(CMP_R0_0_MOVNE_R0_1_POP_R4PC)
    add_word(0xDEADC0DE)

def store(value, addr):
    pop(r0=value, r4=addr)
    add_word(STR_R0R4_POP_R4PC)
    add_word(0xDEADC0DE)

def store_if_equal(value, addr):
    pop(r0=value, r4=addr-4)
    add_word(STREQ_R0R4_4_POP_R4R5R6PC)
    garbage(3)

def store_r0(addr):
    POP_R4(addr)
    add_word(STR_R0R4_POP_R4PC)
    add_word(0xDEADC0DE)

def sleep(tl, th=0):
    SET_LR(NOP)
    pop(r0=tl, r1=th)
    add_word(SVC_SLEEPTHREAD)

def flush_dcache(addr, size):
    pop(r0=addr, r1=size)
    add_word(GSPGPU_FLUSHDATACACHE_WRAPPER+0x4)
    garbage(3)
