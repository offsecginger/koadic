#pragma once

#ifndef WIN32_LEAN_AND_MEAN
#define WIN32_LEAN_AND_MEAN
#endif
#include <Windows.h>

HMODULE WINAPI powerkatz_reflective_load(LPVOID lpPowerkatz, LPVOID lpParameter);
wchar_t * WINAPI powerkatz_invoke(HMODULE hPowerKatz, LPCWSTR input);