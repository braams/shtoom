# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'shtoommainwindow.ui'
#
# Created: Thu Jun 17 21:20:45 2004
#      by: The PyQt User Interface Compiler (pyuic) 3.12
#
# WARNING! All changes made in this file will be lost!


from qt import *

class ShtoomMainWindow(QMainWindow):
    def __init__(self,parent = None,name = None,fl = 0):
        QMainWindow.__init__(self,parent,name,fl)
        self.statusBar()

        if not name:
            self.setName("ShtoomMainWindow")

        self.setSizePolicy(QSizePolicy(0,7,0,0,self.sizePolicy().hasHeightForWidth()))
        self.setMinimumSize(QSize(408,444))

        self.setCentralWidget(QWidget(self,"qt_central_widget"))

        self.frame10 = QFrame(self.centralWidget(),"frame10")
        self.frame10.setGeometry(QRect(0,0,408,410))
        self.frame10.setSizePolicy(QSizePolicy(4,4,4,5,self.frame10.sizePolicy().hasHeightForWidth()))
        self.frame10.setFrameShape(QFrame.NoFrame)
        self.frame10.setFrameShadow(QFrame.Plain)
        frame10Layout = QGridLayout(self.frame10,1,1,0,0,"frame10Layout")

        self.frame4 = QFrame(self.frame10,"frame4")
        self.frame4.setSizePolicy(QSizePolicy(7,5,0,0,self.frame4.sizePolicy().hasHeightForWidth()))
        self.frame4.setFrameShape(QFrame.NoFrame)
        self.frame4.setFrameShadow(QFrame.Raised)
        frame4Layout = QGridLayout(self.frame4,1,1,0,0,"frame4Layout")

        self.textLabel4 = QLabel(self.frame4,"textLabel4")
        textLabel4_font = QFont(self.textLabel4.font())
        textLabel4_font.setFamily("Sans Serif")
        textLabel4_font.setBold(1)
        self.textLabel4.setFont(textLabel4_font)
        self.textLabel4.setAlignment(QLabel.AlignVCenter | QLabel.AlignRight)

        frame4Layout.addWidget(self.textLabel4,0,0)

        self.statusLabel = QLabel(self.frame4,"statusLabel")
        self.statusLabel.setSizePolicy(QSizePolicy(7,5,0,0,self.statusLabel.sizePolicy().hasHeightForWidth()))
        self.statusLabel.setMinimumSize(QSize(250,0))
        self.statusLabel.setBackgroundMode(QLabel.PaletteBrightText)
        statusLabel_font = QFont(self.statusLabel.font())
        statusLabel_font.setFamily("Sans Serif")
        self.statusLabel.setFont(statusLabel_font)
        self.statusLabel.setAlignment(QLabel.AlignVCenter | QLabel.AlignLeft)

        frame4Layout.addWidget(self.statusLabel,0,1)

        self.pixmapLogo = QLabel(self.frame4,"pixmapLogo")
        self.pixmapLogo.setMinimumSize(QSize(50,30))
        self.pixmapLogo.setScaledContents(1)

        frame4Layout.addWidget(self.pixmapLogo,0,2)

        frame10Layout.addWidget(self.frame4,4,0)

        self.frame6 = QFrame(self.frame10,"frame6")
        self.frame6.setSizePolicy(QSizePolicy(7,5,0,0,self.frame6.sizePolicy().hasHeightForWidth()))
        self.frame6.setFrameShape(QFrame.NoFrame)
        self.frame6.setFrameShadow(QFrame.Raised)
        frame6Layout = QGridLayout(self.frame6,1,1,0,0,"frame6Layout")

        layout2 = QGridLayout(None,1,1,0,0,"layout2")

        self.clearButton = QPushButton(self.frame6,"clearButton")

        layout2.addWidget(self.clearButton,0,0)

        self.appVersion = QLabel(self.frame6,"appVersion")
        self.appVersion.setMinimumSize(QSize(200,0))
        appVersion_font = QFont(self.appVersion.font())
        appVersion_font.setFamily("Sans Serif")
        appVersion_font.setPointSize(14)
        appVersion_font.setBold(1)
        self.appVersion.setFont(appVersion_font)
        self.appVersion.setAlignment(QLabel.AlignVCenter | QLabel.AlignRight)

        layout2.addWidget(self.appVersion,0,2)

        self.muteCheck = QCheckBox(self.frame6,"muteCheck")

        layout2.addWidget(self.muteCheck,0,1)

        frame6Layout.addLayout(layout2,0,0)

        frame10Layout.addWidget(self.frame6,3,0)

        self.frame9 = QFrame(self.frame10,"frame9")
        self.frame9.setFrameShape(QFrame.StyledPanel)
        self.frame9.setFrameShadow(QFrame.Raised)
        frame9Layout = QHBoxLayout(self.frame9,11,6,"frame9Layout")

        self.frame8 = QFrame(self.frame9,"frame8")
        self.frame8.setFrameShape(QFrame.NoFrame)
        self.frame8.setFrameShadow(QFrame.Raised)
        frame8Layout = QGridLayout(self.frame8,1,1,0,0,"frame8Layout")

        self.textLabel1 = QLabel(self.frame8,"textLabel1")
        self.textLabel1.setSizePolicy(QSizePolicy(1,5,0,0,self.textLabel1.sizePolicy().hasHeightForWidth()))
        self.textLabel1.setAlignment(QLabel.AlignVCenter | QLabel.AlignRight)

        frame8Layout.addWidget(self.textLabel1,0,0)

        self.addressComboBox = QComboBox(0,self.frame8,"addressComboBox")
        self.addressComboBox.setSizePolicy(QSizePolicy(7,0,0,0,self.addressComboBox.sizePolicy().hasHeightForWidth()))
        self.addressComboBox.setMinimumSize(QSize(250,0))
        self.addressComboBox.setEditable(1)
        self.addressComboBox.setSizeLimit(20)
        self.addressComboBox.setInsertionPolicy(QComboBox.AtTop)
        self.addressComboBox.setAutoCompletion(1)
        self.addressComboBox.setDuplicatesEnabled(0)

        frame8Layout.addWidget(self.addressComboBox,0,1)

        self.frame7 = QFrame(self.frame8,"frame7")
        self.frame7.setFrameShape(QFrame.NoFrame)
        self.frame7.setFrameShadow(QFrame.Plain)
        frame7Layout = QGridLayout(self.frame7,1,1,0,6,"frame7Layout")

        self.pushButton17 = QPushButton(self.frame7,"pushButton17")

        frame7Layout.addWidget(self.pushButton17,0,2)

        self.callButton = QPushButton(self.frame7,"callButton")

        frame7Layout.addWidget(self.callButton,0,0)

        self.hangupButton = QPushButton(self.frame7,"hangupButton")
        self.hangupButton.setEnabled(0)

        frame7Layout.addWidget(self.hangupButton,0,1)

        frame8Layout.addMultiCellWidget(self.frame7,2,2,0,1)
        spacer1 = QSpacerItem(240,16,QSizePolicy.Expanding,QSizePolicy.Minimum)
        frame8Layout.addMultiCell(spacer1,1,1,0,1)
        frame9Layout.addWidget(self.frame8)

        self.dtmfFrame = QFrame(self.frame9,"dtmfFrame")
        self.dtmfFrame.setMinimumSize(QSize(75,95))
        self.dtmfFrame.setPaletteBackgroundColor(QColor(191,191,191))
        self.dtmfFrame.setFrameShape(QFrame.StyledPanel)
        self.dtmfFrame.setFrameShadow(QFrame.Raised)

        self.dtmfButton1 = QPushButton(self.dtmfFrame,"dtmfButton1")
        self.dtmfButton1.setGeometry(QRect(10,10,15,15))
        self.dtmfButton1.setMaximumSize(QSize(15,15))
        dtmfButton1_font = QFont(self.dtmfButton1.font())
        self.dtmfButton1.setFont(dtmfButton1_font)

        self.dtmfButton4 = QPushButton(self.dtmfFrame,"dtmfButton4")
        self.dtmfButton4.setGeometry(QRect(10,30,15,15))
        self.dtmfButton4.setMaximumSize(QSize(15,15))
        dtmfButton4_font = QFont(self.dtmfButton4.font())
        self.dtmfButton4.setFont(dtmfButton4_font)

        self.dtmfButton2 = QPushButton(self.dtmfFrame,"dtmfButton2")
        self.dtmfButton2.setGeometry(QRect(30,10,15,15))
        dtmfButton2_font = QFont(self.dtmfButton2.font())
        self.dtmfButton2.setFont(dtmfButton2_font)

        self.dtmfButton7 = QPushButton(self.dtmfFrame,"dtmfButton7")
        self.dtmfButton7.setGeometry(QRect(10,50,15,15))
        dtmfButton7_font = QFont(self.dtmfButton7.font())
        self.dtmfButton7.setFont(dtmfButton7_font)

        self.dtmfButtonStar = QPushButton(self.dtmfFrame,"dtmfButtonStar")
        self.dtmfButtonStar.setGeometry(QRect(10,70,15,15))
        dtmfButtonStar_font = QFont(self.dtmfButtonStar.font())
        self.dtmfButtonStar.setFont(dtmfButtonStar_font)

        self.dtmfButton0 = QPushButton(self.dtmfFrame,"dtmfButton0")
        self.dtmfButton0.setGeometry(QRect(30,70,15,15))
        dtmfButton0_font = QFont(self.dtmfButton0.font())
        self.dtmfButton0.setFont(dtmfButton0_font)

        self.dtmfButton8 = QPushButton(self.dtmfFrame,"dtmfButton8")
        self.dtmfButton8.setGeometry(QRect(30,50,15,15))
        dtmfButton8_font = QFont(self.dtmfButton8.font())
        self.dtmfButton8.setFont(dtmfButton8_font)

        self.dtmfButton5 = QPushButton(self.dtmfFrame,"dtmfButton5")
        self.dtmfButton5.setGeometry(QRect(30,30,16,16))
        dtmfButton5_font = QFont(self.dtmfButton5.font())
        self.dtmfButton5.setFont(dtmfButton5_font)

        self.dtmfButton9 = QPushButton(self.dtmfFrame,"dtmfButton9")
        self.dtmfButton9.setGeometry(QRect(50,50,15,15))
        dtmfButton9_font = QFont(self.dtmfButton9.font())
        self.dtmfButton9.setFont(dtmfButton9_font)

        self.dtmfButtonHash = QPushButton(self.dtmfFrame,"dtmfButtonHash")
        self.dtmfButtonHash.setGeometry(QRect(50,70,15,15))
        dtmfButtonHash_font = QFont(self.dtmfButtonHash.font())
        self.dtmfButtonHash.setFont(dtmfButtonHash_font)

        self.dtmfButton3 = QPushButton(self.dtmfFrame,"dtmfButton3")
        self.dtmfButton3.setGeometry(QRect(50,10,15,15))
        dtmfButton3_font = QFont(self.dtmfButton3.font())
        self.dtmfButton3.setFont(dtmfButton3_font)

        self.dtmfButton6 = QPushButton(self.dtmfFrame,"dtmfButton6")
        self.dtmfButton6.setGeometry(QRect(50,30,15,15))
        dtmfButton6_font = QFont(self.dtmfButton6.font())
        self.dtmfButton6.setFont(dtmfButton6_font)
        frame9Layout.addWidget(self.dtmfFrame)

        frame10Layout.addWidget(self.frame9,1,0)

        self.callSelectionTab = QTabWidget(self.frame10,"callSelectionTab")
        self.callSelectionTab.setMinimumSize(QSize(0,25))
        self.callSelectionTab.setMaximumSize(QSize(32767,25))
        self.callSelectionTab.setTabShape(QTabWidget.Rounded)

        self.tab1 = QWidget(self.callSelectionTab,"tab1")
        self.callSelectionTab.insertTab(self.tab1,QString(""))

        frame10Layout.addWidget(self.callSelectionTab,0,0)

        self.debuggingTextEdit = QTextEdit(self.frame10,"debuggingTextEdit")
        self.debuggingTextEdit.setSizePolicy(QSizePolicy(7,7,100,100,self.debuggingTextEdit.sizePolicy().hasHeightForWidth()))
        debuggingTextEdit_font = QFont(self.debuggingTextEdit.font())
        debuggingTextEdit_font.setFamily("Courier")
        self.debuggingTextEdit.setFont(debuggingTextEdit_font)
        self.debuggingTextEdit.setTextFormat(QTextEdit.PlainText)
        self.debuggingTextEdit.setWrapPolicy(QTextEdit.Anywhere)
        self.debuggingTextEdit.setUndoDepth(0)
        self.debuggingTextEdit.setReadOnly(1)
        self.debuggingTextEdit.setUndoRedoEnabled(0)

        frame10Layout.addWidget(self.debuggingTextEdit,2,0)

        self.fileNewAction = QAction(self,"fileNewAction")
        self.fileNewAction.setIconSet(QIconSet())
        self.fileOpenAction = QAction(self,"fileOpenAction")
        self.fileOpenAction.setIconSet(QIconSet())
        self.fileSaveAction = QAction(self,"fileSaveAction")
        self.fileSaveAction.setIconSet(QIconSet())
        self.fileSaveAsAction = QAction(self,"fileSaveAsAction")
        self.filePrefsAction = QAction(self,"filePrefsAction")
        self.filePrefsAction.setIconSet(QIconSet())
        self.fileExitAction = QAction(self,"fileExitAction")
        self.helpContentsAction = QAction(self,"helpContentsAction")
        self.helpIndexAction = QAction(self,"helpIndexAction")
        self.helpAboutAction = QAction(self,"helpAboutAction")




        self.menubar = QMenuBar(self,"menubar")


        self.fileMenu = QPopupMenu(self)
        self.fileNewAction.addTo(self.fileMenu)
        self.fileOpenAction.addTo(self.fileMenu)
        self.fileSaveAction.addTo(self.fileMenu)
        self.fileSaveAsAction.addTo(self.fileMenu)
        self.fileMenu.insertSeparator()
        self.filePrefsAction.addTo(self.fileMenu)
        self.fileMenu.insertSeparator()
        self.fileExitAction.addTo(self.fileMenu)
        self.menubar.insertItem(QString(""),self.fileMenu,1)

        self.helpMenu = QPopupMenu(self)
        self.helpContentsAction.addTo(self.helpMenu)
        self.helpIndexAction.addTo(self.helpMenu)
        self.helpMenu.insertSeparator()
        self.helpAboutAction.addTo(self.helpMenu)
        self.menubar.insertItem(QString(""),self.helpMenu,2)


        self.languageChange()

        self.resize(QSize(408,453).expandedTo(self.minimumSizeHint()))
        self.clearWState(Qt.WState_Polished)

        self.connect(self.fileNewAction,SIGNAL("activated()"),self.fileNew)
        self.connect(self.fileOpenAction,SIGNAL("activated()"),self.fileOpen)
        self.connect(self.fileSaveAction,SIGNAL("activated()"),self.fileSave)
        self.connect(self.fileSaveAsAction,SIGNAL("activated()"),self.fileSaveAs)
        self.connect(self.filePrefsAction,SIGNAL("activated()"),self.filePrefs)
        self.connect(self.fileExitAction,SIGNAL("activated()"),self.fileExit)
        self.connect(self.helpIndexAction,SIGNAL("activated()"),self.helpIndex)
        self.connect(self.helpContentsAction,SIGNAL("activated()"),self.helpContents)
        self.connect(self.helpAboutAction,SIGNAL("activated()"),self.helpAbout)
        self.connect(self.callButton,SIGNAL("clicked()"),self.callButton_clicked)
        self.connect(self.hangupButton,SIGNAL("clicked()"),self.hangupButton_clicked)
        self.connect(self.dtmfButton2,SIGNAL("pressed()"),self.dtmfButton2_pressed)
        self.connect(self.dtmfButton2,SIGNAL("released()"),self.dtmfButton2_released)
        self.connect(self.dtmfButton3,SIGNAL("pressed()"),self.dtmfButton3_pressed)
        self.connect(self.dtmfButton3,SIGNAL("released()"),self.dtmfButton3_released)
        self.connect(self.dtmfButton4,SIGNAL("pressed()"),self.dtmfButton4_pressed)
        self.connect(self.dtmfButton4,SIGNAL("released()"),self.dtmfButton4_released)
        self.connect(self.dtmfButton5,SIGNAL("pressed()"),self.dtmfButton5_pressed)
        self.connect(self.dtmfButton5,SIGNAL("released()"),self.dtmfButton5_released)
        self.connect(self.dtmfButton6,SIGNAL("pressed()"),self.dtmfButton6_pressed)
        self.connect(self.dtmfButton6,SIGNAL("released()"),self.dtmfButton6_released)
        self.connect(self.dtmfButton7,SIGNAL("pressed()"),self.dtmfButton7_pressed)
        self.connect(self.dtmfButton7,SIGNAL("released()"),self.dtmfButton7_released)
        self.connect(self.dtmfButton8,SIGNAL("pressed()"),self.dtmfButton8_pressed)
        self.connect(self.dtmfButton8,SIGNAL("released()"),self.dtmfButton8_released)
        self.connect(self.dtmfButton9,SIGNAL("pressed()"),self.dtmfButton9_pressed)
        self.connect(self.dtmfButton9,SIGNAL("released()"),self.dtmfButton9_released)
        self.connect(self.dtmfButton0,SIGNAL("pressed()"),self.dtmfButton0_pressed)
        self.connect(self.dtmfButton0,SIGNAL("released()"),self.dtmfButton0_released)
        self.connect(self.dtmfButtonHash,SIGNAL("pressed()"),self.dtmfButtonHash_pressed)
        self.connect(self.dtmfButtonHash,SIGNAL("released()"),self.dtmfButtonHash_released)
        self.connect(self.dtmfButtonStar,SIGNAL("pressed()"),self.dtmfButtonStar_pressed)
        self.connect(self.dtmfButtonStar,SIGNAL("released()"),self.dtmfButtonStar_released)
        self.connect(self.pushButton17,SIGNAL("clicked()"),self.register_clicked)
        self.connect(self.callSelectionTab,SIGNAL("currentChanged(QWidget*)"),self.callSelectionTab_currentChanged)


    def languageChange(self):
        self.setCaption(self.__tr("Shtoom - Qt UI"))
        self.textLabel4.setText(self.__tr("Status"))
        self.statusLabel.setText(QString.null)
        self.clearButton.setText(self.__tr("Clear"))
        self.appVersion.setText(self.__tr("Shtoom"))
        self.muteCheck.setText(self.__tr("mute"))
        self.textLabel1.setText(self.__tr("Call: "))
        self.pushButton17.setText(self.__tr("Register"))
        self.callButton.setText(self.__tr("Call"))
        self.callButton.setAccel(self.__tr("Return"))
        self.hangupButton.setText(self.__tr("Hang Up"))
        self.dtmfButton1.setText(self.__tr("1"))
        self.dtmfButton4.setText(self.__tr("4"))
        self.dtmfButton2.setText(self.__tr("2"))
        self.dtmfButton7.setText(self.__tr("7"))
        self.dtmfButtonStar.setText(self.__tr("*"))
        self.dtmfButton0.setText(self.__tr("0"))
        self.dtmfButton8.setText(self.__tr("8"))
        self.dtmfButton5.setText(self.__tr("5"))
        self.dtmfButton9.setText(self.__tr("9"))
        self.dtmfButtonHash.setText(self.__tr("#"))
        self.dtmfButton3.setText(self.__tr("3"))
        self.dtmfButton6.setText(self.__tr("6"))
        self.callSelectionTab.changeTab(self.tab1,self.__tr("New Call"))
        QToolTip.add(self.debuggingTextEdit,self.__tr("Debugging Messages"))
        self.fileNewAction.setText(self.__tr("New"))
        self.fileNewAction.setMenuText(self.__tr("&New"))
        self.fileNewAction.setAccel(self.__tr("Ctrl+N"))
        self.fileOpenAction.setText(self.__tr("Open"))
        self.fileOpenAction.setMenuText(self.__tr("&Open..."))
        self.fileOpenAction.setAccel(self.__tr("Ctrl+O"))
        self.fileSaveAction.setText(self.__tr("Save"))
        self.fileSaveAction.setMenuText(self.__tr("&Save"))
        self.fileSaveAction.setAccel(self.__tr("Ctrl+S"))
        self.fileSaveAsAction.setText(self.__tr("Save As"))
        self.fileSaveAsAction.setMenuText(self.__tr("Save &As..."))
        self.fileSaveAsAction.setAccel(QString.null)
        self.filePrefsAction.setText(self.__tr("Preferences"))
        self.filePrefsAction.setMenuText(self.__tr("&Preferences..."))
        self.filePrefsAction.setAccel(self.__tr("Ctrl+P"))
        self.fileExitAction.setText(QString.null)
        self.fileExitAction.setMenuText(self.__tr("E&xit"))
        self.fileExitAction.setAccel(QString.null)
        self.helpContentsAction.setText(self.__tr("Contents"))
        self.helpContentsAction.setMenuText(self.__tr("&Contents..."))
        self.helpContentsAction.setAccel(QString.null)
        self.helpIndexAction.setText(self.__tr("Index"))
        self.helpIndexAction.setMenuText(self.__tr("&Index..."))
        self.helpIndexAction.setAccel(QString.null)
        self.helpAboutAction.setText(self.__tr("About"))
        self.helpAboutAction.setMenuText(self.__tr("&About"))
        self.helpAboutAction.setAccel(QString.null)
        if self.menubar.findItem(1):
            self.menubar.findItem(1).setText(self.__tr("&File"))
        if self.menubar.findItem(2):
            self.menubar.findItem(2).setText(self.__tr("&Help"))


    def fileNew(self):
        print "ShtoomMainWindow.fileNew(): Not implemented yet"

    def fileOpen(self):
        print "ShtoomMainWindow.fileOpen(): Not implemented yet"

    def fileSave(self):
        print "ShtoomMainWindow.fileSave(): Not implemented yet"

    def fileSaveAs(self):
        print "ShtoomMainWindow.fileSaveAs(): Not implemented yet"

    def filePrefs(self):
        print "ShtoomMainWindow.filePrefs(): Not implemented yet"

    def fileExit(self):
        print "ShtoomMainWindow.fileExit(): Not implemented yet"

    def helpIndex(self):
        print "ShtoomMainWindow.helpIndex(): Not implemented yet"

    def helpContents(self):
        print "ShtoomMainWindow.helpContents(): Not implemented yet"

    def helpAbout(self):
        print "ShtoomMainWindow.helpAbout(): Not implemented yet"

    def lookupAddressButton_clicked(self):
        print "ShtoomMainWindow.lookupAddressButton_clicked(): Not implemented yet"

    def dtmfButtonHash_clicked(self):
        print "ShtoomMainWindow.dtmfButtonHash_clicked(): Not implemented yet"

    def dtmfButtonHash_pressed(self):
        print "ShtoomMainWindow.dtmfButtonHash_pressed(): Not implemented yet"

    def dtmfButtonHash_released(self):
        print "ShtoomMainWindow.dtmfButtonHash_released(): Not implemented yet"

    def dtmfButton0_released(self):
        print "ShtoomMainWindow.dtmfButton0_released(): Not implemented yet"

    def dtmfButton0_pressed(self):
        print "ShtoomMainWindow.dtmfButton0_pressed(): Not implemented yet"

    def dtmfButtonStar_pressed(self):
        print "ShtoomMainWindow.dtmfButtonStar_pressed(): Not implemented yet"

    def dtmfButtonStar_released(self):
        print "ShtoomMainWindow.dtmfButtonStar_released(): Not implemented yet"

    def dtmfButton9_pressed(self):
        print "ShtoomMainWindow.dtmfButton9_pressed(): Not implemented yet"

    def dtmfButton9_released(self):
        print "ShtoomMainWindow.dtmfButton9_released(): Not implemented yet"

    def dtmfButton8_pressed(self):
        print "ShtoomMainWindow.dtmfButton8_pressed(): Not implemented yet"

    def dtmfButton8_released(self):
        print "ShtoomMainWindow.dtmfButton8_released(): Not implemented yet"

    def dtmfButton7_pressed(self):
        print "ShtoomMainWindow.dtmfButton7_pressed(): Not implemented yet"

    def dtmfButton7_released(self):
        print "ShtoomMainWindow.dtmfButton7_released(): Not implemented yet"

    def dtmfButton6_pressed(self):
        print "ShtoomMainWindow.dtmfButton6_pressed(): Not implemented yet"

    def dtmfButton6_released(self):
        print "ShtoomMainWindow.dtmfButton6_released(): Not implemented yet"

    def dtmfButton5_pressed(self):
        print "ShtoomMainWindow.dtmfButton5_pressed(): Not implemented yet"

    def dtmfButton5_released(self):
        print "ShtoomMainWindow.dtmfButton5_released(): Not implemented yet"

    def dtmfButton4_pressed(self):
        print "ShtoomMainWindow.dtmfButton4_pressed(): Not implemented yet"

    def dtmfButton4_released(self):
        print "ShtoomMainWindow.dtmfButton4_released(): Not implemented yet"

    def dtmfButton3_pressed(self):
        print "ShtoomMainWindow.dtmfButton3_pressed(): Not implemented yet"

    def dtmfButton3_released(self):
        print "ShtoomMainWindow.dtmfButton3_released(): Not implemented yet"

    def dtmfButton2_pressed(self):
        print "ShtoomMainWindow.dtmfButton2_pressed(): Not implemented yet"

    def dtmfButton2_released(self):
        print "ShtoomMainWindow.dtmfButton2_released(): Not implemented yet"

    def callButton_clicked(self):
        print "ShtoomMainWindow.callButton_clicked(): Not implemented yet"

    def hangupButton_clicked(self):
        print "ShtoomMainWindow.hangupButton_clicked(): Not implemented yet"

    def clearButton_clicked(self):
        print "ShtoomMainWindow.clearButton_clicked(): Not implemented yet"

    def register_clicked(self):
        print "ShtoomMainWindow.register_clicked(): Not implemented yet"

    def muteCheck_stateChanged(self,a0):
        print "ShtoomMainWindow.muteCheck_stateChanged(int): Not implemented yet"

    def callSelectionTab_currentChanged(self,a0):
        print "ShtoomMainWindow.callSelectionTab_currentChanged(QWidget*): Not implemented yet"

    def __tr(self,s,c = None):
        return qApp.translate("ShtoomMainWindow",s,c)
