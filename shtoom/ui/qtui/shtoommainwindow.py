# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'shtoommainwindow.ui'
#
# Created: Wed Jan 19 15:16:20 2005
#      by: The PyQt User Interface Compiler (pyuic) 3.13
#
# WARNING! All changes made in this file will be lost!


from qt import *

class ShtoomMainWindow(QMainWindow):
    def __init__(self,parent = None,name = None,fl = 0):
        QMainWindow.__init__(self,parent,name,fl)
        self.statusBar()

        if not name:
            self.setName("ShtoomMainWindow")


        self.setCentralWidget(QWidget(self,"qt_central_widget"))
        ShtoomMainWindowLayout = QVBoxLayout(self.centralWidget(),11,6,"ShtoomMainWindowLayout")

        layout4 = QHBoxLayout(None,0,6,"layout4")

        self.textLabel1 = QLabel(self.centralWidget(),"textLabel1")
        self.textLabel1.setAlignment(QLabel.AlignVCenter | QLabel.AlignRight)
        layout4.addWidget(self.textLabel1)

        self.addressComboBox = QComboBox(0,self.centralWidget(),"addressComboBox")
        self.addressComboBox.setSizePolicy(QSizePolicy(QSizePolicy.Expanding,QSizePolicy.Minimum,0,0,self.addressComboBox.sizePolicy().hasHeightForWidth()))
        self.addressComboBox.setEditable(1)
        layout4.addWidget(self.addressComboBox)

        self.lookupButton = QPushButton(self.centralWidget(),"lookupButton")
        self.lookupButton.setSizePolicy(QSizePolicy(QSizePolicy.Minimum,QSizePolicy.Minimum,0,0,self.lookupButton.sizePolicy().hasHeightForWidth()))
        self.lookupButton.setMaximumSize(QSize(25,32767))
        layout4.addWidget(self.lookupButton)
        ShtoomMainWindowLayout.addLayout(layout4)

        layout2 = QHBoxLayout(None,0,6,"layout2")

        self.callButton = QPushButton(self.centralWidget(),"callButton")
        self.callButton.setSizePolicy(QSizePolicy(QSizePolicy.Minimum,QSizePolicy.Minimum,0,0,self.callButton.sizePolicy().hasHeightForWidth()))
        layout2.addWidget(self.callButton)

        self.hangupButton = QPushButton(self.centralWidget(),"hangupButton")
        self.hangupButton.setSizePolicy(QSizePolicy(QSizePolicy.Minimum,QSizePolicy.Minimum,0,0,self.hangupButton.sizePolicy().hasHeightForWidth()))
        layout2.addWidget(self.hangupButton)

        self.registerButton = QPushButton(self.centralWidget(),"registerButton")
        self.registerButton.setSizePolicy(QSizePolicy(QSizePolicy.Minimum,QSizePolicy.Minimum,0,0,self.registerButton.sizePolicy().hasHeightForWidth()))
        layout2.addWidget(self.registerButton)
        ShtoomMainWindowLayout.addLayout(layout2)

        self.statusLabel = QLabel(self.centralWidget(),"statusLabel")
        ShtoomMainWindowLayout.addWidget(self.statusLabel)

        self.fileDTMFAction = QAction(self,"fileDTMFAction")
        self.fileDTMFAction.setEnabled(1)
        self.fileDebugAction = QAction(self,"fileDebugAction")
        self.fileDebugAction.setEnabled(1)
        self.fileExitAction = QAction(self,"fileExitAction")
        self.helpAboutAction = QAction(self,"helpAboutAction")
        self.editPreferencesAction = QAction(self,"editPreferencesAction")




        self.MenuBar = QMenuBar(self,"MenuBar")


        self.fileMenu = QPopupMenu(self)
        self.fileDTMFAction.addTo(self.fileMenu)
        self.fileDebugAction.addTo(self.fileMenu)
        self.fileMenu.insertSeparator()
        self.fileExitAction.addTo(self.fileMenu)
        self.MenuBar.insertItem(QString(""),self.fileMenu,1)

        self.Edit = QPopupMenu(self)
        self.editPreferencesAction.addTo(self.Edit)
        self.MenuBar.insertItem(QString(""),self.Edit,2)

        self.helpMenu = QPopupMenu(self)
        self.helpAboutAction.addTo(self.helpMenu)
        self.MenuBar.insertItem(QString(""),self.helpMenu,3)


        self.languageChange()

        self.resize(QSize(343,156).expandedTo(self.minimumSizeHint()))
        self.clearWState(Qt.WState_Polished)

        self.connect(self.fileDTMFAction,SIGNAL("activated()"),self.fileDTMF)
        self.connect(self.fileDebugAction,SIGNAL("activated()"),self.fileDebugging)
        self.connect(self.editPreferencesAction,SIGNAL("activated()"),self.editPreferences)
        self.connect(self.fileExitAction,SIGNAL("activated()"),self.fileExit)
        self.connect(self.helpAboutAction,SIGNAL("activated()"),self.helpAbout)
        self.connect(self.callButton,SIGNAL("clicked()"),self.callButton_clicked)
        self.connect(self.hangupButton,SIGNAL("clicked()"),self.hangupButton_clicked)
        self.connect(self.registerButton,SIGNAL("clicked()"),self.registerButton_clicked)
        self.connect(self.lookupButton,SIGNAL("clicked()"),self.lookupButton_clicked)


    def languageChange(self):
        self.setCaption(self.__tr("Shtoom"))
        self.textLabel1.setText(self.__tr("Address"))
        self.lookupButton.setText(self.__tr("..."))
        self.callButton.setText(self.__tr("Call"))
        self.hangupButton.setText(self.__tr("Hang Up"))
        self.registerButton.setText(self.__tr("Register"))
        self.statusLabel.setText(QString.null)
        self.fileDTMFAction.setText(self.__tr("DTMF"))
        self.fileDTMFAction.setMenuText(self.__tr("DTMF"))
        self.fileDTMFAction.setToolTip(self.__tr("Show DTMF Window"))
        self.fileDTMFAction.setAccel(self.__tr("Ctrl+D"))
        self.fileDebugAction.setText(self.__tr("Debug Log"))
        self.fileDebugAction.setMenuText(self.__tr("Debug Log"))
        self.fileDebugAction.setToolTip(self.__tr("Show Debugging Log"))
        self.fileDebugAction.setAccel(self.__tr("Ctrl+O"))
        self.fileExitAction.setText(self.__tr("Exit"))
        self.fileExitAction.setMenuText(self.__tr("Exit"))
        self.fileExitAction.setAccel(QString.null)
        self.helpAboutAction.setText(self.__tr("About"))
        self.helpAboutAction.setMenuText(self.__tr("About"))
        self.helpAboutAction.setAccel(QString.null)
        self.editPreferencesAction.setText(self.__tr("Preferences"))
        self.editPreferencesAction.setMenuText(self.__tr("Preferences"))
        self.editPreferencesAction.setAccel(self.__tr("Ctrl+P"))
        if self.MenuBar.findItem(1):
            self.MenuBar.findItem(1).setText(self.__tr("File"))
        if self.MenuBar.findItem(2):
            self.MenuBar.findItem(2).setText(self.__tr("Edit"))
        if self.MenuBar.findItem(3):
            self.MenuBar.findItem(3).setText(self.__tr("Help"))


    def fileDTMF(self):
        print "ShtoomMainWindow.fileDTMF(): Not implemented yet"

    def fileDebugging(self):
        print "ShtoomMainWindow.fileDebugging(): Not implemented yet"

    def fileExit(self):
        print "ShtoomMainWindow.fileExit(): Not implemented yet"

    def editPreferences(self):
        print "ShtoomMainWindow.editPreferences(): Not implemented yet"

    def helpAbout(self):
        print "ShtoomMainWindow.helpAbout(): Not implemented yet"

    def callButton_clicked(self):
        print "ShtoomMainWindow.callButton_clicked(): Not implemented yet"

    def hangupButton_clicked(self):
        print "ShtoomMainWindow.hangupButton_clicked(): Not implemented yet"

    def registerButton_clicked(self):
        print "ShtoomMainWindow.registerButton_clicked(): Not implemented yet"

    def lookupButton_clicked(self):
        print "ShtoomMainWindow.lookupButton_clicked(): Not implemented yet"

    def __tr(self,s,c = None):
        return qApp.translate("ShtoomMainWindow",s,c)
