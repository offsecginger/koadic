sub DoVoice
    dim speechobject
    set speechobject=createobject("sapi.spvoice")

    For i = 0 To 50
        kows.SendKeys(chr(&hAF))
    Next

    speechobject.speak "~MESSAGE~"
end sub

DoVoice
KoReportWork ""
KoExit
