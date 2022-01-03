function TestPortMSHTA(url)
{
    var ret = {};
    ret.status = "unknown";
    ret.errno = -1;

    var ABNORMAL_TERMINATION = -2147012866;
    var UNSUPPORTED_PORT = -2147012795;
    var CONNECTION_ERROR = -2147012867;
    var WRONG_PROTOCOL = -2147012744;
    var OPERATION_CANCELED = -2147012879;

    try
    {
        var objHTTP = new ActiveXObject("WinHttp.WinHttpRequest.5.1");
        objHTTP.Open("GET", url, true);
        objHTTP.Send();
        objHTTP.WaitForResponse(~TIMEOUT~);

        ret.status = "open";
        ret.errno = 0;
    }
    catch(err)
    {
        ret.errno = err.number;

        if (err.number == UNSUPPORTED_PORT)
            ret.status = "unsupported";
        else if (err.number == CONNECTION_ERROR)
            ret.status = "closed";
        else if (err.number == WRONG_PROTOCOL || err.number == ABNORMAL_TERMINATION || err.number == OPERATION_CANCELED)
            ret.status = "open";
    }

    return ret;
}

function TestPort(ip, port)
{
    var url = "http://" + ip + ":" + port;
    return TestPortMSHTA(url);
}


~RHOSTSARRAY~

~RPORTSARRAY~

function status_string(status, ip, port, err)
{
    return status + "\n" + ip + "\n" + port + "\n" + err;
}

try
{
    for (var idx in ips)
    {
        var ip = ips[idx];
        var test = "closed";
        var testerrno = 0;
        if (~CHECKLIVE~)
        {
            // ghetto check if the IP is up
            var testport = TestPort(ip, 1);
            test = testport.status;
            testerrno = testport.errno;
        }
        if (test == "closed")
        {
            for (var pdx in ports)
            {
                var port = ports[pdx];
                var ret = TestPort(ip, port);
                Koadic.work.report(status_string(ret.status, ip, port, ret.errno));
            }
        }
        else
        {
            Koadic.work.report(status_string("not up", ip, 1, testerrno));
        }
    }

    Koadic.work.report("done");
}
catch(e)
{
    Koadic.work.error(e);
}

Koadic.exit();
