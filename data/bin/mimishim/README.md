# mimishim

mimishim.dll is a reflective DLL that shims Koadic C3 and powerkatz.dll

Screenshot: http://shellcorp.org/koadikatz.png

### Methodology

Several issues arise when trying to use the "well-known" powerkatz.dll straight from a Koadic job.

1. We might be an x86 process on x64 CPU, you need to be in the same arch process for mimikatz to work correctly
2. We cannot reflectively load with a stub in JScript (Empire does it all in PowerShell) because we will run out of instructions ("A script is taking too long, want to continue?" dialog)
3. Even if powerkatz.dll just used normal reflective injection instead, Wow64->x64 still requires a ton of shellcode sorcery

So we have this shim DLL that has the reflective loader built in and uses a pre-calculated offset to minimize the JScript code.

DllMain basically does the following:

1. Detect if WOW64 Process (aka x86)
2. If WOW64, create an x64 process and inject x64 version of self into it (aforementioned sorcery)
3. If x64, reflectively load powerkatz.dll and call it.
4. DllMain's lpParam contains strings of UUIDs, the mimikatz command to run, and the C&C callhome URL.

There is also network code built-in so it can report back to the C&C server.

### Build Notes

- Build x64 version first
- Get pre-calculated offset via inject.x64.exe
- Insert x64 offset into koadic_process.c
- Build x86
- Get pre-calculated offset via inject.exe
- Insert x86 offset into mimikatz_dynwrapx.py
