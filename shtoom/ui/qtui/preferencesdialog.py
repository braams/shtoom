# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'preferencesdialog.ui'
#
# Created: Fri Nov 14 11:41:12 2003
#      by: The PyQt User Interface Compiler (pyuic) 3.8.1
#
# WARNING! All changes made in this file will be lost!


from qt import *

class PreferencesDialog(QDialog):
    def __init__(self,parent = None,name = None,modal = 0,fl = 0):
        QDialog.__init__(self,parent,name,modal,fl)

        if not name:
            self.setName("PreferencesDialog")



        self.tabWidget2 = QTabWidget(self,"tabWidget2")
        self.tabWidget2.setGeometry(QRect(0,0,601,300))

        self.tab = QWidget(self.tabWidget2,"tab")

        LayoutWidget = QWidget(self.tab,"layout2")
        LayoutWidget.setGeometry(QRect(320,120,220,108))
        layout2 = QVBoxLayout(LayoutWidget,11,6,"layout2")

        self.textLabel1 = QLabel(LayoutWidget,"textLabel1")
        layout2.addWidget(self.textLabel1)

        self.slider2 = QSlider(LayoutWidget,"slider2")
        self.slider2.setOrientation(QSlider.Horizontal)
        layout2.addWidget(self.slider2)

        self.textLabel2 = QLabel(LayoutWidget,"textLabel2")
        layout2.addWidget(self.textLabel2)

        self.slider1 = QSlider(LayoutWidget,"slider1")
        self.slider1.setOrientation(QSlider.Horizontal)
        layout2.addWidget(self.slider1)

        self.buttonGroup1 = QButtonGroup(self.tab,"buttonGroup1")
        self.buttonGroup1.setGeometry(QRect(48,40,190,100))

        self.radioButton1 = QRadioButton(self.buttonGroup1,"radioButton1")
        self.radioButton1.setGeometry(QRect(20,30,150,21))

        self.radioButton2 = QRadioButton(self.buttonGroup1,"radioButton2")
        self.radioButton2.setGeometry(QRect(20,60,160,21))
        self.tabWidget2.insertTab(self.tab,QString(""))

        self.tab_2 = QWidget(self.tabWidget2,"tab_2")
        self.tabWidget2.insertTab(self.tab_2,QString(""))

        self.tab_3 = QWidget(self.tabWidget2,"tab_3")
        self.tabWidget2.insertTab(self.tab_3,QString(""))

        self.languageChange()

        self.resize(QSize(600,345).expandedTo(self.minimumSizeHint()))
        self.clearWState(Qt.WState_Polished)

        self.connect(self.radioButton1,SIGNAL("toggled(bool)"),self,SLOT("accept()"))
        self.connect(self.radioButton2,SIGNAL("toggled(bool)"),self,SLOT("accept()"))


    def languageChange(self):
        self.setCaption(self.__tr("Form1"))
        self.textLabel1.setText(self.__tr("Playback Volume"))
        self.textLabel2.setText(self.__tr("Record Volume"))
        self.buttonGroup1.setTitle(self.__tr("Audio Source"))
        self.radioButton1.setText(self.__tr("Audio from File"))
        self.radioButton2.setText(self.__tr("Audio In (/dev/dsp)"))
        self.tabWidget2.changeTab(self.tab,self.__tr("Audio"))
        self.tabWidget2.changeTab(self.tab_2,self.__tr("Network"))
        self.tabWidget2.changeTab(self.tab_3,self.__tr("Other"))


    def __tr(self,s,c = None):
        return qApp.translate("PreferencesDialog",s,c)
