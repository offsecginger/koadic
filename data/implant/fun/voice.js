try
{
    var voiceObj = new ActiveXObject("sapi.spvoice");

    for (var i = 0; i < 50; ++i)
    {
        Koadic.WS.SendKeys(String.fromCharCode(0xAF));
    }
    voiceObj.Speak("~MESSAGE~");
    Koadic.work.report("");
}
catch (e)
{
    Koadic.work.error(e);
}
Koadic.exit();
