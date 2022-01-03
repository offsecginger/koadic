sub EnableRDesktop
    Const HKEY_LOCAL_MACHINE = &H80000002
    Const ERROR_ACCESS_DENIED = 5
    strKeyPath = "System\CurrentControlSet\Control\Terminal Server"
    strValueName = "fDenyTsConnections"
    Set objRegistry = GetObject("winmgmts:\\.\root\default:StdRegProv")
    objRegistry.CreateKey HKEY_LOCAL_MACHINE, strKeyPath
    objRegistry.SetDWORDValue HKEY_LOCAL_MACHINE, strKeyPath, strValueName, ~MODE~
    objRegistry.GetDWORDValue HKEY_LOCAL_MACHINE, strKeyPath, strValueName, dwValue
    if dwValue <> ~MODE~ then
        err.raise ERROR_ACCESS_DENIED
    end if
end sub

EnableRDesktop
KoReportWork ""
KoExit
