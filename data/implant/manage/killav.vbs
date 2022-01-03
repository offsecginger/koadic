Dim objWMIService, objProcess, colProcess
Dim strComputer, strList

Set objWMIService = GetObject("winmgmts:{impersonationLevel=impersonate}!\\.\root\cimv2")

Set colProcess = objWMIService.ExecQuery("Select * from Win32_Process")

For Each objProcess in colProcess
  strList = strList & vbCr & objProcess.Name
Next

MsgBox strList
