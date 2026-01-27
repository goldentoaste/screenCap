
from types import UnionType


from betterconf import betterconf, JSONProvider
from typing import Any, List, TypeVar, Union, Type, Generic, ClassVar, Dict
import typing

# print(typing.get_type_hints(Config))

class ConfigBase:
    def A(self):
        pass

    def B(self):
        pass

T = TypeVar("T")
strType = type(str())
boolType = type(bool())
intType = type(int)
floatType = type(float)
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
    raise RuntimeError(f"bad type: {_type}" )

print(getDefault(List[int]))


def createConfigInstance(configPath:str, configObj:T)-> T:
    defaults: Dict[str, str | int | bool| List[str | int | bool]] = dict()
    types: Dict[str, type[str] | type[int] | type[bool] | type[List[str | int | bool]]] = dict()
    vals : Dict[str, str | int | bool| List[str | int | bool]] = dict()

    print(configObj)



    for attr, _type in typing.get_type_hints(configObj).items():
        try:
            defaults[attr] = getattr(configObj, attr)
        except AttributeError:
            defaults[attr] = getDefault(_type)
        setattr(configObj, attr, attr)
        types[attr] = _type

    with open(configPath, 'w', encoding='utf8') as f:
        lines = f.readlines()

        for line in lines:
            idx = line.find("=")
            if idx == -1:
                continue

            name = line[:idx]
            val = line[idx + 1:]

            if name not in defaults:
                continue



            match types[name]:
                case strType:
                    pass



    return configObj()  # pyright: ignore[reportCallIssue]

class Config(ConfigBase):
    '''
    Define the defaults config items and types here.
    '''

    stringVal: str = "default"
    numberVal: int = 2
    colors: List[str] = ["asdasdad"]




# y = createConfigInstance("", Config)




class Tester:
    val = 123

    def __getattribute__(self, name: str, /) :
        return 456


print(Tester.val)
print(Tester().val)


