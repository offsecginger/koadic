class Colors(object):
    def __init__(self):
        # http://ozzmaker.com/add-colour-to-text-in-python/
        self.ENDC = '\033[0m'

        self.RED = '31'
        self.GREEN = '32'
        self.YELLOW = '33'
        self.BLUE = '34'
        self.CYAN = '36'

        self.NORMAL = '0'
        self.BOLD = '1'
        self.UNDERLINE = '2'

    def error(self, text):
        return self.colorize(text, [self.RED, self.BOLD])

    def warning(self, text):
        return self.colorize(text, [self.YELLOW, self.BOLD])

    def good(self, text):
        return self.colorize(text, [self.GREEN, self.BOLD])

    def status(self, text):
        return self.colorize(text, [self.BLUE, self.BOLD])

    def colorize(self, text, options, readline=False):
        start = ""
        if readline:
            start += "\001"
        start += '\033['
        start += ";".join(options)
        start += "m"
        if readline:
            start += "\002"
            end = "\001" + self.ENDC + "\002"
        else:
            end = self.ENDC

        return start + text + end

    def get_prompt(self, state, isreadline = True):
        import os
        glyph = "#" if os.geteuid() == 0 else "$"
        last = state.split("/")[-1]
        state = [s[0:3] for s in state.split("/")[:-1]]
        state.append(last)
        state = "/".join(state)
        return "%s%s: %s%s" % (self.colorize("(", [self.GREEN], isreadline),
                                 self.colorize("koadic", [self.BOLD], isreadline),
                                 self.colorize(state, [self.CYAN], isreadline),
                                 self.colorize(")" + glyph + " ", [self.GREEN], isreadline))
