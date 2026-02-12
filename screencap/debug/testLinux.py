policyTemplate = """<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE policyconfig PUBLIC
    "-//freedesktop//DTD PolicyKit Policy Configuration 1.0//EN"
    "http://www.freedesktop.org/standards/PolicyKit/1.0/policyconfig.dtd">
    <policyconfig>
    <action id="com.yourname.screencap.input">
        <description>Allow ScreenCap to access input devices</description>
        <message>Authentication is required to access input devices</message>
        <defaults>
        <allow_any>auth_admin</allow_any>
        <allow_inactive>auth_admin</allow_inactive>
        <allow_active>auth_admin_keep</allow_active>
        </defaults>
        <annotate key="org.freedesktop.policykit.exec.path">{path}</annotate>
        <annotate key="org.freedesktop.policykit.exec.allow_gui">true</annotate>
    </action>
</policyconfig>
"""


policyTarget = "/usr/share/polkit-1/actions/com.goldentoaste.screencap.input.policy"

import os
import subprocess
import sys

from PySide6.QtWidgets import QApplication, QWidget

def createPolicy(relPath:str):
    with open(policyTarget, 'w', encoding="utf8") as f:
        f.write(policyTemplate.format(path=os.path.abspath(relPath)))


class Tester(QWidget):

    def __init__(self) -> None:
        super().__init__(None)

        self.setGeometry(200, 200, 400, 400)
        self.show()

        createPolicy("./helper")

        subprocess.run([
            "pkexec",
            "./helper",
        ], check=True) # start socket




if __name__  == '__main__':
    a = QApplication()
    t = Tester()
    sys.exit(a.exec())