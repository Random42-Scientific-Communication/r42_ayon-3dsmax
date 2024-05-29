from qtpy import QtWidgets, QtGui, QtCore


class ReviewExplorerUIGraphics(QtWidgets.QDialog):
    """
    The Graphics part of the UI to get the reviews from
    """

    def __init__(self):
        super().__init__()

        # -- Set Window Properties
        self.setWindowTitle("Review_Explorer")
        self.setWindowFlags(QtCore.Qt.WindowCloseButtonHint)
        self.setMinimumWidth(300)
        self.setSizePolicy(QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Expanding)

        # -- Create the layout
        self.layout = QtWidgets.QVBoxLayout()
        self.product_widget = QtWidgets.QWidget()
        self.product_layout= QtWidgets.QHBoxLayout(self.product_widget)

        # -- Create the widgets
        self.labelProducts = QtWidgets.QLabel("Review Products")
        self.comboProducts = QtWidgets.QComboBox()
        self.buttonReview = QtWidgets.QPushButton("Open Selected Review Folder")
        self.buttonXDriveFolder = QtWidgets.QPushButton("Open X Drive Folder")
        self.buttonMoveToX = QtWidgets.QPushButton("Move Selected to X Drive")
        self.buttonLatestToX = QtWidgets.QPushButton("Move Latest to X Drive")
        self.checkDebug = QtWidgets.QCheckBox("Toggle_Debug")
        self.debugBox = QtWidgets.QPlainTextEdit()
        self.debugBox.setVisible(False)

        # -- Attaching widgets to layout
        self.product_layout.addWidget(self.labelProducts)
        self.product_layout.addWidget(self.comboProducts)

        self.layout.addWidget(self.product_widget)
        self.layout.addWidget(self.buttonReview)
        self.layout.addWidget(self.buttonXDriveFolder)
        self.layout.addWidget(self.buttonMoveToX)
        self.layout.addWidget(self.buttonLatestToX)
        self.layout.addWidget(self.checkDebug)
        self.layout.addWidget(self.debugBox)
        self.setLayout(self.layout)