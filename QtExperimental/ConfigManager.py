
from configparser import ConfigParser

import os

class ConfigManager:
    
    def __init__(self, path, default:dict):
        self.default = default if default is not None else dict()
        self.config = ConfigParser()
        self.path = path
        if os.path.isfile(path):
            self.config.read(path)
        else:
            self.newConfig()
        
        
        self.vals = dict()
        self.secs = dict()
        for sec in self.config.sections():
            for opt in self.config.options(sec):
                self.loadVar(sec, opt)
                
        
    def newConfig(self):
        self.config.clear()
        self.vals.clear()
        
        for key, val in self.default.items():
            self.vals[key] = val[0]
            self.secs[key] = val[1]
            
            if not self.config.has_section(val[1]):
                self.config.add_section(val[1])
                
            self.config.set(val[1], key, str(val[0]))
            
        with open(self.path, "w") as file:
                self.config.write(file)
    
    def loadVar(self,sec, opt):
        
        def intVar():
            try:
                self.vals[opt] = self.config.getint(sec, opt)
            except:
                self.vals[opt] =self.default.get(opt, (0,))[0]
                
        def floatVar():
            try:
                self.vals[opt] = self.config.getfloat(sec, opt)
            except:
                self.vals[opt] =self.default.get(opt, (0,))[0]
        
        def listVar():
            try:
                temp = self.config.get(sec, opt).split('|')
                varType = {'i':int, 'f':float, 's':str}[opt[1]]
                self.vals[opt] = [varType(item) for item in temp]
        
            except:
                self.vals[opt] = self.default.get(opt, ([],))[0]
        
        def strVar():
            try:
                self.vals[opt] = self.config.get(sec, opt)
            except:
                self.vals[opt] = self.default.get(opt, ('',))[0]
        
        t = opt[0]
        
        {'i':intVar, 'f':floatVar, 's':strVar, 'l': listVar}[t]()
        self.secs[opt] = sec
        
if __name__ == '__main__':
    
    c = ConfigManager()