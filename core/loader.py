import os
import sys
import inspect
import core.plugin
import random
import string

def load_plugins(dir, instantiate = False, shell = None):
    plugins = {}

    for root, dirs, files in os.walk(dir):
        sys.path.append(root)

        # make forward slashes on windows
        module_root = root.replace(dir, "").replace("\\", "/")

        #if (module_root.startswith("/")):
            #module_root = module_root[1:]

        #print root
        for file in files:
            if not file.endswith(".py"):
                continue

            if file in ["__init__.py"]:
                continue

            file = file.rsplit(".py", 1)[0]
            pname = module_root + "/" + file
            if (pname.startswith("/")):
                pname = pname[1:]

            if instantiate:
                if pname in sys.modules:
                    del sys.modules[pname]
                env = __import__(file, )
                for name, obj in inspect.getmembers(env):
                    if inspect.isclass(obj) and issubclass(obj, core.plugin.Plugin):
                        plugins[pname] = obj(shell)
                        break
            else:
                plugins[pname] = __import__(file)

        sys.path.remove(root)

    return plugins

def load_script(path, options = None, minimize = True):
    with open(path, "rb") as f:
        script = f.read().strip()

    #script = self.linter.prepend_stdlib(script)

    #if minimize:
        #script = self.linter.minimize_script(script)

    script = apply_options(script, options)

    return script

def apply_options(script, options = None):
    if options is not None:
        for option in options.options:
            name = "~%s~" % option.name
            val = str(option.value).encode()

            script = script.replace(name.encode(), val)
            script = script.replace(name.lower().encode(), val)

    return script

def create_xor_key():
    return "".join(random.choice(string.ascii_uppercase + string.ascii_lowercase + string.digits) for _ in range(random.randint(10,20)))

def xor_data(data, key):
    import binascii
    while len(key) < len(data):
        key += key

    return binascii.hexlify("".join([chr(ord(c1) ^ ord(c2)) for (c1,c2) in zip(data.decode(),key)]).encode())

def xor_js_file(script, key):
    function_name = "".join(random.choice(string.ascii_uppercase + string.ascii_lowercase) for _ in range(random.randint(10,20)))
    var_encoded = "".join(random.choice(string.ascii_uppercase + string.ascii_lowercase) for _ in range(random.randint(10,20)))
    var_decoded = "".join(random.choice(string.ascii_uppercase + string.ascii_lowercase) for _ in range(random.randint(10,20)))
    var_key = "".join(random.choice(string.ascii_uppercase + string.ascii_lowercase) for _ in range(random.randint(10,20)))
    var_s = "".join(random.choice(string.ascii_uppercase + string.ascii_lowercase) for _ in range(random.randint(10,20)))
    var_e_len = "".join(random.choice(string.ascii_uppercase + string.ascii_lowercase) for _ in range(101))
    var_e_var = "".join(random.choice(string.ascii_uppercase + string.ascii_lowercase) for _ in range(random.randint(10,20)))
    var_v_len = "".join(random.choice(string.ascii_uppercase + string.ascii_lowercase) for _ in range(118))
    var_v_var = "".join(random.choice(string.ascii_uppercase + string.ascii_lowercase) for _ in range(random.randint(10,20)))
    var_a_len = "".join(random.choice(string.ascii_uppercase + string.ascii_lowercase) for _ in range(97))
    var_a_var = "".join(random.choice(string.ascii_uppercase + string.ascii_lowercase) for _ in range(random.randint(10,20)))
    var_l_len = "".join(random.choice(string.ascii_uppercase + string.ascii_lowercase) for _ in range(108))
    var_l_var = "".join(random.choice(string.ascii_uppercase + string.ascii_lowercase) for _ in range(random.randint(10,20)))
    var_eval_arr = "".join(random.choice(string.ascii_uppercase + string.ascii_lowercase) for _ in range(random.randint(10,20)))
    var_eval = "".join(random.choice(string.ascii_uppercase + string.ascii_lowercase) for _ in range(random.randint(10,20)))
    js = """function """+function_name+"""("""+var_encoded+""", """+var_key+""") {
var """+var_decoded+""" = '';
while ("""+var_key+""".length < """+var_encoded+""".length) {
"""+var_key+""" += """+var_key+""";
}
for (i = 0+0-0; i < """+var_encoded+""".length; i+=(2+0-0)) {
var """+var_s+""" = String.fromCharCode(parseInt("""+var_encoded+""".substr(i, 2+0-0), 16+0-0) ^ """+var_key+""".charCodeAt(i/(2+0-0)));
"""+var_decoded+""" = """+var_decoded+""" + """+var_s+""";
}
return """+var_decoded+""";
}

var """+var_e_var+""" = \""""+var_e_len+"""\";
var """+var_v_var+""" = \""""+var_v_len+"""\";
var """+var_a_var+""" = \""""+var_a_len+"""\";
var """+var_l_var+""" = \""""+var_l_len+"""\";
var """+var_eval_arr+""" = [String.fromCharCode("""+var_e_var+""".length), String.fromCharCode("""+var_v_var+""".length), String.fromCharCode("""+var_a_var+""".length), String.fromCharCode("""+var_l_var+""".length)];
var """+var_eval+""" = this["""+var_eval_arr+"""[0+0-0]+"""+var_eval_arr+"""[1+0-0]+"""+var_eval_arr+"""[2+0-0]+"""+var_eval_arr+"""[3+0-0]];
"""+var_eval+"""("""+function_name+"""('"""+script+"""', '"""+key+"""'));"""
    return js
