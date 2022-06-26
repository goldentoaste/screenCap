from configparser import ConfigParser, NoSectionError, NoOptionError

import os
from typing import Any, Dict, List, Union


class ConfigManager:
    """
    dynamic variable addition, deletion, renaming etc not implemented yet.
    And is not needed for the current project.
    """

    loaded = False

    def __init__(
        self,
        path: str,
        default: dict = None,
        addMissingVars=True,
        removeExtraVars=False,
    ):
        """
        path is directory to the ini file.(does not need to be an existing file)
        default is a dict with format : 'varName':(val, 'section), varName should have prefix i, f, s, b for int, float, string, boolean.
        use prefix li, lf, ls for list of integer, float or string.
        **preferably the entire config is defined via default dictionary**
        addMissingVars will compare default's vars with the existing config ini file, and add any missing variables
        removeExtraVars will remove any variables that is in the config file, but not the default.
        """

        self.config = ConfigParser()
        self.config.optionxform = str
        self.vals = {}
        self.secs = {}
        self.path = path
        self.default = default if default else dict()

        self.addMissingVars = addMissingVars
        self.removeExtraVars = removeExtraVars
        
        if os.path.isfile(path):
            self.config.read(path)
        else:
            self.newConfig()
        self.update()

    def update(self, save=True):
        self.loaded = False

        # loading variable existing in local files
        for sec in self.config.sections():
            for opt in self.config.options(sec):
                self.loadVar(sec, opt)

        if self.default.keys() != self.vals.keys():
            # add variables thaty exist in defaults, but not in file
            if self.addMissingVars:
                for key, vals in self.default.items():
                    if key not in self.vals.keys():
                        self.loadVar(vals[1], key)
                        if not self.config.has_section(vals[1]):
                            self.config.add_section(vals[1])
                        self.config.set(
                            vals[1],
                            key,
                            self.getVarString(key, vals[0]),
                        )
            # remove variables existing in local file, but not in defaults
            if self.removeExtraVars:
                for key in self.vals.keys():
                    if key not in self.default.keys():
                        self.vals.pop(key)
                        s = self.secs.pop(key)
                        self.config.remove_option(s, key)

            # remove empty sections
            for section in self.config.sections():
                if not self.config.options(section):
                    self.config.remove_section(section)

        if save:
            self.save()
        self.loaded = True

    def addDefaultVars(self, newDefaults: dict):
        """
        adds the given default dict to this config
        """
        self.default.update(newDefaults)
        self.update(save=False)

    def setMultipleVars(self, updates: Dict[str, Any]):
        """
        used to update multiple variables

        input is {varName : val, ... }, each varName must exist
        """
        try:
            for key, val in updates.items():
                self.typeCheck(key, val)
                self.vals[key] = val
                self.config.set(self.secs[key], key, self.getVarString(key, val))
            self.save()
        except KeyError as e:
            raise KeyError(
                f"Trying set a config value that doesnt exist! in setMultipleVars\n {updates}"
            ) from e

    def getVarString(self, name, val):
        return (
            str(val)
            if name[0] != "l"
            else ("|".join([str(item) for item in val]) if len(val) > 0 else "")
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

    def typeCheck(self, name: str, val):
        def _raise(e):
            raise e

        try:
            return {
                "i": lambda: _raise(TypeError("must be int"))
                if type(val) is not int
                else (),
                "f": lambda: _raise(TypeError("must be float"))
                if type(val) is not float
                else (),
                "s": lambda: _raise(TypeError("must be string"))
                if type(val) is not str
                else (),
                "b": lambda: _raise(TypeError("must be string"))
                if type(val) is not bool
                else (),
                "l": lambda: _raise(TypeError("must be list"))
                if type(val) is not list
                else (),
            }[name[0]]()
        except KeyError as e:
            raise KeyError(
                f"Configer Manager TypeCheck: variable '{name}' is not typed."
            ) from e

    def getSection(self, val):
        return self.secs[val]

    def __contains__(self, item: str):
        return item in self.vals

    def __getitem__(self, key) -> Union[str, int, float, List[Union[str, int, float]]]:
        """
        returns a config value based on config key, via the list index operator.
        """
        return self.vals[key]

    def __setitem__(self, key, val):
        try:
            if self.vals[key] == val:
                return
            self.typeCheck(key, val)
            self.vals[key] = val
            self.config.set(self.secs[key], key, self.getVarString(key, val))
            self.save()
        except KeyError as e:
            raise KeyError(f"Trying to set a config value that doesnt exist! {key} ") from e

    def __setattr__(self, name: str, value) -> None:
        if self.loaded:
            try:
                if self.vals[name] == value:
                    return
                self.typeCheck(name, value)
                self.vals[name] = value
                self.config.set(self.secs[name], name, self.getVarString(name, value))

                self.save()
            except KeyError as e:
                raise AttributeError(
                    f"Trying to set a config value that doesnt exist! {name}"
                ) from e
                # super().__setattr__(name, value)
        else:
            super().__setattr__(name, value)

    def __getattribute__(self, name: str):
        try:
            return super().__getattribute__(name)
        except AttributeError:
            try:
                return self.vals[name]
            except KeyError as e:
                raise AttributeError(f"The config attribute is not found: {name}") from e

    def save(self):
        if not os.path.isdir(os.path.dirname(self.path)):
            os.mkdir(os.path.dirname(self.path))
        with open(self.path, "w", encoding='utf-8') as file:
            self.config.write(file)

    def loadVar(self, sec: str, opt: str):
        """Load a single variable from config file into
        Args:
            sec (str): Section of the config file
            opt (str): Option of the given section
        """

        def boolVar():
            try:
                s = self.config.get(sec, opt)
                self.vals[opt] = bool(s.lower() == "true")
            except (NoSectionError, NoOptionError):
                self.vals[opt] = self.default.get(opt, (False,))[0]

        def intVar():
            try:
                self.vals[opt] = self.config.getint(sec, opt)
            except (NoSectionError, NoOptionError):
                self.vals[opt] = self.default.get(opt, (0,))[0]

        def floatVar():
            try:
                self.vals[opt] = self.config.getfloat(sec, opt)
            except (NoSectionError, NoOptionError):
                self.vals[opt] = self.default.get(opt, (0,))[0]

        def listVar():
            try:
                temp = self.config.get(sec, opt).split("|")
                length = len(temp)
                print(f"length check {sec, opt, length , len(self.default[opt][0])}")
                if length < len(self.default[opt][0]):
                    temp.extend(
                        self.default[opt][0][length + 1 :]
                    )  # if the list has fewer items than the default, add the missing items.
                    self.config.set(sec, opt, self.getVarString(opt, temp))
                    
                if not temp[0]:
                    self.vals[opt] = []  # if temp is blank, just make it an empty array
                    return
                varType = {
                    "i": int,
                    "f": float,
                    "s": str,
                    "b": lambda s: s.lower() == "true",
                }[opt[1]]
                self.vals[opt] = [varType(item) for item in temp]
            except (NoSectionError, NoOptionError):
                self.vals[opt] = self.default.get(opt, ([],))[0]

        def strVar():
            try:
                self.vals[opt] = self.config.get(sec, opt)
            except (NoSectionError, NoOptionError):
                self.vals[opt] = self.default.get(opt, ("",))[0]

        t = opt[0]

        {"i": intVar, "f": floatVar, "s": strVar, "l": listVar, "b": boolVar}[t]()
        self.secs[opt] = sec


if __name__ == "__main__":

    c = ConfigManager(
        "D:\Work\Refactors\\test.ini",
        {
            "inum": (33, "main"),
            "fnum": (2.2, "main"),
            "sstring": ("sadasd", "temp"),
            "lilist": ([2, 3, 4], "list"),
        },
    )
    print(c.secs)
    print(c.vals)
