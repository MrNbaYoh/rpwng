#include "utils.h"
#include "imports.h"

void* memset(void *ptr, int value, size_t num)
{
  u8 *p = ptr;
  while (num)
  {
    *p++ = value;
    num--;
  }

	return ptr;
}

void* memcpy(void *destination, const void *source, size_t num)
{
  u8 *dest = destination;
  u8 *src  = (u8*)source;
  while (num)
  {
    *dest++ = *src++;
    num--;
  }

	return destination;
}

int memcmp(void *ptr1, void *ptr2, size_t num)
{
	for(; num--; ptr1++, ptr2++)
		if(*(u8*)ptr1 != *(u8*)ptr2)
			return *(u8*)ptr1-*(u8*)ptr2;
	return 0;
}

Result gspwn(void* dst, void* src, u32 size)
{
	u32 gxCommand[] =
	{
		0x00000004, //cmd header (SetTextureCopy)
		(u32)src,
		(u32)dst,
		size,
		0xFFFFFFFF, //dim in
		0xFFFFFFFF, //dim out
		0x00000008, //flags
		0x00000000
	};

	return _GSPGPU_GxTryEnqueue(sharedGspCmdBuf, gxCommand);
}

Result _GSPGPU_SetBufferSwap(Handle handle, u32 screenId, GSPGPU_FramebufferInfo framebufferInfo)
{
	Result ret = 0;
	u32* cmdbuf = getThreadCommandBuffer();

	cmdbuf[0] = 0x0050200;
	cmdbuf[1] = screenId;
	memcpy(&cmdbuf[2], &framebufferInfo, sizeof(GSPGPU_FramebufferInfo));

	if((ret = svcSendSyncRequest(handle))) return ret;

	return cmdbuf[1];
}
