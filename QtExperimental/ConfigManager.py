from configparser import ConfigParser

import os


class ConfigManager:
    """
    dynamic variable addition, deletion, renaming etc not implemented yet.
    """

    loaded = False

    def __init__(
        self, path, default: dict = None, addMissingVars=True, removeExtraVars=False
    ):
        """
        path is directory to the ini file.(does not need to be an existing file)
        default is a dict with format : 'varName':(val, 'section), varName should have prefix i, f, s for int, float, string.
        use prefix li, lf, ls for list of integer, float or string.

        **preferably the entire config is defined via default dictionary**

        addMissingVars will compare default's vars with the existing config ini file, and add any missing variables
        removeExtraVars will remove any variables that is in the config file, but not the default.
        """

        self.config = ConfigParser()

        self.vals = dict()
        self.secs = dict()
        self.path = path
        self.default = default if default is not None else dict()
        if os.path.isfile(path):
            self.config.read(path)
        else:
            self.newConfig()

        for sec in self.config.sections():
            for opt in self.config.options(sec):
                self.loadVar(sec, opt)

        if self.default.keys() != self.vals.keys():
            for key, vals in self.default.items():
                if addMissingVars:
                    if key not in self.vals.keys():
                        self.loadVar(vals[1], key)
                        if not self.config.has_section(vals[1]):
                            self.config.add_section(vals[1])
                        self.config.set(
                            vals[1],
                            key,
                            self.getVarString(key, vals[0]),
                        )

            for key in self.vals.keys():
                if removeExtraVars and key not in self.default.keys():
                    self.vals.pop(key)
                    s = self.secs.pop(key)
                    self.config.remove_option(s, key)

            for section in self.config.sections():
                if not self.config.options(section):
                    self.config.remove_section(section)
            self.save()

        self.loaded = True

    def getVarString(self,name, val):
        return str(val) if name[0] != "l"else (
                    "|".join([str(item) for item in val]) if len(val) > 0 else ""
                )

    def newConfig(self):
        self.config.clear()
        self.vals.clear()

        for key, val in self.default.items():
            self.vals[key] = val[0]
            self.secs[key] = val[1]

            if not self.config.has_section(val[1]):
                self.config.add_section(val[1])

            # gotta force these 1 liners for some reason
            self.config.set(
                val[1],
                key,
                self.getVarString(key, val[0]),
            )

        self.save()

    def typeCheck(self, name, val):
        def _raise(e):
            raise e

        {
            "i": lambda: _raise(TypeError("must be int"))
            if type(val) is not int
            else "",
            "f": lambda: _raise(TypeError("must be float"))
            if type(val) is not float
            else "",
            "s": lambda: _raise(TypeError("must be string"))
            if type(val) is not str
            else "",
            "l": lambda: _raise(TypeError("must be list"))
            if type(val) is not list
            else "",
        }[name[0]]

    def __getitem__(self, key):
        return self.vals[key]

    def __setitem__(self, key, val):
        if key in self.vals:
            self.typeCheck(key, val)
            self.vals[key] = val
            self.config.set(self.secs[key], key, self.getVarString(key, val))

        else:
            raise KeyError()

    def __setattr__(self, name: str, value) -> None:

        if self.loaded:
            if name in self.vals.keys():
                self.typeCheck(name, value)
                self.vals[name] = value
                self.config.set(self.secs[name], name, self.getVarString(name, value))

                self.save()
            else:

                super().__setattr__(name, value)
        else:
            super.__setattr__(self, name, value)

    def __getattribute__(self, name: str):
        try:
            return super().__getattribute__(name)
        except AttributeError:
            if name in self.vals.keys():

                return self.vals[name]
            else:
                raise AttributeError()

    def save(self):
        if not os.path.isdir(os.path.dirname(self.path)):
            os.mkdir(os.path.dirname(self.path))
        with open(self.path, "w") as file:
            self.config.write(file)

    def loadVar(self, sec, opt):
        def intVar():
            try:
                self.vals[opt] = self.config.getint(sec, opt)
            except:
                self.vals[opt] = self.default.get(opt, (0,))[0]

        def floatVar():
            try:
                self.vals[opt] = self.config.getfloat(sec, opt)
            except:
                self.vals[opt] = self.default.get(opt, (0,))[0]

        def listVar():
            try:
                temp = self.config.get(sec, opt).split("|")
                varType = {"i": int, "f": float, "s": str}[opt[1]]
                self.vals[opt] = [varType(item) for item in temp]
            except:
                self.vals[opt] = self.default.get(opt, ([],))[0]

        def strVar():
            try:
                self.vals[opt] = self.config.get(sec, opt)
            except:
                self.vals[opt] = self.default.get(opt, ("",))[0]

        t = opt[0]

        {"i": intVar, "f": floatVar, "s": strVar, "l": listVar}[t]()
        self.secs[opt] = sec


if __name__ == "__main__":
    c = ConfigManager(
        "D:\Python Project\screenCap\QtExperimental\config.ini",
        {
            "inum": (33, "main"),
            "fnum": (2.2, "main"),
            "sstring": ("sadasd", "temp"),
            "lilist": ([2, 3, 4], "list"),
        },
    )
    c.inum = 44
    print(c.inum)
    
