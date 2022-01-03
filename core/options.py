
class Option(object):
    def __init__(self, name, value, description, **kwargs):
        self.name = name
        self.description = description
        self.validate = None
        self.required = True
        self.advanced = False
        self.hidden = False
        self.boolean = False
        self.file = False
        self.implant = False
        self.alias = ""
        self.enum = []
        self.value = value
        self.default = value
        self.__dict__.update(kwargs)

    def set(self, value):
        if self.validate is not None:
            if not self.validate(value):
                return False

        elif len(self.enum) > 0:
            if value not in self.enum:
                return False

        self.value = value
        return True

class Options(object):
    def __init__(self):
        self.options = []

    def register(self, name, value, description, **kwargs):
        name = name.upper()
        option = Option(name, value, description, **kwargs)
        self.options.append(option)

    def get(self, name):
        name = name.upper()
        for option in self.options:
            if option.name == name or option.alias == name and name:
                return option.value

        return None

    def set(self, name, value):
        name = name.upper()

        for option in self.options:
            if option.name == name or option.alias == name and name:
                return option.set(value)

        return False

    def copy(self):
        import copy
        return copy.deepcopy(self)
