# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'authdialog.ui'
#
# Created: Mon May 9 01:39:10 2005
#      by: The PyQt User Interface Compiler (pyuic) 3.13
#
# WARNING! All changes made in this file will be lost!


from qt import *

image0_data = \
    "\x89\x50\x4e\x47\x0d\x0a\x1a\x0a\x00\x00\x00\x0d" \
    "\x49\x48\x44\x52\x00\x00\x00\x32\x00\x00\x00\x1e" \
    "\x08\x06\x00\x00\x00\x6e\x51\x4d\xfc\x00\x00\x01" \
    "\x01\x49\x44\x41\x54\x58\x85\xd5\x98\x4b\x0e\xc3" \
    "\x20\x0c\x05\x1f\x11\x39\x53\x7b\xff\x55\x7a\xa5" \
    "\x28\x12\x5d\xb9\x42\x28\x11\xf8\x87\xe9\xac\x13" \
    "\xe4\xa9\xc1\x8f\x34\x95\x52\xb0\x2a\x47\xce\x05" \
    "\x00\xde\xd7\x95\x7a\xcf\xa6\x68\x11\x2a\x56\x0a" \
    "\x49\x66\x9b\x72\x78\x58\x15\x5f\x33\x4d\xe4\xb3" \
    "\xef\x45\xd3\xfd\xde\xf6\x72\x17\x91\xfe\xfa\x23" \
    "\xe7\xa2\xc6\x4d\x64\x96\x00\x61\x2e\x32\x5b\x80" \
    "\xd8\x34\x2f\xb7\x44\x49\x00\x86\x1d\x91\x48\x58" \
    "\x08\x10\x6a\x91\xc8\x2e\xd4\xa8\x44\x2c\x25\xda" \
    "\xb5\xb8\xa2\xe2\x64\xb7\xd8\x4a\xbd\x35\x38\x32" \
    "\xa2\x8e\x68\x25\xb4\xc9\x7e\xc7\x94\x64\x27\x09" \
    "\x0f\x01\x82\x3d\x7e\xa5\xc5\x78\x4a\x00\x4c\x11" \
    "\xe9\x96\x9a\x31\x9a\x4d\x03\xb1\x45\x3a\x62\x25" \
    "\xef\xb9\x9c\x11\xef\x83\x7d\x87\xa9\x08\x77\xbc" \
    "\x8e\xac\x31\x0a\x3b\x47\x46\x82\x2b\x22\xed\xcd" \
    "\x3f\x75\xa3\xae\x2c\xa6\x5b\x2b\xf2\xe2\x68\x22" \
    "\xb2\xc2\xc5\x51\x3d\x7e\x57\x90\x00\x14\x1d\x59" \
    "\x45\x80\x60\x8b\x44\x7f\x40\x3d\xd1\x15\xd1\x04" \
    "\x5a\xda\x36\xbc\xce\xd3\x5d\x02\x78\x10\xf1\xf8" \
    "\x03\xcd\x9b\x9f\xc8\x3f\x16\x5f\x33\x14\x88\x47" \
    "\xce\x25\xba\xd0\x1e\x5f\xab\x2c\xa1\x4b\x6f\xae" \
    "\x64\xe3\x00\x00\x00\x00\x49\x45\x4e\x44\xae\x42" \
    "\x60\x82"

class ShtoomAuthDialog(QDialog):
    def __init__(self,parent = None,name = None,modal = 0,fl = 0):
        QDialog.__init__(self,parent,name,modal,fl)

        self.image0 = QPixmap()
        self.image0.loadFromData(image0_data,"PNG")
        if not name:
            self.setName("ShtoomAuthenticationDialog")

        self.setIcon(self.image0)


        self.frame3 = QFrame(self,"frame3")
        self.frame3.setGeometry(QRect(0,0,311,198))
        self.frame3.setFrameShape(QFrame.StyledPanel)
        self.frame3.setFrameShadow(QFrame.Raised)

        LayoutWidget = QWidget(self.frame3,"layout8")
        LayoutWidget.setGeometry(QRect(-1,1,311,190))
        layout8 = QVBoxLayout(LayoutWidget,11,6,"layout8")

        self.realmLabel = QLabel(LayoutWidget,"realmLabel")
        self.realmLabel.setAlignment(QLabel.WordBreak | QLabel.AlignCenter)
        layout8.addWidget(self.realmLabel)

        layout2 = QGridLayout(None,1,1,0,6,"layout2")

        self.textLabel2 = QLabel(LayoutWidget,"textLabel2")
        self.textLabel2.setAlignment(QLabel.AlignVCenter | QLabel.AlignRight)

        layout2.addWidget(self.textLabel2,0,0)

        self.textLabel3 = QLabel(LayoutWidget,"textLabel3")
        self.textLabel3.setAlignment(QLabel.AlignVCenter | QLabel.AlignRight)

        layout2.addWidget(self.textLabel3,1,0)

        self.userEntry = QLineEdit(LayoutWidget,"userEntry")
        self.userEntry.setMinimumSize(QSize(200,0))
        self.userEntry.setAlignment(QLineEdit.AlignLeft)

        layout2.addWidget(self.userEntry,0,1)

        self.passwdEntry = QLineEdit(LayoutWidget,"passwdEntry")
        self.passwdEntry.setMinimumSize(QSize(200,0))
        self.passwdEntry.setEchoMode(QLineEdit.Password)
        self.passwdEntry.setAlignment(QLineEdit.AlignLeft)

        layout2.addWidget(self.passwdEntry,1,1)
        layout8.addLayout(layout2)

        layout7 = QHBoxLayout(None,0,6,"layout7")
        spacer1_3 = QSpacerItem(20,20,QSizePolicy.Expanding,QSizePolicy.Minimum)
        layout7.addItem(spacer1_3)

        self.saveButton = QCheckBox(LayoutWidget,"saveButton")
        layout7.addWidget(self.saveButton)
        spacer1_2 = QSpacerItem(30,20,QSizePolicy.Expanding,QSizePolicy.Minimum)
        layout7.addItem(spacer1_2)
        layout8.addLayout(layout7)

        self.line1 = QFrame(LayoutWidget,"line1")
        self.line1.setFrameShape(QFrame.HLine)
        self.line1.setFrameShadow(QFrame.Sunken)
        self.line1.setFrameShape(QFrame.HLine)
        layout8.addWidget(self.line1)

        layout6 = QHBoxLayout(None,0,6,"layout6")
        spacer1 = QSpacerItem(111,20,QSizePolicy.Expanding,QSizePolicy.Minimum)
        layout6.addItem(spacer1)

        self.pushButton1 = QPushButton(LayoutWidget,"pushButton1")
        layout6.addWidget(self.pushButton1)

        self.pushButton2 = QPushButton(LayoutWidget,"pushButton2")
        layout6.addWidget(self.pushButton2)
        layout8.addLayout(layout6)

        self.languageChange()

        self.resize(QSize(312,200).expandedTo(self.minimumSizeHint()))
        self.clearWState(Qt.WState_Polished)

        self.connect(self.userEntry,SIGNAL("returnPressed()"),self.userEntry_returnPressed)
        self.connect(self.passwdEntry,SIGNAL("returnPressed()"),self.passwdEntry_returnPressed)
        self.connect(self.pushButton1,SIGNAL("pressed()"),self.cancelButton_pressed)
        self.connect(self.pushButton2,SIGNAL("pressed()"),self.okButton_pressed)


    def languageChange(self):
        self.setCaption(self.__tr("Shtoom Authentication"))
        self.realmLabel.setText(self.__tr("Some authentication information is required"))
        self.textLabel2.setText(self.__tr("Username"))
        self.textLabel3.setText(self.__tr("Password"))
        self.saveButton.setText(self.__tr("Save this username and password"))
        self.pushButton1.setText(self.__tr("Cancel"))
        self.pushButton2.setText(self.__tr("OK"))


    def userEntry_returnPressed(self):
        print "ShtoomAuthDialog.userEntry_returnPressed(): Not implemented yet"

    def passwdEntry_returnPressed(self):
        print "ShtoomAuthDialog.passwdEntry_returnPressed(): Not implemented yet"

    def cancelButton_pressed(self):
        print "ShtoomAuthDialog.cancelButton_pressed(): Not implemented yet"

    def okButton_pressed(self):
        print "ShtoomAuthDialog.okButton_pressed(): Not implemented yet"

    def __tr(self,s,c = None):
        return qApp.translate("ShtoomAuthDialog",s,c)
