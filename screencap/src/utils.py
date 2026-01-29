from os import path, makedirs
from datetime import datetime
# TODO: use global constants instead
targetPath = "./screencap.log"

class Logger:
    # https://softwareengineering.stackexchange.com/a/380212
    __log: "Logger"
    makedirs(path.dirname(path.abspath(targetPath)), exist_ok=True)
    with open(targetPath, 'w', encoding='utf8') as f:
        pass # clear log on start

    @classmethod
    def log(cls, msg:str):
        print(f"Logger: {msg}")
        with open(targetPath, 'a', encoding='utf8') as f:
            f.write(f"{datetime.now().isoformat()}: {msg}")