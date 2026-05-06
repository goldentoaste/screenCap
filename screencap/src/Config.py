from io import TextIOWrapper
from os import path, makedirs
from typing import Any, Callable, List, TypeVar, Dict, Set
import typing




class ConfigBase:
    '''
Config usage

1. Create a config class with desired config names and default values, inheriting ConfigBase.
Use python type hint for type checking on load. (but not on save)
This class is the metadata of the metadata.

Example:
```
class DemoConfig(Config):
    number: int  # defaults to 0
    colors: list[str] = ["...", "..."]
    value: float = 1234.5
```
2. create an instance of the config.
Ex: obj = createConfigInstance("./test.config", DemoConfig)
Note that the config file in disk is created if not exist

3. config data from disk or the default value is now loaded in the config instance (obj)


Other notes:
* Each method in ConfigBase is prefixed with "_", so that config attributes always appears before methods when using intellisense.
* After calling createConfigInstance(..., DemoConfig), the original class's attribute will be rewritten with the attribute name.
In this example, `DemoConfig.number == "number", DemoConfig.colors == "colors"`
This has some consequences:
    + This allows the config items's name to be referenced in a typesafe way, this is used to implement: `obj._registerCallback(DemoConfig.number, lambda: ...)`
    + However, the original default value is lost after calling createConfigInstance().
    + createConfigInstance should be only called once for each config class, ie, each should be unique within the app. Which is fine.
    '''
    class _SaveContext:
        def __init__(self, config: "ConfigBase") -> None:
            self.config = config

        def __enter__(self):
            self.config._pauseSave = True

        def __exit__(self, exc_type, exc_value, exc_traceback):
            self.config._save()

    def __init__(self, configPath: str, configNames: Set[str]) -> None:
        self._configNames: Set[str] = configNames
        self._sortedConfigNames: List[str] = sorted(configNames)
        self._configPath: str = configPath
        self._pauseSave = False
        self._callbacks: Dict[str, List[Callable[...]]] = dict()

    def _save(self):
        self._pauseSave = False
        with open(self._configPath, "a+", encoding="utf8") as f:
            f.seek(0)
            self._saveHelper(f)

    def _saveHelper(self, file: TextIOWrapper):
        """
        writes to disk, given a file stream
        """
        file.truncate(0)
        file.seek(0)

        for attr in self._sortedConfigNames:
            val = getattr(self, attr)
            if type(val) is list:
                file.write(f"{attr}={','.join(val)}\n")  # drop the bracket chars
            else:
                file.write(f"{attr}={getattr(self, attr)}\n")

    def _getBatchContext(self):
        return ConfigBase._SaveContext(self)

    def _pauseAutoSave(self):
        self._pauseSave = True

    def _registerCallback(self, attr: str | Any, callback: Callable):
        if attr not in self._callbacks:
            self._callbacks[attr] = []

        self._callbacks[attr].append(callback)

    def __setattr__(self, name: str, value: Any, /) -> None:
        if name.startswith("_"):
            super().__setattr__(name, value)
            return

        if value == getattr(self, name):
            return

        super().__setattr__(name, value)
        if name in self._callbacks:
            for callback in self._callbacks[name]:
                callback(value)

        if not self._pauseSave:
            self._save()


T = TypeVar("T", bound=ConfigBase)
strType = type(str())
boolType = type(bool())
intType = type(int())
floatType = type(float())


def getDefault(_type: type):
    if _type == strType:
        return ""
    if _type == boolType:
        return False
    if _type == intType:
        return 0
    if _type == floatType:
        return 0
    if _type.__name__.lower().find("list") != -1:
        return []
    raise RuntimeError(f"bad type: {_type}")


def createConfigInstance(configPath: str, configObj: type[T]) -> T:
    defaults: Dict[
        str, str | int | bool | float | List[str] | List[int] | List[bool] | List[float]
    ] = dict()
    types: Dict[
        str,
        type[str]
        | type[int]
        | type[bool]
        | type[List[str]]
        | type[List[int]]
        | type[List[float] | type[List[bool]]],
    ] = dict()

    for attr, _type in typing.get_type_hints(configObj).items():
        try:
            defaults[attr] = getattr(configObj, attr)
        except AttributeError:
            defaults[attr] = getDefault(_type)
        setattr(configObj, attr, attr)
        types[attr] = _type

    obj = configObj(
        configPath, set(defaults.keys())
    )  # pyright: ignore[reportCallIssue]

    # make folder containing config, if needed
    makedirs(path.dirname(configPath), exist_ok=True)

    with obj._getBatchContext():
        with open(configPath, "a+", encoding="utf8") as f:
            f.seek(0)

            lines = f.readlines()

            # read content of existing config file
            for line in lines:
                line = line.strip()
                idx = line.find("=")
                if idx == -1:
                    continue

                name = line[:idx]
                if name == "colors":
                    pass
                val = line[idx + 1 :]

                if name not in defaults:
                    continue

                _type = types[name]
                # try to assign casted value to config obj, assign default if not possible.
                try:
                    if _type == strType:
                        setattr(obj, name, str(val))
                    elif _type == intType:
                        setattr(obj, name, int(val))
                    elif _type == floatType:
                        setattr(obj, name, float(val))
                    elif _type == boolType:
                        setattr(
                            obj, name, val.lower() == "true"
                        )  # treat all non 'true' as false
                    elif _type.__name__.lower().find("list") != -1:
                        items = [
                            x.strip() for x in val.split(",")
                        ]  # comma separated, so content cannot contain "," this is not enforced.

                        if _type.__name__.find("int") != -1:
                            setattr(obj, name, [int(x) for x in items])
                        elif _type.__name__.find("float") != -1:
                            setattr(obj, name, [float(x) for x in items])
                        elif _type.__name__.find("bool") != -1:
                            setattr(obj, name, [x.lower() == "true" for x in items])
                        else:  # defaults to cast to string.
                            setattr(obj, name, [str(x) for x in items])
                    else:
                        raise RuntimeError(
                            f"Bad type for attribute: {name}, type is {_type}"
                        )

                except ValueError:
                    setattr(obj, name, defaults[name])

                # In case the attr is processed correctly, remove from defaults.
                defaults.pop(name)

            for name, val in defaults.items():
                setattr(obj, name, val)

            # overwrite contents of the config to ensure consistency
            obj._saveHelper(f)

    return obj


class _Config(ConfigBase):
    """
    Define the defaults config items and types here.
    """

    stringVal: str = "default"
    numberVal: int
    colors: List[str] = ["abc", "xyz"]
    floatVal: float


if __name__ == "__main__":
    # testing config

    obj = createConfigInstance("./test.config", _Config)
    print(obj.colors)
    print(_Config.colors)

    print(type(obj.colors))
    print(type(obj.floatVal))
    print(type(obj.numberVal))
    print(type(obj.stringVal))

    obj._registerCallback(_Config.floatVal, lambda x: print('nice', x))
    obj.floatVal = 1.2345222

