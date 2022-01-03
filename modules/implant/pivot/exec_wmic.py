# wmic /node:~IP~ /user:~SMBDOMAIN~\~SMBUSER~ /password:~SMBPASS~ process call create "cmd /c ~CMD~"
import core.implant

class ExecCmdImplant(core.implant.Implant):
    pass
