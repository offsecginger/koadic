try
{
    var path = "System\\CurrentControlSet\\Control\\Terminal Server";
    var key = "fDenyTsConnections";

    Koadic.registry.write(Koadic.registry.HKLM, path, key, ~MODE~, Koadic.registry.DWORD);
    var out = Koadic.registry.read(Koadic.registry.HKLM, path, key, Koadic.registry.DWORD);

    if (out.uValue != ~MODE~)
        throw new Error("Unable to write to registry key.");

    Koadic.work.report("");
}
catch(e)
{
    Koadic.work.error(e);
}

Koadic.exit()
