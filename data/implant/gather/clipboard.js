try
{
    var html = new ActiveXObject("htmlfile");
    var text = html.parentWindow.clipboardData.getData("text");
    Koadic.work.report(text);
}
catch (e)
{
    Koadic.work.error(e)
}

Koadic.exit();
