# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'shtoommainwindow.ui'
#
# Created: Sat Feb 21 14:53:01 2004
#      by: The PyQt User Interface Compiler (pyuic) 3.10
#
# WARNING! All changes made in this file will be lost!


from qt import *

class ShtoomMainWindow(QMainWindow):
    def __init__(self,parent = None,name = None,fl = 0):
        QMainWindow.__init__(self,parent,name,fl)
        self.statusBar()

        if not name:
            self.setProperty("name",QVariant("ShtoomMainWindow"))


        self.setCentralWidget(QWidget(self,"qt_central_widget"))

        self.textLabel1 = QLabel(self.centralWidget(),"textLabel1")
        self.textLabel1.setProperty("geometry",QVariant(QRect(10,20,40,30)))

        self.textLabel4 = QLabel(self.centralWidget(),"textLabel4")
        self.textLabel4.setProperty("geometry",QVariant(QRect(10,138,50,30)))

        self.lookupAddressButton = QPushButton(self.centralWidget(),"lookupAddressButton")
        self.lookupAddressButton.setProperty("geometry",QVariant(QRect(370,20,31,31)))

        self.callButton = QPushButton(self.centralWidget(),"callButton")
        self.callButton.setProperty("geometry",QVariant(QRect(50,60,80,30)))

        self.hangupButton = QPushButton(self.centralWidget(),"hangupButton")
        self.hangupButton.setProperty("enabled",QVariant(QVariant(0,0)))
        self.hangupButton.setProperty("geometry",QVariant(QRect(140,60,80,30)))

        self.statusLabel = QLabel(self.centralWidget(),"statusLabel")
        self.statusLabel.setProperty("geometry",QVariant(QRect(60,140,180,31)))

        self.debuggingTextEdit = QTextEdit(self.centralWidget(),"debuggingTextEdit")
        self.debuggingTextEdit.setProperty("geometry",QVariant(QRect(0,270,490,120)))
        self.debuggingTextEdit.setProperty("sizePolicy",QVariant(QSizePolicy(7,7,0,0,self.debuggingTextEdit.sizePolicy().hasHeightForWidth())))
        debuggingTextEdit_font = QFont(self.debuggingTextEdit.font())
        debuggingTextEdit_font.setFamily("Courier")
        self.debuggingTextEdit.setFont(debuggingTextEdit_font)
        self.debuggingTextEdit.setProperty("textFormat",QVariant(QTextEdit.PlainText))
        self.debuggingTextEdit.setProperty("wrapPolicy",QVariant(QTextEdit.Anywhere))
        self.debuggingTextEdit.setProperty("undoDepth",QVariant(0))
        self.debuggingTextEdit.setProperty("readOnly",QVariant(QVariant(1,0)))
        self.debuggingTextEdit.setProperty("undoRedoEnabled",QVariant(QVariant(0,0)))

        self.addressComboBox = QComboBox(0,self.centralWidget(),"addressComboBox")
        self.addressComboBox.setProperty("geometry",QVariant(QRect(50,20,311,31)))
        self.addressComboBox.setProperty("editable",QVariant(QVariant(1,0)))
        self.addressComboBox.setProperty("sizeLimit",QVariant(20))
        self.addressComboBox.setProperty("insertionPolicy",QVariant(QComboBox.AtTop))
        self.addressComboBox.setProperty("autoCompletion",QVariant(QVariant(1,0)))
        self.addressComboBox.setProperty("duplicatesEnabled",QVariant(QVariant(0,0)))

        self.clearButton = QPushButton(self.centralWidget(),"clearButton")
        self.clearButton.setProperty("geometry",QVariant(QRect(10,400,71,31)))

        LayoutWidget = QWidget(self.centralWidget(),"layout6")
        LayoutWidget.setProperty("geometry",QVariant(QRect(11,191,246,28)))
        layout6 = QHBoxLayout(LayoutWidget,11,6,"layout6")

        self.textLabel2 = QLabel(LayoutWidget,"textLabel2")
        textLabel2_font = QFont(self.textLabel2.font())
        self.textLabel2.setFont(textLabel2_font)
        layout6.addWidget(self.textLabel2)

        self.sentPacketsLineEdit = QLineEdit(LayoutWidget,"sentPacketsLineEdit")
        sentPacketsLineEdit_font = QFont(self.sentPacketsLineEdit.font())
        sentPacketsLineEdit_font.setFamily("Courier")
        self.sentPacketsLineEdit.setFont(sentPacketsLineEdit_font)
        layout6.addWidget(self.sentPacketsLineEdit)

        LayoutWidget_2 = QWidget(self.centralWidget(),"layout6_2")
        LayoutWidget_2.setProperty("geometry",QVariant(QRect(10,220,246,28)))
        layout6_2 = QHBoxLayout(LayoutWidget_2,11,6,"layout6_2")

        self.textLabel2_r = QLabel(LayoutWidget_2,"textLabel2_r")
        textLabel2_r_font = QFont(self.textLabel2_r.font())
        self.textLabel2_r.setFont(textLabel2_r_font)
        layout6_2.addWidget(self.textLabel2_r)

        self.rcvdPacketsLineEdit = QLineEdit(LayoutWidget_2,"rcvdPacketsLineEdit")
        rcvdPacketsLineEdit_font = QFont(self.rcvdPacketsLineEdit.font())
        rcvdPacketsLineEdit_font.setFamily("Courier")
        self.rcvdPacketsLineEdit.setFont(rcvdPacketsLineEdit_font)
        layout6_2.addWidget(self.rcvdPacketsLineEdit)

        self.frame3 = QFrame(self.centralWidget(),"frame3")
        self.frame3.setProperty("geometry",QVariant(QRect(330,100,80,100)))
        self.frame3.setProperty("paletteBackgroundColor",QVariant(QColor(230,230,230)))
        self.frame3.setProperty("frameShape",QVariant(QFrame.StyledPanel))
        self.frame3.setProperty("frameShadow",QVariant(QFrame.Raised))

        self.dtmfButton1 = QPushButton(self.frame3,"dtmfButton1")
        self.dtmfButton1.setProperty("geometry",QVariant(QRect(10,10,15,15)))
        self.dtmfButton1.setProperty("maximumSize",QVariant(QSize(15,15)))
        dtmfButton1_font = QFont(self.dtmfButton1.font())
        self.dtmfButton1.setFont(dtmfButton1_font)

        self.dtmfButton4 = QPushButton(self.frame3,"dtmfButton4")
        self.dtmfButton4.setProperty("geometry",QVariant(QRect(10,30,15,15)))
        self.dtmfButton4.setProperty("maximumSize",QVariant(QSize(15,15)))
        dtmfButton4_font = QFont(self.dtmfButton4.font())
        self.dtmfButton4.setFont(dtmfButton4_font)

        self.dtmfButton2 = QPushButton(self.frame3,"dtmfButton2")
        self.dtmfButton2.setProperty("geometry",QVariant(QRect(30,10,15,15)))
        dtmfButton2_font = QFont(self.dtmfButton2.font())
        self.dtmfButton2.setFont(dtmfButton2_font)

        self.dtmfButton3 = QPushButton(self.frame3,"dtmfButton3")
        self.dtmfButton3.setProperty("geometry",QVariant(QRect(50,10,15,15)))
        dtmfButton3_font = QFont(self.dtmfButton3.font())
        self.dtmfButton3.setFont(dtmfButton3_font)

        self.dtmfButton5 = QPushButton(self.frame3,"dtmfButton5")
        self.dtmfButton5.setProperty("geometry",QVariant(QRect(30,30,15,15)))
        dtmfButton5_font = QFont(self.dtmfButton5.font())
        self.dtmfButton5.setFont(dtmfButton5_font)

        self.dtmfButton6 = QPushButton(self.frame3,"dtmfButton6")
        self.dtmfButton6.setProperty("geometry",QVariant(QRect(50,30,15,15)))
        dtmfButton6_font = QFont(self.dtmfButton6.font())
        self.dtmfButton6.setFont(dtmfButton6_font)

        self.dtmfButton7 = QPushButton(self.frame3,"dtmfButton7")
        self.dtmfButton7.setProperty("geometry",QVariant(QRect(10,50,15,15)))
        dtmfButton7_font = QFont(self.dtmfButton7.font())
        self.dtmfButton7.setFont(dtmfButton7_font)

        self.dtmfButton8 = QPushButton(self.frame3,"dtmfButton8")
        self.dtmfButton8.setProperty("geometry",QVariant(QRect(30,50,15,15)))
        dtmfButton8_font = QFont(self.dtmfButton8.font())
        self.dtmfButton8.setFont(dtmfButton8_font)

        self.dtmfButton9 = QPushButton(self.frame3,"dtmfButton9")
        self.dtmfButton9.setProperty("geometry",QVariant(QRect(50,50,15,15)))
        dtmfButton9_font = QFont(self.dtmfButton9.font())
        self.dtmfButton9.setFont(dtmfButton9_font)

        self.dtmfButtonStar = QPushButton(self.frame3,"dtmfButtonStar")
        self.dtmfButtonStar.setProperty("geometry",QVariant(QRect(10,70,15,15)))
        dtmfButtonStar_font = QFont(self.dtmfButtonStar.font())
        self.dtmfButtonStar.setFont(dtmfButtonStar_font)

        self.dtmfButton0 = QPushButton(self.frame3,"dtmfButton0")
        self.dtmfButton0.setProperty("geometry",QVariant(QRect(30,70,15,15)))
        dtmfButton0_font = QFont(self.dtmfButton0.font())
        self.dtmfButton0.setFont(dtmfButton0_font)

        self.dtmfButtonHash = QPushButton(self.frame3,"dtmfButtonHash")
        self.dtmfButtonHash.setProperty("geometry",QVariant(QRect(50,70,15,15)))
        dtmfButtonHash_font = QFont(self.dtmfButtonHash.font())
        self.dtmfButtonHash.setFont(dtmfButtonHash_font)

        self.pixmapLogo = QLabel(self.centralWidget(),"pixmapLogo")
        self.pixmapLogo.setProperty("geometry",QVariant(QRect(420,16,50,30)))
        self.pixmapLogo.setProperty("scaledContents",QVariant(QVariant(1,0)))

        self.fileNewAction = QAction(self,"fileNewAction")
        self.fileNewAction.setProperty("iconSet",QVariant(QIconSet()))
        self.fileOpenAction = QAction(self,"fileOpenAction")
        self.fileOpenAction.setProperty("iconSet",QVariant(QIconSet()))
        self.fileSaveAction = QAction(self,"fileSaveAction")
        self.fileSaveAction.setProperty("iconSet",QVariant(QIconSet()))
        self.fileSaveAsAction = QAction(self,"fileSaveAsAction")
        self.filePrefsAction = QAction(self,"filePrefsAction")
        self.filePrefsAction.setProperty("iconSet",QVariant(QIconSet()))
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

        self.resize(QSize(493,499).expandedTo(self.minimumSizeHint()))
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
        self.connect(self.lookupAddressButton,SIGNAL("clicked()"),self.lookupAddressButton_clicked)
        self.connect(self.callButton,SIGNAL("clicked()"),self.callButton_clicked)
        self.connect(self.hangupButton,SIGNAL("clicked()"),self.hangupButton_clicked)
        self.connect(self.clearButton,SIGNAL("clicked()"),self.clearButton_clicked)
        self.connect(self.dtmfButton1,SIGNAL("pressed()"),self.dtmfButton1_pressed)
        self.connect(self.dtmfButton1,SIGNAL("released()"),self.dtmfButton1_released)
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


    def languageChange(self):
        self.setProperty("caption",QVariant(self.__tr("Shtoom - Qt UI")))
        self.textLabel1.setProperty("text",QVariant(self.__tr("Call:")))
        self.textLabel4.setProperty("text",QVariant(self.__tr("Status")))
        self.lookupAddressButton.setProperty("text",QVariant(QString.null))
        self.callButton.setProperty("text",QVariant(self.__tr("Call")))
        self.hangupButton.setProperty("text",QVariant(self.__tr("Hang Up")))
        self.statusLabel.setProperty("text",QVariant(QString.null))
        QToolTip.add(self.debuggingTextEdit,self.__tr("Debugging Messages"))
        self.clearButton.setProperty("text",QVariant(self.__tr("Clear")))
        self.textLabel2.setProperty("text",QVariant(self.__tr("Sent Pkts")))
        self.textLabel2_r.setProperty("text",QVariant(self.__tr("Rcvd Pkts")))
        self.dtmfButton1.setProperty("text",QVariant(self.__tr("1")))
        self.dtmfButton4.setProperty("text",QVariant(self.__tr("4")))
        self.dtmfButton2.setProperty("text",QVariant(self.__tr("2")))
        self.dtmfButton3.setProperty("text",QVariant(self.__tr("3")))
        self.dtmfButton5.setProperty("text",QVariant(self.__tr("5")))
        self.dtmfButton6.setProperty("text",QVariant(self.__tr("6")))
        self.dtmfButton7.setProperty("text",QVariant(self.__tr("7")))
        self.dtmfButton8.setProperty("text",QVariant(self.__tr("8")))
        self.dtmfButton9.setProperty("text",QVariant(self.__tr("9")))
        self.dtmfButtonStar.setProperty("text",QVariant(self.__tr("*")))
        self.dtmfButton0.setProperty("text",QVariant(self.__tr("0")))
        self.dtmfButtonHash.setProperty("text",QVariant(self.__tr("#")))
        self.fileNewAction.setProperty("text",QVariant(self.__tr("New")))
        self.fileNewAction.setProperty("menuText",QVariant(self.__tr("&New")))
        self.fileNewAction.setProperty("accel",QVariant(self.__tr("Ctrl+N")))
        self.fileOpenAction.setProperty("text",QVariant(self.__tr("Open")))
        self.fileOpenAction.setProperty("menuText",QVariant(self.__tr("&Open...")))
        self.fileOpenAction.setProperty("accel",QVariant(self.__tr("Ctrl+O")))
        self.fileSaveAction.setProperty("text",QVariant(self.__tr("Save")))
        self.fileSaveAction.setProperty("menuText",QVariant(self.__tr("&Save")))
        self.fileSaveAction.setProperty("accel",QVariant(self.__tr("Ctrl+S")))
        self.fileSaveAsAction.setProperty("text",QVariant(self.__tr("Save As")))
        self.fileSaveAsAction.setProperty("menuText",QVariant(self.__tr("Save &As...")))
        self.fileSaveAsAction.setProperty("accel",QVariant(QString.null))
        self.filePrefsAction.setProperty("text",QVariant(self.__tr("Preferences")))
        self.filePrefsAction.setProperty("menuText",QVariant(self.__tr("&Preferences...")))
        self.filePrefsAction.setProperty("accel",QVariant(self.__tr("Ctrl+P")))
        self.fileExitAction.setProperty("text",QVariant(QString.null))
        self.fileExitAction.setProperty("menuText",QVariant(self.__tr("E&xit")))
        self.fileExitAction.setProperty("accel",QVariant(QString.null))
        self.helpContentsAction.setProperty("text",QVariant(self.__tr("Contents")))
        self.helpContentsAction.setProperty("menuText",QVariant(self.__tr("&Contents...")))
        self.helpContentsAction.setProperty("accel",QVariant(QString.null))
        self.helpIndexAction.setProperty("text",QVariant(self.__tr("Index")))
        self.helpIndexAction.setProperty("menuText",QVariant(self.__tr("&Index...")))
        self.helpIndexAction.setProperty("accel",QVariant(QString.null))
        self.helpAboutAction.setProperty("text",QVariant(self.__tr("About")))
        self.helpAboutAction.setProperty("menuText",QVariant(self.__tr("&About")))
        self.helpAboutAction.setProperty("accel",QVariant(QString.null))
        self.menubar.findItem(1).setText(self.__tr("&File"))
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

    def dtmfButton1_pressed(self):
        print "ShtoomMainWindow.dtmfButton1_pressed(): Not implemented yet"

    def dtmfButton1_released(self):
        print "ShtoomMainWindow.dtmfButton1_released(): Not implemented yet"

    def callButton_clicked(self):
        print "ShtoomMainWindow.callButton_clicked(): Not implemented yet"

    def hangupButton_clicked(self):
        print "ShtoomMainWindow.hangupButton_clicked(): Not implemented yet"

    def clearButton_clicked(self):
        print "ShtoomMainWindow.clearButton_clicked(): Not implemented yet"

    def __tr(self,s,c = None):
        return qApp.translate("ShtoomMainWindow",s,c)
