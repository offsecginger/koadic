dim kotimeout
kotimeout = ~TIMEOUT~

function TestPortWscript(url)
    on error resume next
    Set x = createobject("Microsoft.XMLHTTP")
    x.open "GET", url, true
    x.send
    'MsgBox url
    KoSleep kotimeout

    status = x.status
    if err.number = -2147467259 then
        TestPortWscript = "open"
        exit function
    end if

    if x.status < 1000 or x.status = 12031 then
        TestPortWscript = "open"
        exit function
    end if
    if status = 12029 then
        TestPortWscript = "closed"
        exit function
    end if
    if x.status = 12005 then
            TestPortWscript = "unsupported"
            exit function
    end if

    TestPortWscript = "unknown"
end function

function TestPortMSHTA(url)
{
    var ABNORMAL_TERMINATION = -2147012866
    var UNSUPPORTED_PORT = -2147012795
    var CONNECTION_ERROR = -2147012867
    var WRONG_PROTOCOL = -2147012744
    var OPERATION_CANCELED = -2147012879

    try
    {
        var objHTTP = new ActiveXObject("WinHttp.WinHttpRequest.5.1")
        objHTTP.Open("GET", url, True)
        objHTTP.Send();
        objHTTP.WaitForResponse(~TIMEOUT~)

        return "open";
    }
    catch(err)
    {
        if (err.number == UNSUPPORTED_PORT)
            return "unsupported";

        if (err.number == CONNECTION_ERROR)
            return "closed";

        if (err.number == WRONG_PROTOCOL || err.number == ABNORMAL_TERMINATION || err.number == OPERATION_CANCELED)
            return "open";
    }

    return "unknown";
}

function TestPort(ip, port)
{
    var url = "http://" + ip + ":" + port;
    if (Koadic.isHTA())
      return TestPortMSHTA(url)
    else
      TestPort = TestPortWscript(url)
    end if
}
end function


~RHOSTS~

~RPORTS~


for each ip in ips
    ' ghetto check if the IP is up
    if TestPort(ip, 0) = "closed" then
        for each port in ports
            data = TestPort(ip, port)
            errno = hex(err.number)
            data = data & vbcrlf & ip & vbcrlf & port & vbcrlf & errno
            KoReportWork data
        next
    else
        errno = hex(err.number)
        KoReportWork "not up" & vbcrlf & ip & vbcrlf & "0" & vbcrlf & "-1"
    end if
next

KoReportWork "done"

KoExit
