from configparser import ConfigParser
from os import path, getenv

configDir = path.join(getenv("appdata"), "screenCap")
configFile = path.join(configDir, "config.ini")

#not needed I think
class ConfigManager:
    
    def __init__(self, path):
        self.config = ConfigParser()
        self.variables = dict() #varName: (value, section, callback pointer[list])
        self.config.read(configFile)
        
        # #initialize 
        # for section in self.config.sections:
        #     for varName in self.config.keys():
        #         if varName[0] == "i":
        #             pass #handle integer
        #         elif varName[1] == "s":
        #             pass #handle string
        
        
    def getIntConfig(self, section, varName, default=0):
        try:
            return self.config.getint(section, varName)
        except Exception:
            return default


    def getStrConfig(self,section, varName, default=""):
        try:
            return self.config.get(section, varName)
        except Exception:
            return default

    
if __name__ == "__main__":
    pass