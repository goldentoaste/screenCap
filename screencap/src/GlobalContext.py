
class GlobalContext:
    '''
    Store global states here
    When critical components are made, store a reference here to avoid passing things around too much.
    '''

    __instance: "GlobalContext | None" = None


    def __init__(self) -> None:
        pass

    @classmethod
    def getCtx(cls):
        if not GlobalContext.__instance:
            GlobalContext.__instance = GlobalContext()
        return GlobalContext.__instance

