import sys
from PySide6.QtCore import QMetaObject, QSize, Qt
from PySide6.QtGui import QColor, QIcon

from PySide6.QtWidgets import (
    QApplication,
    QHBoxLayout,
    QLabel,
    QLayout,
    QPushButton,
    QSizePolicy,
    QWidget,
)

from screencap.src.GlobalContext import GlobalContext
from screencap.src.utils import pixmapWithMaskedColor


class CropUI(object):
    def setupUi(self, Form):
        if not Form.objectName():
            Form.setObjectName("Form")
        Form.resize(160, 28)
        Form.setContextMenuPolicy(Qt.ContextMenuPolicy.NoContextMenu)
        self.horizontalLayout = QHBoxLayout(Form)
        self.horizontalLayout.setSpacing(4)
        self.horizontalLayout.setObjectName("horizontalLayout")
        self.horizontalLayout.setSizeConstraint(QLayout.SizeConstraint.SetNoConstraint)
        self.horizontalLayout.setContentsMargins(0, 0, 0, 0)
        self.cutBtn = QPushButton(Form)
        self.cutBtn.setObjectName("cutBtn")
        sizePolicy = QSizePolicy(QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Minimum)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.cutBtn.sizePolicy().hasHeightForWidth())
        self.cutBtn.setSizePolicy(sizePolicy)
        self.cutBtn.setMinimumSize(QSize(28, 28))
        icon = QIcon()
        icon.addFile(
            "./screencap/icons/Cut.svg", QSize(), QIcon.Mode.Normal, QIcon.State.Off
        )
        self.cutBtn.setIcon(icon)
        self.cutBtn.setIconSize(QSize(20, 20))

        self.horizontalLayout.addWidget(self.cutBtn)

        self.copyBtn = QPushButton(Form)
        self.copyBtn.setObjectName("copyBtn")
        sizePolicy.setHeightForWidth(self.copyBtn.sizePolicy().hasHeightForWidth())
        self.copyBtn.setSizePolicy(sizePolicy)
        self.copyBtn.setMinimumSize(QSize(28, 28))
        icon1 = QIcon()
        icon1.addFile(
            "./screencap/icons/Copy.svg", QSize(), QIcon.Mode.Normal, QIcon.State.Off
        )
        self.copyBtn.setIcon(icon1)
        self.copyBtn.setIconSize(QSize(20, 20))

        self.horizontalLayout.addWidget(self.copyBtn)

        self.drawBtn = QPushButton(Form)
        self.drawBtn.setObjectName("darwBtn")
        sizePolicy.setHeightForWidth(self.drawBtn.sizePolicy().hasHeightForWidth())
        self.drawBtn.setSizePolicy(sizePolicy)
        self.drawBtn.setMinimumSize(QSize(28, 28))
        icon2 = QIcon()
        icon2.addFile(
            "./screencap/icons/Paint.svg", QSize(), QIcon.Mode.Normal, QIcon.State.Off
        )
        self.drawBtn.setIcon(icon2)
        self.drawBtn.setIconSize(QSize(20, 20))

        self.horizontalLayout.addWidget(self.drawBtn)

        self.noBtn = QPushButton(Form)
        self.noBtn.setObjectName("noBtn")
        sizePolicy.setHeightForWidth(self.noBtn.sizePolicy().hasHeightForWidth())
        self.noBtn.setSizePolicy(sizePolicy)
        self.noBtn.setMinimumSize(QSize(28, 28))
        icon3 = QIcon()
        icon3.addFile(
            "./screencap/icons/X.svg", QSize(), QIcon.Mode.Normal, QIcon.State.Off
        )
        self.noBtn.setIcon(icon3)
        self.noBtn.setIconSize(QSize(20, 20))

        self.horizontalLayout.addWidget(self.noBtn)

        self.yesBtn = QPushButton(Form)
        self.yesBtn.setObjectName("yesBtn")
        sizePolicy.setHeightForWidth(self.yesBtn.sizePolicy().hasHeightForWidth())
        self.yesBtn.setSizePolicy(sizePolicy)
        self.yesBtn.setMinimumSize(QSize(28, 28))
        icon4 = QIcon()
        icon4.addFile(
            "./screencap/icons/Check.svg", QSize(), QIcon.Mode.Normal, QIcon.State.Off
        )
        self.yesBtn.setIcon(icon4)
        self.yesBtn.setIconSize(QSize(20, 20))

        self.horizontalLayout.addWidget(self.yesBtn)

        self.retranslateUi(Form)

        QMetaObject.connectSlotsByName(Form)

    # setupUi

    def retranslateUi(self, Form):
        Form.setWindowTitle("")
        self.cutBtn.setText("")
        self.copyBtn.setText("")
        self.drawBtn.setText("")
        self.noBtn.setText("")
        self.yesBtn.setText("")

    # retranslateUi


class CropToolBar(QWidget, CropUI):

    def __init__(self, parent: QWidget) -> None:
        super().__init__(parent)

        self.setupUi(self)
        self.ctx = GlobalContext.getCtx()
        self.config = GlobalContext.getCtx().getConfig()

        self.updateTheme()

    def updateTheme(self):
        self.setStyleSheet(
            f"""
#thisWidget {{
    background:none;
}}

QPushButton {{
    border: 1px solid {self.config.border};
    background-color: {self.config.bgAlt};
    border-radius: 4px;
}}

QPushButton:hover{{
    border: 1px solid {self.config.borderAlt};
    background-color: {self.config.bgAlt2};
}}

QPushButton:pressed {{
    background-color: {self.config.bg};
}}
            """
        )
        self.adjustButton(self.yesBtn)
        self.adjustButton(self.noBtn)
        self.adjustButton(self.drawBtn)
        self.adjustButton(self.cutBtn)
        self.adjustButton(self.copyBtn)

    def adjustButton(self, btn: QPushButton):
        btn.setIcon(
            QIcon(
                pixmapWithMaskedColor(
                    btn.icon().pixmap(btn.iconSize()), QColor(self.config.fg)
                )
            )
        )


class Test(QWidget):

    def __init__(
        self,
    ):
        super().__init__()

        self.w = CropToolBar(self)
        self.adjustSize()

        self.show()


if __name__ == "__main__":
    a = QApplication()
    t = CropToolBar(None)
    t.show()
    sys.exit(a.exec())
