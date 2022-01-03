#pragma once

#include <Windows.h>

#include "koadic_types.h"

#define MIMISHIM_X64_OFFSET 7620


BOOL koadic_create_sysnative_process(LPCSTR program, LPDWORD dwPID);
BOOL koadic_fork_x64(koadic_shim_parsed *parsed, LPWSTR lpParam, char *data, DWORD dwDataSize);
