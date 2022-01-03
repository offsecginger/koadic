import core.loader
import copy

class Linter(object):
    def __init__(self):
        pass

    def prepend_stdlib(self, script):
        with open("data/stdlib.vbs", "rb") as f:
            stdlib = f.read().lower()

        return stdlib + script

    def minimize_glyph(self, script, glyph):
        orig_script = script
        script = script.replace(glyph + b" ", glyph)
        script = script.replace(b" " + glyph, glyph)
        if orig_script != script:
            return self.minimize_glyph(script,glyph)
        return script

    def minimize_script(self, script):
        if type(script) != bytes:
            script = script.encode()

        lines = []
        script = script.replace(b"\r", b"")
        script = self.minimize_glyph(script, b",")
        script = self.minimize_glyph(script, b"=")
        script = self.minimize_glyph(script, b"(")
        script = self.minimize_glyph(script, b")")
        script = self.minimize_glyph(script, b":")
        script = self.minimize_glyph(script, b"&")
        script = self.minimize_glyph(script, b"<")
        script = self.minimize_glyph(script, b">")

        for line in script.split(b"\n"):
            line = line.split(b"'")[0]
            line = line.strip()
            if line:
                lines.append(line)

        return b":".join(lines).lower()

    # this removes functions that the current script doesn't use
    def trim_stdlib(self, stdlib, script):
        stdlib = stdlib.decode()
        script = script.decode()

        sleepflag = False
        exitflag = False
        if "Koadic.sleep" not in script:
            stdlib = stdlib.split("//sleep.start")[0] + stdlib.split("//sleep.end")[1]
            sleepflag = True
        if "Koadic.exit" not in script:
            stdlib = stdlib.split("//exit.start")[0] + stdlib.split("//exit.end")[1]
            exitflag = True
        if "Koadic.isHTA" not in script and sleepflag and exitflag:
            stdlib = stdlib.split("//isHTA.start")[0] + stdlib.split("//isHTA.end")[1]
        if "Koadic.isWScript" not in script:
            stdlib = stdlib.split("//isWScript.start")[0] + stdlib.split("//isWScript.end")[1]
        userinfoflag = False
        if "Koadic.user.info" not in script:
            stdlib = stdlib.split("//user.info.start")[0] + stdlib.split("//user.info.end")[1]
            userinfoflag = True
        useriselevatedflag = False
        if "Koadic.user.isElevated" not in script and userinfoflag:
            stdlib = stdlib.split("//user.isElevated.start")[0] + stdlib.split("//user.isElevated.end")[1]
            useriselevatedflag = True
        if "Koadic.user.OS" not in script and userinfoflag:
            stdlib = stdlib.split("//user.OS.start")[0] + stdlib.split("//user.OS.end")[1]
        if "Koadic.user.DC" not in script and userinfoflag:
            stdlib = stdlib.split("//user.DC.start")[0] + stdlib.split("//user.DC.end")[1]
        if "Koadic.user.Arch" not in script and userinfoflag:
            stdlib = stdlib.split("//user.Arch.start")[0] + stdlib.split("//user.Arch.end")[1]
        usercwdflag = False
        if "Koadic.user.CWD" not in script and userinfoflag:
            stdlib = stdlib.split("//user.CWD.start")[0] + stdlib.split("//user.CWD.end")[1]
            usercwdflag = True
        useripaddrsflag = False
        if "Koadic.user.IPAddrs" not in script and userinfoflag:
            stdlib = stdlib.split("//user.IPAddrs.start")[0] + stdlib.split("//user.IPAddrs.end")[1]
            useripaddrsflag = True
        workerrorflag = False
        if "Koadic.work.error" not in script:
            stdlib = stdlib.split("//work.error.start")[0] + stdlib.split("//work.error.end")[1]
            workerrorflag = True
        workgetflag = False
        if "Koadic.work.get" not in script:
            stdlib = stdlib.split("//work.get.start")[0] + stdlib.split("//work.get.end")[1]
            workgetflag = True
        workforkflag = False
        if "Koadic.work.fork" not in script:
            stdlib = stdlib.split("//work.fork.start")[0] + stdlib.split("//work.fork.end")[1]
            workforkflag = True
        httpuploadflag = False
        if "Koadic.http.upload" not in script:
            stdlib = stdlib.split("//http.upload.start")[0] + stdlib.split("//http.upload.end")[1]
            httpuploadflag = True
        workreportflag = False
        if "Koadic.work.report" not in script and workerrorflag and httpuploadflag:
            stdlib = stdlib.split("//work.report.start")[0] + stdlib.split("//work.report.end")[1]
            workreportflag = False
        httpdownloadflag = False
        if "Koadic.http.download" not in script:
            stdlib = stdlib.split("//http.download.start")[0] + stdlib.split("//http.download.end")[1]
            httpdownloadflag = True
        if "Koadic.work.make_url" not in script and workgetflag and workforkflag and workreportflag and httpdownloadflag:
            stdlib = stdlib.split("//work.make_url.start")[0] + stdlib.split("//work.make_url.end")[1]
        httpdownloadexflag = False
        if "Koadic.http.downloadEx" not in script and httpdownloadflag:
            stdlib = stdlib.split("//http.downloadEx.start")[0] + stdlib.split("//http.downloadEx.end")[1]
            httpdownloadexflag = True
        httpgetflag = False
        if "Koadic.http.get" not in script and httpdownloadexflag:
            stdlib = stdlib.split("//http.get.start")[0] + stdlib.split("//http.get.end")[1]
            httpgetflag = True
        httppostflag = False
        if "Koadic.http.post" not in script and workgetflag and workreportflag and httpdownloadexflag:
            stdlib = stdlib.split("//http.post.start")[0] + stdlib.split("//http.post.end")[1]
            httppostflag = True
        if "Koadic.http.create" not in script and httpgetflag and httppostflag:
            stdlib = stdlib.split("//http.create.start")[0] + stdlib.split("//http.create.end")[1]
        httpaddheadersflag = False
        if "Koadic.http.addHeaders" not in script and httpgetflag and httppostflag:
            stdlib = stdlib.split("//http.addHeaders.start")[0] + stdlib.split("//http.addHeaders.end")[1]
            httpaddheadersflag = True
        if "Koadic.http.bin2str" not in script and httpdownloadexflag:
            stdlib = stdlib.split("//http.bin2str.start")[0] + stdlib.split("//http.bin2str.end")[1]
        processcurrentpidflag = False
        if "Koadic.process.currentPID" not in script:
            stdlib = stdlib.split("//process.currentPID.start")[0] + stdlib.split("//process.currentPID.end")[1]
            processcurrentpidflag = True
        processkillflag = False
        if "Koadic.process.kill" not in script:
            stdlib = stdlib.split("//process.kill.start")[0] + stdlib.split("//process.kill.end")[1]
            processkillflag = True
        processgetpidflag = False
        if "Koadic.process.getPID" not in script:
            stdlib = stdlib.split("//process.getPID.start")[0] + stdlib.split("//process.getPID.end")[1]
            processgetpidflag = True
        if "Koadic.process.list" not in script and processcurrentpidflag and processkillflag and processgetpidflag:
            stdlib = stdlib.split("//process.list.start")[0] + stdlib.split("//process.list.end")[1]
        registrywriteflag = False
        if "Koadic.registry.write" not in script:
            stdlib = stdlib.split("//registry.write.start")[0] + stdlib.split("//registry.write.end")[1]
            registrywriteflag = True
        registryreadflag = False
        if "Koadic.registry.read" not in script:
            stdlib = stdlib.split("//registry.read.start")[0] + stdlib.split("//registry.read.end")[1]
            registryreadflag = True
        registrydestroyflag = False
        if "Koadic.registry.destroy" not in script:
            stdlib = stdlib.split("//registry.destroy.start")[0] + stdlib.split("//registry.destroy.end")[1]
            registrydestroyflag = True
        if "Koadic.registry.provider" not in script and registrywriteflag and registryreadflag and registrydestroyflag:
            stdlib = stdlib.split("//registry.provider.start")[0] + stdlib.split("//registry.provider.end")[1]
        if "Koadic.WMI.createProcess" not in script and workforkflag and processcurrentpidflag:
            stdlib = stdlib.split("//WMI.createProcess.start")[0] + stdlib.split("//WMI.createProcess.end")[1]
        shellexecflag = False
        if "Koadic.shell.exec" not in script and userinfoflag and useriselevatedflag and usercwdflag and useripaddrsflag:
            stdlib = stdlib.split("//shell.exec.start")[0] + stdlib.split("//shell.exec.end")[1]
            shellexecflag = True
        if "Koadic.user.shellchcp" not in script and userinfoflag and shellexecflag and httpaddheadersflag:
            stdlib = stdlib.split("//user.shellchcp.start")[0] + stdlib.split("//user.shellchcp.end")[1]
        fileget32bitfolderflag = False
        if "Koadic.file.get32BitFolder" not in script and workforkflag:
            stdlib = stdlib.split("//file.get32BitFolder.start")[0] + stdlib.split("//file.get32BitFolder.end")[1]
            fileget32bitfolderflag = True
        filereadbinaryflag = False
        if "Koadic.file.readBinary" not in script and httpuploadflag and shellexecflag:
            stdlib = stdlib.split("//file.readBinary.start")[0] + stdlib.split("//file.readBinary.end")[1]
            filereadbinaryflag = True
        filereadtextflag = False
        if "Koadic.file.readText" not in script and shellexecflag and filereadbinaryflag:
            stdlib = stdlib.split("//file.readText.start")[0] + stdlib.split("//file.readText.end")[1]
            filereadtextflag = True
        if "Koadic.shell.run" not in script and filereadbinaryflag and filereadtextflag:
            stdlib = stdlib.split("//shell.run.start")[0] + stdlib.split("//shell.run.end")[1]
        if "Koadic.user.encoder" not in script and userinfoflag and httpuploadflag and httpaddheadersflag and shellexecflag and filereadbinaryflag:
            stdlib = stdlib.split("//user.encoder.start")[0] + stdlib.split("//user.encoder.end")[1]
        if "Koadic.uuid" not in script and userinfoflag and useriselevatedflag and useripaddrsflag and filereadbinaryflag:
            stdlib = stdlib.split("//uuid.start")[0] + stdlib.split("//uuid.end")[1]
        filewriteflag = False
        if "Koadic.file.write" not in script and httpdownloadexflag:
            stdlib = stdlib.split("//file.write.start")[0] + stdlib.split("//file.write.end")[1]
            filewriteflag = True
        filedeletefileflag = False
        if "Koadic.file.deleteFile" not in script and shellexecflag and filereadbinaryflag:
            stdlib = stdlib.split("//file.deleteFile.start")[0] + stdlib.split("//file.deleteFile.end")[1]
            filedeletefileflag = True
        if "Koadic.file.getPath" not in script and processcurrentpidflag and shellexecflag and fileget32bitfolderflag and filereadbinaryflag and filereadtextflag and filewriteflag and filedeletefileflag:
            stdlib = stdlib.split("//file.getPath.start")[0] + stdlib.split("//file.getPath.end")[1]

        stdlib += "\n"

        return stdlib.encode()

    def scramble(self, data):
        import string
        import random
        symbols = set()
        data2 = data.replace(b"\n", b" ")
        for symbol in data2.split(b" "):
            if symbol.startswith(b'Koadic') and b'(' not in symbol and b')' not in symbol and b';' not in symbol:
                symbols.add(symbol)
            if symbol.startswith(b'#') and symbol.endswith(b'#'):
                symbols.add(symbol)
            if symbol.startswith(b'#') and b'#(' in symbol:
                symbols.add(symbol.split(b'(')[0])

        symbols = list(symbols)
        symbols = sorted(symbols, key=lambda x: x.count(b'.'))

        obnames = []

        finalize = []
        mapping = {}

        for symindex, symbol in enumerate(symbols):
            while True:
                obname = ''.join(random.choice(string.ascii_uppercase) for _ in range(10)).encode()
                if obname not in obnames:
                    obnames.append(obname)
                    break


            fixed = []
            basename = b""
            foundyet = False
            for part in symbol.split(b"."):
                if not foundyet:
                    if part in mapping:
                        fixed.append(mapping[part])
                    else:
                        foundyet = True
                        mapping[part] = obname
                        fixed.append(obname)
                        break
                else:
                    fixed.append(part)

            new_name = b".".join(fixed)

            tup = (symbol, new_name)
            finalize.append(tup)

        finalize = sorted(finalize, key=lambda x: (x[0].count(b"."), len(x[0])), reverse=True)
        for final in finalize:
            data = data.replace(final[0], final[1])

        return data

    def post_process_script(self, script, template, options, session, stdlib=True):
        if stdlib:
            stdlib_content = options.get("_STDLIB_")
            trimmed_stdlib = self.trim_stdlib(stdlib_content, script)
            script = trimmed_stdlib + script

            # crappy hack for forkcmd
            forkopt = copy.deepcopy(options)
            forkopt.set("URL", "***K***")
            forkopt.set("_JOBPATH_", "")
            forkopt.set("_SESSIONPATH_", "")
            forkcmd = options.get("_FORKCMD_")
            forkcmd = core.loader.apply_options(forkcmd, forkopt)

            options.set("_FORKCMD_", forkcmd.decode())

        script = core.loader.apply_options(script, options)

        # obfuscate the script!
        import string
        script = self.scramble(script)

        # minify the script
        from rjsmin import jsmin
        script = jsmin(script.decode()).encode()

        # obfuscation options
        if options.get("OBFUSCATE"):
            if options.get("OBFUSCATE") == "xor":
                xor_key = core.loader.create_xor_key()
                xor_script = core.loader.xor_data(script, xor_key)
                script = core.loader.xor_js_file(xor_script.decode(), xor_key).encode()
            script = jsmin(script.decode()).encode()

        script = template.replace(b"~SCRIPT~", script)
        if session and session.encoder:
            encoder = session.encoder
        else:
            encoder = "1252"
        script = script.decode().encode("cp"+encoder)
        return script

    """
    def _remove_usage(self, line, stdlib, script, keyword):
        line = line.strip()
        start = keyword +  " "
        end = "end " + keyword
        if line.startswith(keyword + " "):
            name = line.split(start)[1].split("(")[0]

            if name not in script.lower():
                part1 = stdlib.split(line)[0]
                part2 = part1.split[1].split(end)

                stdlib = part1 + part2

        return stdlib
    """
