# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'pysipmain.ui'
#
# Created: Fri Nov 14 11:41:11 2003
#      by: The PyQt User Interface Compiler (pyuic) 3.8.1
#
# WARNING! All changes made in this file will be lost!


from qt import *

image0_data = [
"22 22 5 1",
". c None",
"# c #000000",
"c c #838100",
"a c #ffff00",
"b c #ffffff",
"......................",
"......................",
"......................",
"............####....#.",
"...........#....##.##.",
"..................###.",
".................####.",
".####...........#####.",
"#abab##########.......",
"#babababababab#.......",
"#ababababababa#.......",
"#babababababab#.......",
"#ababab###############",
"#babab##cccccccccccc##",
"#abab##cccccccccccc##.",
"#bab##cccccccccccc##..",
"#ab##cccccccccccc##...",
"#b##cccccccccccc##....",
"###cccccccccccc##.....",
"##cccccccccccc##......",
"###############.......",
"......................"
]
image1_data = [
"22 22 5 1",
". c None",
"# c #000000",
"a c #838100",
"b c #c5c2c5",
"c c #cdb6d5",
"......................",
".####################.",
".#aa#bbbbbbbbbbbb#bb#.",
".#aa#bbbbbbbbbbbb#bb#.",
".#aa#bbbbbbbbbcbb####.",
".#aa#bbbccbbbbbbb#aa#.",
".#aa#bbbccbbbbbbb#aa#.",
".#aa#bbbbbbbbbbbb#aa#.",
".#aa#bbbbbbbbbbbb#aa#.",
".#aa#bbbbbbbbbbbb#aa#.",
".#aa#bbbbbbbbbbbb#aa#.",
".#aaa############aaa#.",
".#aaaaaaaaaaaaaaaaaa#.",
".#aaaaaaaaaaaaaaaaaa#.",
".#aaa#############aa#.",
".#aaa#########bbb#aa#.",
".#aaa#########bbb#aa#.",
".#aaa#########bbb#aa#.",
".#aaa#########bbb#aa#.",
".#aaa#########bbb#aa#.",
"..##################..",
"......................"
]

class PySipMainWindow(QMainWindow):
    def __init__(self,parent = None,name = None,fl = 0):
        QMainWindow.__init__(self,parent,name,fl)
        self.statusBar()

        self.image0 = QPixmap(image0_data)
        self.image1 = QPixmap(image1_data)

        if not name:
            self.setName("PySipMainWindow")


        self.setCentralWidget(QWidget(self,"qt_central_widget"))

        self.textLabel1 = QLabel(self.centralWidget(),"textLabel1")
        self.textLabel1.setGeometry(QRect(10,230,391,20))

        self.logMessages = QTextEdit(self.centralWidget(),"logMessages")
        self.logMessages.setGeometry(QRect(0,250,591,141))
        self.logMessages.setWrapPolicy(QTextEdit.Anywhere)
        self.logMessages.setReadOnly(1)

        self.pushButton2 = QPushButton(self.centralWidget(),"pushButton2")
        self.pushButton2.setGeometry(QRect(140,221,61,30))

        self.textLabel4 = QLabel(self.centralWidget(),"textLabel4")
        self.textLabel4.setGeometry(QRect(10,90,34,31))

        self.GoButton = QPushButton(self.centralWidget(),"GoButton")
        self.GoButton.setGeometry(QRect(430,0,90,30))

        self.textLabel5 = QLabel(self.centralWidget(),"textLabel5")
        self.textLabel5.setGeometry(QRect(120,40,91,20))

        self.StatusLabel = QLabel(self.centralWidget(),"StatusLabel")
        self.StatusLabel.setGeometry(QRect(220,30,161,40))
        self.StatusLabel.setPaletteBackgroundColor(QColor(220,230,227))

        self.pushButton3 = QPushButton(self.centralWidget(),"pushButton3")
        self.pushButton3.setGeometry(QRect(300,90,70,31))

        self.rtpHostTextLine = QLineEdit(self.centralWidget(),"rtpHostTextLine")
        self.rtpHostTextLine.setGeometry(QRect(94,1,142,30))

        self.textLabel3 = QLabel(self.centralWidget(),"textLabel3")
        self.textLabel3.setGeometry(QRect(242,1,33,27))

        self.textLabel2 = QLabel(self.centralWidget(),"textLabel2")
        self.textLabel2.setGeometry(QRect(51,1,37,27))

        self.rtpPortTextLine = QLineEdit(self.centralWidget(),"rtpPortTextLine")
        self.rtpPortTextLine.setGeometry(QRect(281,1,142,30))

        self.sipURL = QLineEdit(self.centralWidget(),"sipURL")
        self.sipURL.setGeometry(QRect(50,90,231,31))

        self.fileOpenAction = QAction(self,"fileOpenAction")
        self.fileOpenAction.setIconSet(QIconSet(self.image0))
        self.fileSaveAction = QAction(self,"fileSaveAction")
        self.fileSaveAction.setIconSet(QIconSet(self.image1))
        self.fileSaveAsAction = QAction(self,"fileSaveAsAction")
        self.Preferences = QAction(self,"Preferences")
        self.fileExitAction = QAction(self,"fileExitAction")
        self.helpContentsAction = QAction(self,"helpContentsAction")
        self.helpIndexAction = QAction(self,"helpIndexAction")
        self.helpAboutAction = QAction(self,"helpAboutAction")


        self.toolBar = QToolBar(QString(""),self,Qt.DockTop)

        self.fileExitAction.addTo(self.toolBar)


        self.menubar = QMenuBar(self,"menubar")


        self.audioMenu = QPopupMenu(self)
        self.audioMenu.insertSeparator()
        self.fileOpenAction.addTo(self.audioMenu)
        self.fileSaveAction.addTo(self.audioMenu)
        self.fileSaveAsAction.addTo(self.audioMenu)
        self.audioMenu.insertSeparator()
        self.Preferences.addTo(self.audioMenu)
        self.audioMenu.insertSeparator()
        self.fileExitAction.addTo(self.audioMenu)
        self.menubar.insertItem(QString(""),self.audioMenu,1)

        self.helpMenu = QPopupMenu(self)
        self.helpContentsAction.addTo(self.helpMenu)
        self.helpIndexAction.addTo(self.helpMenu)
        self.helpMenu.insertSeparator()
        self.helpAboutAction.addTo(self.helpMenu)
        self.menubar.insertItem(QString(""),self.helpMenu,2)


        self.languageChange()

        self.resize(QSize(600,480).expandedTo(self.minimumSizeHint()))
        self.clearWState(Qt.WState_Polished)

        self.connect(self.fileOpenAction,SIGNAL("activated()"),self.fileOpen)
        self.connect(self.fileSaveAction,SIGNAL("activated()"),self.fileSave)
        self.connect(self.fileSaveAsAction,SIGNAL("activated()"),self.fileSaveAs)
        self.connect(self.Preferences,SIGNAL("activated()"),self.filePrint)
        self.connect(self.fileExitAction,SIGNAL("activated()"),self.fileExit)
        self.connect(self.helpIndexAction,SIGNAL("activated()"),self.helpIndex)
        self.connect(self.helpContentsAction,SIGNAL("activated()"),self.helpContents)
        self.connect(self.helpAboutAction,SIGNAL("activated()"),self.helpAbout)
        self.connect(self.GoButton,SIGNAL("clicked()"),self.pushButton1_clicked)
        self.connect(self.rtpPortTextLine,SIGNAL("textChanged(const QString&)"),self.rtpPortTextLine_textChanged)
        self.connect(self.rtpPortTextLine,SIGNAL("returnPressed()"),self.rtpPortTextLine_returnPressed)
        self.connect(self.pushButton2,SIGNAL("clicked()"),self.clear_logMessages)
        self.connect(self.pushButton3,SIGNAL("clicked()"),self.callButton_clicked)

        self.setTabOrder(self.GoButton,self.rtpHostTextLine)
        self.setTabOrder(self.rtpHostTextLine,self.rtpPortTextLine)


    def languageChange(self):
        self.setCaption(self.__tr("PySipMainWindow"))
        self.textLabel1.setText(self.__tr("Log Messages"))
        self.pushButton2.setText(self.__tr("clear"))
        self.textLabel4.setText(self.__tr("SIP:"))
        self.GoButton.setText(self.__tr("Send RTP"))
        self.textLabel5.setText(self.__tr("RTP status"))
        self.StatusLabel.setText(self.__tr("idle"))
        self.pushButton3.setText(self.__tr("Call"))
        self.rtpHostTextLine.setText(self.__tr("localhost"))
        self.textLabel3.setText(self.__tr("Port"))
        self.textLabel2.setText(self.__tr("Host"))
        self.rtpPortTextLine.setText(self.__tr("9010"))
        self.sipURL.setText(self.__tr("sip:96748002@gw2.off.ekorp.com"))
        self.fileOpenAction.setText(self.__tr("Load Audio"))
        self.fileOpenAction.setMenuText(self.__tr("&Load Audio..."))
        self.fileOpenAction.setAccel(self.__tr("Ctrl+O"))
        self.fileSaveAction.setText(self.__tr("Save"))
        self.fileSaveAction.setMenuText(self.__tr("&Save"))
        self.fileSaveAction.setAccel(self.__tr("Ctrl+S"))
        self.fileSaveAsAction.setText(self.__tr("Save As"))
        self.fileSaveAsAction.setMenuText(self.__tr("Save &As..."))
        self.fileSaveAsAction.setAccel(QString.null)
        self.Preferences.setText(self.__tr("Preferences"))
        self.Preferences.setMenuText(self.__tr("&Preferences"))
        self.Preferences.setAccel(self.__tr("Ctrl+P"))
        self.fileExitAction.setText(self.__tr("Exit"))
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
        self.toolBar.setLabel(self.__tr("Tools"))
        self.menubar.findItem(1).setText(self.__tr("&Audio"))
        self.menubar.findItem(2).setText(self.__tr("&Help"))


    def fileNew(self):
        print "PySipMainWindow.fileNew(): Not implemented yet"

    def fileOpen(self):
        print "PySipMainWindow.fileOpen(): Not implemented yet"

    def fileSave(self):
        print "PySipMainWindow.fileSave(): Not implemented yet"

    def fileSaveAs(self):
        print "PySipMainWindow.fileSaveAs(): Not implemented yet"

    def filePrint(self):
        print "PySipMainWindow.filePrint(): Not implemented yet"

    def fileExit(self):
        print "PySipMainWindow.fileExit(): Not implemented yet"

    def helpIndex(self):
        print "PySipMainWindow.helpIndex(): Not implemented yet"

    def helpContents(self):
        print "PySipMainWindow.helpContents(): Not implemented yet"

    def helpAbout(self):
        print "PySipMainWindow.helpAbout(): Not implemented yet"

    def pushButton1_clicked(self):
        print "PySipMainWindow.pushButton1_clicked(): Not implemented yet"

    def rtpPortTextLine_textChanged(self,a0):
        print "PySipMainWindow.rtpPortTextLine_textChanged(const QString&): Not implemented yet"

    def rtpPortTextLine_returnPressed(self):
        print "PySipMainWindow.rtpPortTextLine_returnPressed(): Not implemented yet"

    def clear_logMessages(self):
        print "PySipMainWindow.clear_logMessages(): Not implemented yet"

    def callButton_clicked(self):
        print "PySipMainWindow.callButton_clicked(): Not implemented yet"

    def __tr(self,s,c = None):
        return qApp.translate("PySipMainWindow",s,c)
