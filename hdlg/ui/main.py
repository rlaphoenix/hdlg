from hdlg.ui import BaseWindow


class Main(BaseWindow):
    def __init__(self):
        super().__init__(name=self.__class__.__name__)

        self.window.setMinimumSize(1000, 400)

        self.window.actionExit.triggered.connect(self.window.close)
        self.window.actionAbout.triggered.connect(self.about)
