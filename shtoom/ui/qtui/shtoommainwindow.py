# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'shtoommainwindow.ui'
#
# Created: Fri Nov 14 20:03:43 2003
#      by: The PyQt User Interface Compiler (pyuic) 3.8.1
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

        self.textLabel1 = QLabel(self.centralWidget(),"textLabel1")
        self.textLabel1.setGeometry(QRect(10,20,40,30))

        self.frame3 = QFrame(self.centralWidget(),"frame3")
        self.frame3.setGeometry(QRect(380,120,99,138))
        self.frame3.setPaletteBackgroundColor(QColor(230,230,230))
        self.frame3.setFrameShape(QFrame.StyledPanel)
        self.frame3.setFrameShadow(QFrame.Raised)
        frame3Layout = QHBoxLayout(self.frame3,11,6,"frame3Layout")

        layout1 = QGridLayout(None,1,1,0,6,"layout1")

        self.dtmfButton9 = QPushButton(self.frame3,"dtmfButton9")
        dtmfButton9_font = QFont(self.dtmfButton9.font())
        dtmfButton9_font.setPointSize(10)
        self.dtmfButton9.setFont(dtmfButton9_font)

        layout1.addWidget(self.dtmfButton9,2,2)

        self.dtmfButton0 = QPushButton(self.frame3,"dtmfButton0")
        dtmfButton0_font = QFont(self.dtmfButton0.font())
        dtmfButton0_font.setPointSize(10)
        self.dtmfButton0.setFont(dtmfButton0_font)

        layout1.addWidget(self.dtmfButton0,3,1)

        self.dtmfButton1 = QPushButton(self.frame3,"dtmfButton1")
        dtmfButton1_font = QFont(self.dtmfButton1.font())
        dtmfButton1_font.setPointSize(10)
        self.dtmfButton1.setFont(dtmfButton1_font)

        layout1.addWidget(self.dtmfButton1,0,0)

        self.dtmfButtonStar = QPushButton(self.frame3,"dtmfButtonStar")
        dtmfButtonStar_font = QFont(self.dtmfButtonStar.font())
        dtmfButtonStar_font.setPointSize(10)
        self.dtmfButtonStar.setFont(dtmfButtonStar_font)

        layout1.addWidget(self.dtmfButtonStar,3,0)

        self.dtmfButton5 = QPushButton(self.frame3,"dtmfButton5")
        dtmfButton5_font = QFont(self.dtmfButton5.font())
        dtmfButton5_font.setPointSize(10)
        self.dtmfButton5.setFont(dtmfButton5_font)

        layout1.addWidget(self.dtmfButton5,1,1)

        self.dtmfButton7 = QPushButton(self.frame3,"dtmfButton7")
        dtmfButton7_font = QFont(self.dtmfButton7.font())
        dtmfButton7_font.setPointSize(10)
        self.dtmfButton7.setFont(dtmfButton7_font)

        layout1.addWidget(self.dtmfButton7,2,0)

        self.dtmfButton6 = QPushButton(self.frame3,"dtmfButton6")
        dtmfButton6_font = QFont(self.dtmfButton6.font())
        dtmfButton6_font.setPointSize(10)
        self.dtmfButton6.setFont(dtmfButton6_font)

        layout1.addWidget(self.dtmfButton6,1,2)

        self.dtmfButton8 = QPushButton(self.frame3,"dtmfButton8")
        dtmfButton8_font = QFont(self.dtmfButton8.font())
        dtmfButton8_font.setPointSize(10)
        self.dtmfButton8.setFont(dtmfButton8_font)

        layout1.addWidget(self.dtmfButton8,2,1)

        self.dtmfButton4 = QPushButton(self.frame3,"dtmfButton4")
        dtmfButton4_font = QFont(self.dtmfButton4.font())
        dtmfButton4_font.setPointSize(10)
        self.dtmfButton4.setFont(dtmfButton4_font)

        layout1.addWidget(self.dtmfButton4,1,0)

        self.dtmfButton3 = QPushButton(self.frame3,"dtmfButton3")
        dtmfButton3_font = QFont(self.dtmfButton3.font())
        dtmfButton3_font.setPointSize(10)
        self.dtmfButton3.setFont(dtmfButton3_font)

        layout1.addWidget(self.dtmfButton3,0,2)

        self.dtmfButton2 = QPushButton(self.frame3,"dtmfButton2")
        dtmfButton2_font = QFont(self.dtmfButton2.font())
        dtmfButton2_font.setPointSize(10)
        self.dtmfButton2.setFont(dtmfButton2_font)

        layout1.addWidget(self.dtmfButton2,0,1)

        self.dtmfButtonHash = QPushButton(self.frame3,"dtmfButtonHash")
        dtmfButtonHash_font = QFont(self.dtmfButtonHash.font())
        dtmfButtonHash_font.setPointSize(10)
        self.dtmfButtonHash.setFont(dtmfButtonHash_font)

        layout1.addWidget(self.dtmfButtonHash,3,2)
        frame3Layout.addLayout(layout1)

        self.textLabel4 = QLabel(self.centralWidget(),"textLabel4")
        self.textLabel4.setGeometry(QRect(10,138,50,30))

        self.lookupAddressButton = QPushButton(self.centralWidget(),"lookupAddressButton")
        self.lookupAddressButton.setGeometry(QRect(370,20,31,31))
        self.lookupAddressButton.setPixmap(QPixmap.fromMimeSource("filefind.png"))

        self.callButton = QPushButton(self.centralWidget(),"callButton")
        self.callButton.setGeometry(QRect(50,60,80,30))

        self.hangupButton = QPushButton(self.centralWidget(),"hangupButton")
        self.hangupButton.setEnabled(0)
        self.hangupButton.setGeometry(QRect(140,60,80,30))

        self.statusLabel = QLabel(self.centralWidget(),"statusLabel")
        self.statusLabel.setGeometry(QRect(60,140,180,31))

        self.debuggingTextEdit = QTextEdit(self.centralWidget(),"debuggingTextEdit")
        self.debuggingTextEdit.setGeometry(QRect(0,270,490,120))
        self.debuggingTextEdit.setSizePolicy(QSizePolicy(7,7,0,0,self.debuggingTextEdit.sizePolicy().hasHeightForWidth()))
        debuggingTextEdit_font = QFont(self.debuggingTextEdit.font())
        debuggingTextEdit_font.setFamily("Courier")
        debuggingTextEdit_font.setPointSize(10)
        self.debuggingTextEdit.setFont(debuggingTextEdit_font)
        self.debuggingTextEdit.setTextFormat(QTextEdit.PlainText)
        self.debuggingTextEdit.setWrapPolicy(QTextEdit.Anywhere)
        self.debuggingTextEdit.setUndoDepth(0)
        self.debuggingTextEdit.setReadOnly(1)
        self.debuggingTextEdit.setUndoRedoEnabled(0)

        self.addressComboBox = QComboBox(0,self.centralWidget(),"addressComboBox")
        self.addressComboBox.setGeometry(QRect(50,20,311,31))
        self.addressComboBox.setEditable(1)
        self.addressComboBox.setSizeLimit(20)
        self.addressComboBox.setInsertionPolicy(QComboBox.AtTop)
        self.addressComboBox.setAutoCompletion(1)
        self.addressComboBox.setDuplicatesEnabled(0)

        self.clearButton = QPushButton(self.centralWidget(),"clearButton")
        self.clearButton.setGeometry(QRect(10,400,71,31))

        LayoutWidget = QWidget(self.centralWidget(),"layout6")
        LayoutWidget.setGeometry(QRect(11,191,246,28))
        layout6 = QHBoxLayout(LayoutWidget,11,6,"layout6")

        self.textLabel2 = QLabel(LayoutWidget,"textLabel2")
        textLabel2_font = QFont(self.textLabel2.font())
        textLabel2_font.setPointSize(10)
        self.textLabel2.setFont(textLabel2_font)
        layout6.addWidget(self.textLabel2)

        self.sentPacketsLineEdit = QLineEdit(LayoutWidget,"sentPacketsLineEdit")
        sentPacketsLineEdit_font = QFont(self.sentPacketsLineEdit.font())
        sentPacketsLineEdit_font.setFamily("Courier")
        self.sentPacketsLineEdit.setFont(sentPacketsLineEdit_font)
        layout6.addWidget(self.sentPacketsLineEdit)

        LayoutWidget_2 = QWidget(self.centralWidget(),"layout6_2")
        LayoutWidget_2.setGeometry(QRect(10,220,246,28))
        layout6_2 = QHBoxLayout(LayoutWidget_2,11,6,"layout6_2")

        self.textLabel2_r = QLabel(LayoutWidget_2,"textLabel2_r")
        textLabel2_r_font = QFont(self.textLabel2_r.font())
        textLabel2_r_font.setPointSize(10)
        self.textLabel2_r.setFont(textLabel2_r_font)
        layout6_2.addWidget(self.textLabel2_r)

        self.rcvdPacketsLineEdit = QLineEdit(LayoutWidget_2,"rcvdPacketsLineEdit")
        rcvdPacketsLineEdit_font = QFont(self.rcvdPacketsLineEdit.font())
        rcvdPacketsLineEdit_font.setFamily("Courier")
        self.rcvdPacketsLineEdit.setFont(rcvdPacketsLineEdit_font)
        layout6_2.addWidget(self.rcvdPacketsLineEdit)

        self.fileNewAction = QAction(self,"fileNewAction")
        self.fileNewAction.setIconSet(QIconSet(QPixmap.fromMimeSource("icon-network.png")))
        self.fileOpenAction = QAction(self,"fileOpenAction")
        self.fileOpenAction.setIconSet(QIconSet(QPixmap.fromMimeSource("fileopen")))
        self.fileSaveAction = QAction(self,"fileSaveAction")
        self.fileSaveAction.setIconSet(QIconSet(QPixmap.fromMimeSource("filesave")))
        self.fileSaveAsAction = QAction(self,"fileSaveAsAction")
        self.filePrintAction = QAction(self,"filePrintAction")
        self.filePrintAction.setIconSet(QIconSet(QPixmap.fromMimeSource("print")))
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
        self.filePrintAction.addTo(self.fileMenu)
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
        self.connect(self.filePrintAction,SIGNAL("activated()"),self.filePrint)
        self.connect(self.fileExitAction,SIGNAL("activated()"),self.fileExit)
        self.connect(self.helpIndexAction,SIGNAL("activated()"),self.helpIndex)
        self.connect(self.helpContentsAction,SIGNAL("activated()"),self.helpContents)
        self.connect(self.helpAboutAction,SIGNAL("activated()"),self.helpAbout)
        self.connect(self.lookupAddressButton,SIGNAL("clicked()"),self.lookupAddressButton_clicked)
        self.connect(self.callButton,SIGNAL("clicked()"),self.callButton_clicked)
        self.connect(self.hangupButton,SIGNAL("clicked()"),self.hangupButton_clicked)
        self.connect(self.clearButton,SIGNAL("clicked()"),self.clearButton_clicked)


    def languageChange(self):
        self.setCaption(self.__tr("Shtoom - Qt UI"))
        self.textLabel1.setText(self.__tr("Call:"))
        self.dtmfButton9.setText(self.__tr("9"))
        self.dtmfButton0.setText(self.__tr("0"))
        self.dtmfButton1.setText(self.__tr("1"))
        self.dtmfButtonStar.setText(self.__tr("*"))
        self.dtmfButton5.setText(self.__tr("5"))
        self.dtmfButton7.setText(self.__tr("7"))
        self.dtmfButton6.setText(self.__tr("6"))
        self.dtmfButton8.setText(self.__tr("8"))
        self.dtmfButton4.setText(self.__tr("4"))
        self.dtmfButton3.setText(self.__tr("3"))
        self.dtmfButton2.setText(self.__tr("2"))
        self.dtmfButtonHash.setText(self.__tr("#"))
        self.textLabel4.setText(self.__tr("Status"))
        self.lookupAddressButton.setText(QString.null)
        self.callButton.setText(self.__tr("Call"))
        self.hangupButton.setText(self.__tr("Hang Up"))
        self.statusLabel.setText(QString.null)
        QToolTip.add(self.debuggingTextEdit,self.__tr("Debugging Messages"))
        self.clearButton.setText(self.__tr("Clear"))
        self.textLabel2.setText(self.__tr("Sent Pkts"))
        self.textLabel2_r.setText(self.__tr("Rcvd Pkts"))
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
        self.filePrintAction.setText(self.__tr("Print"))
        self.filePrintAction.setMenuText(self.__tr("&Print..."))
        self.filePrintAction.setAccel(self.__tr("Ctrl+P"))
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

    def filePrint(self):
        print "ShtoomMainWindow.filePrint(): Not implemented yet"

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

    def __tr(self,s,c = None):
        return qApp.translate("ShtoomMainWindow",s,c)
