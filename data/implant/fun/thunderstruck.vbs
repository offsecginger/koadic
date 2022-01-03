Set ie = CreateObject("InternetExplorer.Application")
ie.Visible = 0
ie.Navigate2 "~VIDEOURL~"

For i = 0 To 50
    kows.SendKeys(chr(&hAF))
Next

KoSleep 90

KoExit
