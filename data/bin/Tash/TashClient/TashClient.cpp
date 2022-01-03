// TashClient.cpp : Defines the entry point for the console application.
//

#include "stdafx.h"

#include <iostream>

void ErrorDescription(HRESULT hr)
{
	TCHAR* szErrMsg;
	if (FormatMessage(FORMAT_MESSAGE_ALLOCATE_BUFFER| FORMAT_MESSAGE_FROM_SYSTEM, NULL, hr, 
				MAKELANGID(LANG_NEUTRAL, SUBLANG_DEFAULT), (LPTSTR)&szErrMsg, 0, NULL) != 0)
	{
		std::wcout << szErrMsg << std::endl;
		LocalFree(szErrMsg);
	}
	else
	{
		std::cout << "Could not find a description for error 0x" << std::hex << hr << std::dec << std::endl;
	}
}

int _tmain(int argc, _TCHAR* argv[])
{
	CoInitializeEx(0, COINIT_MULTITHREADED);

	ACTCTX actCtx = { 0 };
	actCtx.cbSize = sizeof(ACTCTX);
	actCtx.lpSource = L"Tash.X.manifest";

	HANDLE hCtx = CreateActCtx(&actCtx);

	if (hCtx != INVALID_HANDLE_VALUE)
	{
		ULONG_PTR cookie;
		if (::ActivateActCtx(hCtx, &cookie))
		{
			{
				ITashLoaderPtr ptr;
				HRESULT hr = ptr.CreateInstance(__uuidof(TashLoader));

				if (SUCCEEDED(hr))
				{
					BSTR sCode = SysAllocString(L"\xcc\x90\x90\xc3");
					std::cout << ptr->Load(sCode, (BSTR)NULL, 1) << std::endl;

					SysFreeString(sCode);		
				}

				ErrorDescription(hr);
			}

			DeactivateActCtx(0, cookie);
		}
	}


	CoUninitialize();

   return 0;
}

