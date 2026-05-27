
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
    bgTrans : str = "#28282888"
    bgAlt: str = "#3c3836"
    bgAlt2 : str = "#504945"

    fg: str = "#fbf1c7"
    fgAlt: str = "#ebdbb2"

    border: str = "#a89984"
    borderAlt: str =  "#7c6f64"
    borderTrans: str = "#77a89984"

    #### SNAPSHOT CONTROLS ####
    quickSnap : bool = True