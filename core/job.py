from core.mappings import mappings
import string
import threading
import uuid
import core.loader
from core.linter import Linter


class Job(object):
    CREATED = 0
    RECEIVED = 2
    RUNNING = 3
    COMPLETE = 4
    FAILED = 5

    JOB_ID = 0
    JOB_ID_LOCK = threading.Lock()

    def __init__(self, shell, session_id, name, workload, options):
        self.fork32Bit = False
        self.completed = Job.CREATED
        self.hidden = False
        self.shell = shell
        self.options = options
        self.session_id = session_id
        self.name = name
        self.errno = ""
        self.data = b""
        self.unsafe_data = b""
        self.key = uuid.uuid4().hex
        self.results = ""
        self.ip = ""
        self.computer = ""
        self.escape_flag = False
        self.linter = Linter()

        if self.session_id != -1:
            self.session = [session for skey, session in self.shell.sessions.items() if session.id == self.session_id][0]
            self.ip = self.session.ip
            self.computer = self.session.computer

        with Job.JOB_ID_LOCK:
            self.id = Job.JOB_ID
            Job.JOB_ID += 1

        if self.create() != False:
            self.create = True
            self.shell.print_status("Zombie %d: Job %d (%s) created." % (
                self.session_id, self.id, self.name))
        else:
            self.create = False

        self.script = core.loader.load_script(workload, self.options)

    def create(self):
        pass

    def receive(self):
        #self.shell.print_status("Zombie %d: Job %d (%s) received." % (self.session.id, self.id, self.name))
        self.completed = Job.RECEIVED

    def payload(self):
        #self.shell.print_status("Zombie %d: Job %d (%s) running." % (self.session.id, self.id, self.name))
        self.completed = Job.RUNNING
        return self.script

    def load_payload(self, id):
        try:
            for port in self.shell.stagers:
                for endpoint in self.shell.stagers[port]:
                    stager = self.shell.stagers[port][endpoint]
                    if int(stager.get_payload_id()) == int(id):
                        return stager.get_payload_data().decode()
        except:
            pass

        return None

    def convert_shellcode(self, shellcode):
        decis = []
        count = 0
        for i in range(0, len(shellcode), 2):
            count += 1
            hexa = shellcode[i:i+2]
            deci = int(hexa, 16)

            if count % 25 == 0:
                decis.append(" _\\n" + str(deci))
            else:
                decis.append(str(deci))

        return ",".join(decis)

    def parse_ips(self, ips):
        import core.cidr
        return core.cidr.get_ips(ips)

    def parse_ports(self, ports):
        import core.cidr
        return core.cidr.get_ports(ports)

    def make_vb_array(self, name, array):
        ret = "dim %s(%d)\n" % (name, len(array) - 1)

        count = 0
        for el in array:
            x = '%s(%d) = "%s"\n' % (name, count, str(el))
            ret += x
            count += 1

        return ret

    def make_js_array(self, name, array):
        array = ['"%s"' % item for item in array]
        ret = "var %s = [%s];" % (name, ", ".join(array))
        return ret

    def error(self, errno, errdesc, errname, data):
        self.errno = str(errno)
        self.errdesc = errdesc
        self.errname = errname
        self.completed = Job.FAILED
        self.sanitize_data(data)

        self.print_error()

    def print_error(self):
        self.shell.play_sound('FAIL')
        self.shell.print_error("Zombie %d: Job %d (%s) failed!" % (
            self.session_id, self.id, self.name))
        self.shell.print_error("%s (%08x): %s " % (
            self.errname, int(self.errno) + 2**32, self.errdesc))

    def sanitize_data(self, data):
        # clean up unprintable characters from data
        self.data = b""
        for i in range(0, len(data)):
            try:
                if data[i:i + 1].decode() in string.printable:
                    self.data += data[i:i + 1]
            except:
                pass
        self.data = self.data.decode()

        #self.data = "".join(i for i in data.decode() if i in string.printable)

    def report(self, handler, data, sanitize=True):
        #self.errno = str(errno)
        self.completed = Job.COMPLETE

        self.unsafe_data = data

        if (sanitize):
            self.sanitize_data(data)
        else:
            self.data = ""

        if handler:
            handler.reply(202)

        self.shell.play_sound('SUCCESS')
        self.shell.print_good("Zombie %d: Job %d (%s) completed." % (
            self.session_id, self.id, self.name))

        self.done()

    def status_string(self):
        if self.completed == Job.COMPLETE:
            return "Complete"
        if self.completed == Job.CREATED:
            return "Created"
        if self.completed == Job.RECEIVED:
            return "Received"
        if self.completed == Job.RUNNING:
            return "Running"
        if self.completed == Job.FAILED:
            return "Failed"

    def done(self):
        pass

    def display(self):
        pass

    def print_status(self, message):
        self.shell.print_status("Zombie %d: Job %d (%s) %s" % (
            self.session_id, self.id, self.name, message))

    def print_good(self, message):
        self.shell.print_good("Zombie %d: Job %d (%s) %s" % (
            self.session_id, self.id, self.name, message))

    def print_warning(self, message):
        self.shell.print_warning("Zombie %d: Job %d (%s) %s" % (
            self.session_id, self.id, self.name, message))


    def decode_downloaded_data(self, data, encoder, text=False):
        if encoder == "936":
            try:
                alldata = data.decode().splitlines()
                if "-----BEGIN CERTIFICATE-----" in alldata[0] and "-----END CERTIFICATE-----" in alldata[-1]:
                    from base64 import b64decode
                    return b64decode("".join(alldata[1:-1]))
            except Exception:
                pass

        slash_char = chr(92).encode()
        zero_char = chr(0x30).encode()
        null_char = chr(0).encode()
        mapping = mappings

        b_list = []
        special_char = {
            '0': null_char,
            '\\': slash_char
        }

        append = b_list.append
        for i in data.decode('utf-8'):
            # Decide on slash char
            if self.escape_flag:
                self.escape_flag = False
                append(special_char[i])
                continue

            if i == '\\' and not text:
                # EAT the slash
                self.escape_flag = True
            else:
                # collisions will go here
                if i == '€' and encoder == "1251":
                    append(b'\x88')
                    continue

                try:
                    append(mapping[ord(i)])
                except:
                    print(f"ENCODING ERROR: {str(ord(i))} <- Please add a mapping to core/mappings.py with \"chr({str(ord(i))}).encode('cp{encoder}')\"")

        return b"".join(b_list)
