import sys
import importlib
import core.plugin
import copy

DESCRIPTION = "reloads all modules"

def autocomplete(shell, line, text, state):
    return None

def help(shell):
    pass

def execute(shell, cmd):
    count = 0
    for key in shell.plugins:
        _key = key

        try:
            key = key.split("/")[-1]
            module = sys.modules[key]
            source = open("modules/"+_key+".py").read()
            exec(source,module.__dict__)

            for thing in dir(module):
                try:
                    thing = getattr(module, thing)

                    if issubclass(thing, core.plugin.Plugin):
                        new_thing = thing(shell)
                        new_thing.options = copy.deepcopy(shell.plugins[_key].options)
                        shell.plugins[_key] = new_thing
                        count += 1
                except TypeError as e:
                    pass
        except:
            shell.print_error("Failed to load %s" % _key)
            pass

    shell.play_sound('LOAD')
    shell.print_good("Successfully loaded %d modules." % count)
