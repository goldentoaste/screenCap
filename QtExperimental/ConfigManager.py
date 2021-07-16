from configparser import ConfigParser

import os


class ConfigManager:
    """
    dynamic variable addition, deletion, renaming etc not implemented yet.
    """

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
        self.default = default if default is not None else dict()
        self.config = ConfigParser()
        self.path = path

        self.vals = dict()
        self.secs = dict()

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

            for key in self.vals.keys():
                if removeExtraVars and key not in self.default.keys():
                    self.vals.pop(key)
                    self.secs.pop(key)

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
                str(val[0])
                if key[0] != "l"
                else (
                    "|".join([str(item) for item in val[0]]) if len(val[0]) > 0 else ""
                ),
            )

        self.save()

    def __setattr__(self, name: str, value) -> None:
        try:
            super().__setattr__(name, value)
        except AttributeError:
            if name in self.vals.keys():
                self.vals[name] = (value, self.vals[name][1])
                self.save()
            else:
                raise AttributeError()

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
