
from screencap.src.Config import ConfigBase, createConfigInstance


defaultConfigLocation = "./screenCap.config"

class GlobalContext:
    '''
    Store global states here
    When critical components are made, store a reference here to avoid passing things around too much.
    '''

    __instance: "GlobalContext | None" = None


    def __init__(self) -> None:
        self.config = createConfigInstance(defaultConfigLocation, Config)


    @classmethod
    def getCtx(cls):
        if not GlobalContext.__instance:
            GlobalContext.__instance = GlobalContext()
        return GlobalContext.__instance

    def getConfig(self):
        return self.config

class Config(ConfigBase):
    # Colors, TODO make color profiles

    bg: str = "#282828"
    bgTrans : str = "#28282844"
    bgAlt: str = "#3c3836"

    fg: str = "#fbf1c7"
    fgAlt: str = "#ebdbb2"

    border: str = "#a89984"