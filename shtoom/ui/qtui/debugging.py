# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'debugging.ui'
#
# Created: Wed Jan 19 01:53:50 2005
#      by: The PyQt User Interface Compiler (pyuic) 3.13
#
# WARNING! All changes made in this file will be lost!


from qt import *


class Debugging(QDialog):
    def __init__(self,parent = None,name = None,modal = 0,fl = 0):
        QDialog.__init__(self,parent,name,modal,fl)

        if not name:
            self.setName("Debugging")


        DebuggingLayout = QVBoxLayout(self,11,6,"DebuggingLayout")

        self.debuggingTextEdit = QTextEdit(self,"debuggingTextEdit")
        debuggingTextEdit_font = QFont(self.debuggingTextEdit.font())
        debuggingTextEdit_font.setFamily("Courier")
        self.debuggingTextEdit.setFont(debuggingTextEdit_font)
        self.debuggingTextEdit.setTextFormat(QTextEdit.LogText)
        DebuggingLayout.addWidget(self.debuggingTextEdit)

        layout12 = QHBoxLayout(None,0,6,"layout12")

        self.debuggingCloseButton = QPushButton(self,"debuggingCloseButton")
        layout12.addWidget(self.debuggingCloseButton)
        spacer4 = QSpacerItem(40,20,QSizePolicy.Expanding,QSizePolicy.Minimum)
        layout12.addItem(spacer4)

        self.debuggingClearButton = QPushButton(self,"debuggingClearButton")
        layout12.addWidget(self.debuggingClearButton)
        DebuggingLayout.addLayout(layout12)

        self.languageChange()

        self.resize(QSize(338,270).expandedTo(self.minimumSizeHint()))
        self.clearWState(Qt.WState_Polished)

        self.connect(self.debuggingCloseButton,SIGNAL("clicked()"),self.debuggingCloseButton_clicked)
        self.connect(self.debuggingClearButton,SIGNAL("clicked()"),self.debuggingClearButton_clicked)


    def languageChange(self):
        self.setCaption(self.__tr("Debugging"))
        self.debuggingCloseButton.setText(self.__tr("Close"))
        self.debuggingClearButton.setText(self.__tr("Clear"))


    def debuggingCloseButton_clicked(self):
        print "Debugging.debuggingCloseButton_clicked(): Not implemented yet"

    def debuggingCloseButton_2_clicked(self):
        print "Debugging.debuggingCloseButton_2_clicked(): Not implemented yet"

    def debuggingClearButton_clicked(self):
        print "Debugging.debuggingClearButton_clicked(): Not implemented yet"

    def __tr(self,s,c = None):
        return qApp.translate("Debugging",s,c)
