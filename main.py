# Import built-in modules
import os

import maya.cmds as cmds
import pymel.core as pmc

import os
import sys

file_dir = os.path.dirname(__file__)
sys.path.append(file_dir)

# Import third-party modules
from PySide2 import QtCore, QtGui, QtWidgets

import importlib as imp
from dw_kong_render_setup import functions
imp.reload(functions)


tool_name = "Omegas Render Setup"
version = "v001"

class SelectionManagerWidget(QtWidgets.QWidget):
    """
    Custom Qt Widget with selection list widget, add, remove and clear btn
    """
    def __init__(self, name="Content"):

        super(SelectionManagerWidget, self).__init__()

        layout = QtWidgets.QVBoxLayout()
        self.lbl_name = QtWidgets.QLabel()
        self.lbl_name.setText(name)
        font = QtGui.QFont()
        font.setPointSize(7)
        font.setBold(True)
        font.setWeight(75)
        self.lbl_name.setFont(font)
        layout.addWidget(self.lbl_name)

        self.lw_selection = QtWidgets.QListWidget()
        self.lw_selection.setSelectionMode(QtWidgets.QAbstractItemView.ExtendedSelection)
        layout.addWidget(self.lw_selection)

        layout_controls = QtWidgets.QHBoxLayout()

        self.btn_add_content = QtWidgets.QPushButton("+")
        self.btn_add_content.setMinimumSize(QtCore.QSize(0, 15))
        self.btn_add_content.setObjectName("btn_add_content")
        layout_controls.addWidget(self.btn_add_content)

        self.btn_remove_content = QtWidgets.QPushButton("-")
        self.btn_remove_content.setMinimumSize(QtCore.QSize(0, 15))
        self.btn_remove_content.setObjectName("btn_remove_content")
        layout_controls.addWidget(self.btn_remove_content)

        self.btn_clear_content = QtWidgets.QToolButton()
        self.btn_clear_content.setMinimumSize((QtCore.QSize(0, 15)))
        self.btn_clear_content.setIcon(self.btn_clear_content.style().standardIcon(QtWidgets.QStyle.SP_DialogCancelButton))
        self.btn_clear_content.setObjectName("btn_clear_content")
        layout_controls.addWidget(self.btn_clear_content)

        layout.addLayout(layout_controls)

        self.setLayout(layout)

        self.btn_add_content.clicked.connect(lambda : self.populate(self.lw_selection))
        self.btn_remove_content.clicked.connect(lambda : self.remove_sel(self.lw_selection))
        self.btn_clear_content.clicked.connect(lambda : self.clear_list(self.lw_selection))



    def get_items(self, listWidget):
        items = [i for i in listWidget.findItems("", QtCore.Qt.MatchContains)]

        return items

    def remove_sel(self, listWidget):
        listWidget = listWidget
        listItems = listWidget.selectedItems()

        if not listItems:
            return
        for item in listItems:
            listWidget.takeItem(listWidget.row(item))

    def clear_list(self, listWidget):
        listWidget = listWidget

        items = self.get_items(listWidget)

        if not items:
            return
        for item in items:
            listWidget.takeItem(listWidget.row(item))

    def populate(self, listWidget):
        listWidget = listWidget

        sel = pmc.ls(sl=1)

        existing = [i.text() for i in self.get_items(listWidget)]

        for obj in sel:
            name = str(obj)
            if obj in existing:
                continue
            listWidget.addItem(name)

        listWidget.scrollToBottom()

    def clear_file_path(self):
        print ("Clearing Widget {}".format(self.le_file_path))
        self.le_file_path.setText("")
        self.drp_cc_select.setCurrentText("Off")
        return

class Ui_kong_render_setup_generatorWindow(object):

    def __init__(self):
        self.geo = None
        self.sg = ""
        self.asset_name = "default"
        self.variations = {}

    def setupUi(self, kong_render_setup_generatorWindow):

        kong_render_setup_generatorWindow.setObjectName("kong_render_setup_generatorWindow")
        kong_render_setup_generatorWindow.resize(600, 300)

        self.build_default_header(kong_render_setup_generatorWindow)

        self.build_help()

        # Tool Specific UI

        self.gL_main_grp = QtWidgets.QGridLayout()
        self.gL_main_grp.setObjectName("gL_source")


        hL_main_controls = QtWidgets.QHBoxLayout()

        vL_content = QtWidgets.QVBoxLayout()
        self.content_widget = SelectionManagerWidget("Beauty Geo")
        vL_content.addWidget(self.content_widget)

        self.shadow_catch_content = SelectionManagerWidget("Shadow Catch Geo")
        vL_content.addWidget(self.shadow_catch_content)

        hL_main_controls.addLayout(vL_content)


        """"

        # Add Geo Widgets

        self.lbl_geo = QtWidgets.QLabel("Geo")
        font = QtGui.QFont()
        font.setPointSize(7)
        font.setBold(True)
        font.setWeight(75)
        self.lbl_geo.setFont(font)
        self.lbl_geo.setAlignment(
            QtCore.Qt.AlignLeft | QtCore.Qt.AlignVCenter
        )
        self.lbl_geo.setObjectName("lbl_geo")
        self.gL_main_grp.addWidget(self.lbl_geo, 0, 0)

        self.le_geo = QtWidgets.QLineEdit(self.centralwidget)
        self.le_geo.setMinimumSize(QtCore.QSize(250, 30))
        self.le_geo.setAlignment(
            QtCore.Qt.AlignLeft | QtCore.Qt.AlignVCenter
        )
        # self.le_export_path.setDragEnabled(True)
        self.le_geo.setObjectName("le_geo")
        self.le_geo.setEnabled(False)
        self.gL_main_grp.addWidget(self.le_geo, 1, 0)

        self.btn_load_geo = QtWidgets.QToolButton()
        self.btn_load_geo.setMinimumSize(QtCore.QSize(0, 30))
        self.btn_load_geo.setIcon(self.btn_load_geo.style().standardIcon(QtWidgets.QStyle.SP_DialogOkButton))
        self.btn_load_geo.setObjectName("btn_shader")
        #self.set_export_path()

        self.gL_main_grp.addWidget(self.btn_load_geo, 1, 1)
        """

        # Add Shader Widgets

        self.lbl_shader = QtWidgets.QLabel("Shader")
        font = QtGui.QFont()
        font.setPointSize(7)
        font.setBold(True)
        font.setWeight(75)
        self.lbl_shader.setFont(font)
        self.lbl_shader.setAlignment(
            QtCore.Qt.AlignLeft | QtCore.Qt.AlignVCenter
        )
        self.lbl_shader.setObjectName("lbl_shader")
        self.gL_main_grp.addWidget(self.lbl_shader, 0, 0)

        self.le_shader = QtWidgets.QLineEdit(self.centralwidget)
        self.le_shader.setMinimumSize(QtCore.QSize(250, 30))
        self.le_shader.setAlignment(
            QtCore.Qt.AlignLeft | QtCore.Qt.AlignVCenter
        )
        # self.le_export_path.setDragEnabled(True)
        self.le_shader.setObjectName("le_shader")
        self.le_shader.setEnabled(False)
        self.gL_main_grp.addWidget(self.le_shader, 1, 0)

        self.btn_load_shader = QtWidgets.QToolButton()
        self.btn_load_shader.setMinimumSize(QtCore.QSize(0, 30))
        self.btn_load_shader.setIcon(self.btn_load_shader.style().standardIcon(QtWidgets.QStyle.SP_DialogOkButton))
        self.btn_load_shader.setObjectName("btn_load_shader")

        self.gL_main_grp.addWidget(self.btn_load_shader, 1, 1)

        self.lbl_asset_name = QtWidgets.QLabel("Asset Name")
        self.lbl_asset_name.setFont(font)
        self.lbl_asset_name.setAlignment(
            QtCore.Qt.AlignLeft | QtCore.Qt.AlignVCenter
        )
        self.gL_main_grp.addWidget(self.lbl_asset_name, 2, 0)

        self.le_asset_name = QtWidgets.QLineEdit(self.centralwidget)
        self.le_asset_name.setMinimumSize(QtCore.QSize(250, 25))
        self.le_asset_name.setAlignment(
            QtCore.Qt.AlignLeft | QtCore.Qt.AlignVCenter
        )
        #self.le_asset_name.setEnabled(False)
        self.gL_main_grp.addWidget(self.le_asset_name, 3, 0)

        self.lbl_asset_category = QtWidgets.QLabel("Asset Category")
        self.lbl_asset_category.setFont(font)
        self.lbl_asset_category.setAlignment(
            QtCore.Qt.AlignLeft | QtCore.Qt.AlignVCenter
        )
        self.gL_main_grp.addWidget(self.lbl_asset_category, 4, 0)

        self.le_asset_category = QtWidgets.QLineEdit(self.centralwidget)
        self.le_asset_category.setMinimumSize(QtCore.QSize(250, 25))
        self.le_asset_category.setAlignment(
            QtCore.Qt.AlignLeft | QtCore.Qt.AlignVCenter
        )
        #self.le_asset_category.setEnabled(False)
        self.gL_main_grp.addWidget(self.le_asset_category, 5, 0)

        self.lbl_filename_prefix = QtWidgets.QLabel("File Name Prefix")
        self.lbl_filename_prefix.setFont(font)
        self.lbl_filename_prefix.setAlignment(
            QtCore.Qt.AlignLeft | QtCore.Qt.AlignVCenter
        )
        self.gL_main_grp.addWidget(self.lbl_filename_prefix, 6, 0)

        self.le_filename_prefix = QtWidgets.QLineEdit(self.centralwidget)
        self.le_filename_prefix.setMinimumSize(QtCore.QSize(250, 25))
        self.le_filename_prefix.setAlignment(
            QtCore.Qt.AlignLeft | QtCore.Qt.AlignVCenter
        )
        # self.le_asset_category.setEnabled(False)
        self.gL_main_grp.addWidget(self.le_filename_prefix, 7, 0)

        self.lbl_background = QtWidgets.QLabel("Background Selector")
        self.lbl_background.setFont(font)
        self.lbl_background.setAlignment(
            QtCore.Qt.AlignLeft | QtCore.Qt.AlignVCenter
        )
        self.gL_main_grp.addWidget(self.lbl_background, 8, 0)

        self.le_background = QtWidgets.QLineEdit(self.centralwidget)
        self.le_background.setMinimumSize(QtCore.QSize(250, 25))
        self.le_background.setAlignment(
            QtCore.Qt.AlignLeft | QtCore.Qt.AlignVCenter
        )
        # self.le_asset_category.setEnabled(False)

        self.gL_main_grp.addWidget(self.le_background, 9, 0)

        vL_shader_controls = QtWidgets.QVBoxLayout()
        vL_shader_controls.addLayout(self.gL_main_grp)
        hL_main_controls.addLayout(vL_shader_controls)
        self.verticalLayout.addLayout(hL_main_controls)

        spacerItem7 = QtWidgets.QSpacerItem(
            10, 10, QtWidgets.QSizePolicy.Minimum, QtWidgets.QSizePolicy.Minimum
        )
        self.verticalLayout.addItem(spacerItem7)

        self.btn_build_layers = QtWidgets.QPushButton()
        self.verticalLayout.addWidget(self.btn_build_layers)

        spacerItem9 = QtWidgets.QSpacerItem(
            10, 10, QtWidgets.QSizePolicy.Minimum, QtWidgets.QSizePolicy.Minimum
        )
        self.verticalLayout.addItem(spacerItem9)


        kong_render_setup_generatorWindow.setCentralWidget(self.centralwidget)
        self.retranslateUi(kong_render_setup_generatorWindow)

    def build_help(self):
        # Help Button
        self.hL_help = QtWidgets.QHBoxLayout()
        self.hL_help.setObjectName("hL_help")
        self.btn_help = QtWidgets.QToolButton()
        # self.btn_help.setIconSize(QtCore.QSize(10, 10))
        font = QtGui.QFont()
        font.setBold(True)
        font.setUnderline(True)
        font.setWeight(75)
        font.setPointSize(7)
        self.btn_help.setFont(font)
        self.btn_help.setStyleSheet("color: rgb(77, 187, 237);")
        self.btn_help.setObjectName("btn_help")
        self.hL_help.addWidget(self.btn_help)
        self.hL_help.setAlignment(
            QtCore.Qt.AlignRight | QtCore.Qt.AlignTrailing | QtCore.Qt.AlignVCenter
        )
        self.verticalLayout.addLayout(self.hL_help)
        spacerItem_help = QtWidgets.QSpacerItem(
            20, 20, QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Minimum
        )
        self.verticalLayout.addItem(spacerItem_help)

    def build_default_header(self, kong_render_setup_generatorWindow):
        # Setting up the default PXO header
        self.centralwidget = QtWidgets.QWidget(kong_render_setup_generatorWindow)
        self.centralwidget.setObjectName("centralwidget")
        self.verticalLayout = QtWidgets.QVBoxLayout(self.centralwidget)
        self.verticalLayout.setObjectName("verticalLayout")
        self.gridLayout = QtWidgets.QGridLayout()
        self.gridLayout.setObjectName("gridLayout")
        # Shot Field Displaying current Workspace
        self.shotField = QtWidgets.QLabel(self.centralwidget)
        font = QtGui.QFont()
        font.setPointSize(7)
        self.shotField.setFont(font)
        self.shotField.setAlignment(
            QtCore.Qt.AlignRight | QtCore.Qt.AlignTrailing | QtCore.Qt.AlignVCenter
        )
        self.shotField.setObjectName("shotField")
        # Getting Contents from environment variables

        self.gridLayout.addWidget(self.shotField, 2, 2, 1, 1)
        self.projectField = QtWidgets.QLabel(self.centralwidget)
        font = QtGui.QFont()
        font.setPointSize(7)
        font.setBold(True)
        font.setWeight(75)
        self.projectField.setFont(font)
        self.projectField.setAlignment(
            QtCore.Qt.AlignRight | QtCore.Qt.AlignTrailing | QtCore.Qt.AlignVCenter
        )
        self.projectField.setObjectName("projectField")
        self.gridLayout.addWidget(self.projectField, 1, 2, 1, 1)

        # Adding the tool name header
        self.toolName = QtWidgets.QLabel(self.centralwidget)
        font = QtGui.QFont()
        font.setPointSize(14)
        font.setBold(True)
        font.setWeight(75)
        self.toolName.setFont(font)
        self.toolName.setAlignment(
            QtCore.Qt.AlignLeft | QtCore.Qt.AlignVCenter # QtCore.Qt.AlignTrailing
        )
        self.toolName.setObjectName("toolName")
        self.gridLayout.addWidget(self.toolName, 0, 0, 4, 1)
        # Adding Spacers and Lines
        spacerItem = QtWidgets.QSpacerItem(
            40, 10, QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Minimum
        )
        self.gridLayout.addItem(spacerItem, 4, 0, 1, 1)
        self.verticalLine = QtWidgets.QFrame(self.centralwidget)
        sizePolicy = QtWidgets.QSizePolicy(
            QtWidgets.QSizePolicy.Minimum, QtWidgets.QSizePolicy.Preferred
        )
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.verticalLine.sizePolicy().hasHeightForWidth())
        self.verticalLine.setSizePolicy(sizePolicy)
        self.verticalLine.setFrameShadow(QtWidgets.QFrame.Plain)
        self.verticalLine.setFrameShape(QtWidgets.QFrame.VLine)
        self.verticalLine.setObjectName("verticalLine")
        self.gridLayout.addWidget(self.verticalLine, 0, 1, 4, 1)
        spacerItem1 = QtWidgets.QSpacerItem(
            40, 10, QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Minimum
        )
        self.gridLayout.addItem(spacerItem1, 4, 2, 1, 1)
        self.horizontalLineTop = QtWidgets.QFrame(self.centralwidget)
        self.horizontalLineTop.setFrameShadow(QtWidgets.QFrame.Plain)
        self.horizontalLineTop.setFrameShape(QtWidgets.QFrame.HLine)
        self.horizontalLineTop.setObjectName("horizontalLineTop")
        self.gridLayout.addWidget(self.horizontalLineTop, 5, 0, 1, 3)
        spacerItem2 = QtWidgets.QSpacerItem(
            40, 10, QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Minimum
        )
        self.verticalLayout.addItem(spacerItem2)
        self.verticalLayout.addLayout(self.gridLayout)

    def retranslateUi(self, kong_render_setup_generatorWindow):
        _translate = QtCore.QCoreApplication.translate
        kong_render_setup_generatorWindow.setWindowTitle(
            _translate(
                "kong_render_setup_generatorWindow", "{} {}".format(tool_name, version)
            )
        )
        self.projectField.setText(
            "Written for Meta by Art"
        )

        self.shotField.setText(
            "Project: AKC"
        )

        self.toolName.setText(
            "DW Render Setup"
        )

        self.le_background.setText("background_grp")

        self.btn_help.setText(_translate("kong_render_setup_generatorWindow", "Documentation"))
        self.btn_help.clicked.connect(lambda : functions.show_help())


        self.btn_load_shader.clicked.connect(lambda: self.load_shader())
        #self.btn_load_geo.clicked.connect(lambda: self.load_geo())

        self.le_asset_category.textChanged.connect(lambda: self.le_filename_prefix.setText(
            self.build_filename_prefix(self.le_asset_category.text())))


        self.btn_build_layers.setText("Build Layers")
        self.btn_build_layers.clicked.connect(lambda : self.build_layers_clicked())

    def build_filename_prefix(self, category):
        file_name_prefix = "shuffle/" + category  + "/<RenderLayer>"
        return file_name_prefix

    def load_geo(self):

        text = functions.load_selected_geo()
        self.geo = text[0]
        if text:
            self.le_geo.setText(text[-1])
        else:
            self.le_geo.setText("")

    def load_shader(self):

        valid, self.sg, self.asset_name, self.variations = functions.load_selected_shader(pmc.ls(sl=1))

        file_name_prefix = self.build_filename_prefix(self.asset_name)

        if valid:
            self.le_shader.setText(str(self.sg))
            self.le_asset_name.setText(self.asset_name)
            self.le_asset_category.setText(self.asset_name)
            self.le_filename_prefix.setText(file_name_prefix)
        else:
            self.le_shader.setText("")
            self.le_asset_name.setText("")
            self.le_asset_category.setText("")
            self.le_filename_prefix.setText("")

    def build_layers_clicked(self):

        self.geo = [item.text() for item in self.content_widget.get_items(self.content_widget.lw_selection)]

        self.shadow_catch_geo = [item.text() for item in self.shadow_catch_content.get_items(self.shadow_catch_content.lw_selection)]

        if not self.geo:
            pmc.warning("Please define Geo first.")
            return
        if not self.sg:
            pmc.warning("Please define a Shading Engine first.")
            return

        # fetch asset name and file name prefix again since it might have changed
        # by user input

        self.asset_name = self.le_asset_name.text()
        if not self.asset_name:
            pmc.warning("No Valid asset name found, aborting.")
            return

        filename_prefix = self.le_filename_prefix.text()
        if not filename_prefix:
            pmc.warning("No Valid file name prefix found, aborting.")
            return

        bg_selector = self.le_background.text()
        if not bg_selector:
            pmc.warning("No Valid bg selector found, aborting.")
            return

        functions.build_render_setup(self.geo, self.shadow_catch_geo, self.asset_name, filename_prefix, self.sg, self.variations, bg_selector)



def run():
    """Launch the app."""

    windowName = "kong_render_setup_generatorWindow"

    functions.kill_existing_app(windowName)


    app = QtWidgets.QApplication.instance()

    for obj in QtWidgets.QApplication.topLevelWidgets():
        if obj.objectName() == "MayaWindow":
            kong_render_setup_generatorWindow = QtWidgets.QMainWindow(obj)
            ui = Ui_kong_render_setup_generatorWindow()
            ui.setupUi(kong_render_setup_generatorWindow)
            kong_render_setup_generatorWindow.show()

