function ParseUsers(results)
{
    var retstring = "";
    var parse1 = results.split("-------\r\n")[1].split("The command completed")[0];
    var parse2 = parse1.split("\r\n");
    var tmp = [];
    for(var i = 0; i < parse2.length; i++)
    {
        tmp = parse2[i].split(" ");
        for(var j = 0; j < tmp.length; j++)
        {
            if(tmp[j])
            {
                retstring += tmp[j].toLowerCase() + "___";
            }
        }
    }
    return retstring;
}

function ParsePasswordPolicy(results)
{
    var retstring = "";
    retstring += results.split("time expires?:")[1].split("\r\n")[0].replace(/^\s+|\s+$/g, '') + "___";
    retstring += results.split("Minimum password age (days):")[1].split("\r\n")[0].replace(/^\s+|\s+$/g, '') + "___";
    retstring += results.split("Maximum password age (days):")[1].split("\r\n")[0].replace(/^\s+|\s+$/g, '') + "___";
    retstring += results.split("length:")[1].split("\r\n")[0].replace(/^\s+|\s+$/g, '') + "___";
    retstring += results.split("maintained:")[1].split("\r\n")[0].replace(/^\s+|\s+$/g, '') + "___";
    retstring += results.split("threshold:")[1].split("\r\n")[0].replace(/^\s+|\s+$/g, '') + "___";
    retstring += results.split("duration (minutes):")[1].split("\r\n")[0].replace(/^\s+|\s+$/g, '') + "___";
    retstring += results.split("window (minutes):")[1].split("\r\n")[0].replace(/^\s+|\s+$/g, '');
    return retstring;
}

function ParseDomainControllers(results)
{
    var retstring = "";
    var parse1 = results.split("Non-Site specific:\r\n")[1].split("The command completed")[0];
    var parse2 = parse1.split("\r\n");
    var tmp = [];
    for(var i = 0; i < parse2.length; i++)
    {
        // sometimes a warning message will appear in this section and we need to skip it
        if(parse2[i].indexOf("WARNING:") != -1)
        {
            continue;
        }
        var dcstring = "";
        tmp = parse2[i].split(" ");
        for(var j = 0; j < tmp.length; j++)
        {
            if(tmp[j])
            {
                dcstring += tmp[j].toLowerCase() + "___";
            }
        }
        var dcarray = dcstring.split("___");
        retstring += dcarray[0] + "*" + dcarray[dcarray.length-2] + "___";
    }
    return retstring;
}

function ResolveHostnames(hostnames)
{
    var retstring = "";
    var computers = hostnames.split("___");
    for (var i = 0; i < computers.length-1; i++)
    {
        if (computers[i] == 'null')
        {
            continue;
        }
        var nsresults = Koadic.shell.exec("nslookup "+computers[i], "~DIRECTORY~\\"+Koadic.uuid()+".txt");
        try
        {
            var ip = nsresults.split("Name:")[1].split("Address:")[1].split("\r\n")[0];
            ip = ip.replace(/\s/g, "");
        }
        catch(e)
        {
            var pingresults = Koadic.shell.exec("ping -4 -n 1 "+computers[i], "~DIRECTORY~\\"+Koadic.uuid()+".txt");
            try
            {
                var ip = pingresults.split("[")[1].split("]")[0];
            }
            catch(e)
            {
                var ip = "";
            }
        }

        retstring += computers[i] + "***" + ip + "___"
    }
    return retstring;
}

function ParseDomainComputers()
{
    var retstring = "";
    var objWMI = GetObject("winmgmts:{impersonationLevel=impersonate}!\\\\.\\root\\directory\\LDAP");
    var objComps = objWMI.Get("ds_computer").Instances_();
    var computercount = objComps.Count;
    for (var i = 0; i < computercount; i++) {
        var comp = objComps.ItemIndex(i);
        if (comp.ds_dnshostname != "null" || comp.ds_dnshostname != "")
        {
            retstring += comp.ds_dnshostname + "___";
        }
    }
    return retstring;
}

function findFQDN()
{
    var fqdn = "";

    try
    {
        fqdn = Koadic.WS.RegRead("HKLM\\SOFTWARE\\Microsoft\\Windows\\CurrentVersion\\Group Policy\\History\\MachineDomain");
        return fqdn;
    }
    catch (e)
    {}

    try
    {
        fqdn = Koadic.shell.exec("echo %userdnsdomain%", "~DIRECTORY~\\"+Koadic.uuid()+".txt");
        if (fqdn.split(" \r\n")[0] != "%userdnsdomain%")
        {
            return fqdn.split(" \r\n")[0];
        }
    }
    catch (e)
    {}

    try
    {
        fqdn = "";
        fqdnwhole = Koadic.shell.exec("whoami /fqdn", "~DIRECTORY~\\"+Koadic.uuid()+".txt");
        if (fqdnwhole.split(":")[0] != "ERROR")
        {
            var fqdnparts = fqdnwhole.split(",");
            for (var i = 0; i < fqdnparts.length; i++)
            {
                if (fqdnparts[i].split("=")[0] == "DC")
                {
                    fqdn += fqdnparts[i].split("=")[1] + ".";
                }
            }
            return fqdn.split("\r\n.")[0];
        }
    }
    catch (e)
    {}

    Koadic.work.report("NoDomain");
    throw true;
}

try
{
    var fqdn = findFQDN();
    var net = new ActiveXObject("WScript.Network");
    var netbios = net.UserDomain;

    var headers = {};
    headers["Header"] = "Key";
    Koadic.work.report(fqdn + "___" + netbios, headers);

    var domain_admins = ParseUsers(Koadic.shell.exec("net group \"Domain Admins\" /domain", "~DIRECTORY~\\"+Koadic.uuid()+".txt"));
    headers["Header"] = "Admins";
    Koadic.work.report(domain_admins, headers);

    var domain_users = ParseUsers(Koadic.shell.exec("net group \"Domain Users\" /domain", "~DIRECTORY~\\"+Koadic.uuid()+".txt"));
    headers["Header"] = "Users";
    Koadic.work.report(domain_users, headers);

    var password_policy = ParsePasswordPolicy(Koadic.shell.exec("net accounts /domain", "~DIRECTORY~\\"+Koadic.uuid()+".txt"));
    headers["Header"] = "PassPolicy";
    Koadic.work.report(password_policy, headers);

    var check_nltest_exist = Koadic.shell.exec("nltest /?", "~DIRECTORY~\\"+Koadic.uuid()+".txt");
    if (check_nltest_exist.indexOf("not recognized") == -1)
    {
        var domain_controllers = ParseDomainControllers(Koadic.shell.exec("nltest /dnsgetdc:"+fqdn, "~DIRECTORY~\\"+Koadic.uuid()+".txt"));
        headers["Header"] = "DomainControllers";
        Koadic.work.report(domain_controllers, headers);
    }

    var domain_computers = ParseDomainComputers();
    headers["Header"] = "DomainComputers";
    Koadic.work.report(domain_computers, headers);

    var resolved_computers = ResolveHostnames(domain_computers);
    headers["Header"] = "ResolvedComputers";
    Koadic.work.report(resolved_computers, headers);

    Koadic.work.report("Complete");

}
catch(e)
{
    Koadic.work.error(e);
}
Koadic.exit();
