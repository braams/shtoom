# -*- coding: utf-8 -*-

from qt import *
from shtoom.Options import NoDefaultOption

class PreferencesDialog(QDialog):
    def __init__(self, main, opts, parent = None,name = None,modal = 0,fl = 0):
        self.main = main
        self.opts = opts
        QDialog.__init__(self,parent,name,modal,fl)

        self.setProperty("name",QVariant("PreferencesDialog"))
        self.setProperty("sizeGripEnabled",QVariant(QVariant(1,0)))
        PreferencesDialogLayout = QVBoxLayout(self,11,6,"PreferencesDialogLayout")
        self.TabWidget = QTabWidget(self,"TabWidget")

        self.tabs = {}
        self.options = {}

        for group in self.opts:
            Tab = QWidget(self.TabWidget,group.getName())
            for optnumber, option in enumerate(group):
                ypos = 15+(32*optnumber)
                label = QLabel(Tab,"text"+option.getName())
                label.setProperty("geometry",
                    QVariant(QRect(7,ypos,131,30)))
                label.setProperty("text",
                    QVariant(self.__tr(option.getPrettyName())))
                QToolTip.add(label,self.__tr(option.getDescription()))

                if option.optionType in ( 'String', 'Number', 'Password' ):
                    # XXX use KPasswordEdit, if it's available!
                    edit = QLineEdit(Tab,"edit"+option.getName())
                    if option.optionType == 'String':
                        xsize = 240
                    else:
                        xsize = 50
                    edit.setProperty("geometry",
                        QVariant(QRect(147,ypos,xsize,30)))
                    val = option.getValue()
                    if val is not NoDefaultOption:
                        val = str(val)
                        edit.setProperty("text", QVariant(QString(val)))
                    QToolTip.add(edit,self.__tr(option.getDescription()))
                    get = lambda e=edit: str(e.text())

                elif option.optionType == 'Boolean':
                    edit = QCheckBox(Tab,option.getName())
                    edit.setProperty("geometry",QVariant(QRect(147,ypos,31,31)))
                    QToolTip.add(edit,self.__tr(option.getDescription()))
                    get = edit.isChecked

                elif option.optionType == 'Choice':
                    edit = None
                    choices = option.getChoices()
                    btGrp = QButtonGroup(Tab,option.getName())
                    QToolTip.add(btGrp,self.__tr(option.getDescription()))
                    xsize = 70*len(choices)
                    btGrp.setProperty("geometry",
                                      QVariant(QRect(147,ypos,xsize,30)))
                    buttons = []
                    for cnum, c in enumerate(choices):
                        xpos = 3 + cnum*64
                        rb = QRadioButton(btGrp,c)
                        rb.setProperty("geometry",
                                    QVariant(QRect(xpos,5,64,20)))
                        rb.setProperty("text",QVariant(self.__tr(c)))
                        if option.getValue() == c:
                            rb.setProperty("checked", QVariant(1,0))
                        buttons.append(rb)
                    edit = (btGrp, buttons)
                    get = lambda n=c, b=buttons: findCheckedButton(n,b)

                else:
                    raise ValueError, "Unknown option %s"%(option.optionType)
                #print option.getName(), get()
                self.options[option.getName()] = (option.optionType, get, edit)

            self.tabs[group.getName()] = Tab
            self.TabWidget.insertTab(Tab,QString(group.getDescription()))

        PreferencesDialogLayout.addWidget(self.TabWidget)
        Layout1 = QHBoxLayout(None,0,6,"Layout1")
        self.buttonHelp = QPushButton(self,"buttonHelp")
        self.buttonHelp.setProperty("autoDefault",QVariant(QVariant(1,0)))
        Layout1.addWidget(self.buttonHelp)
        spacer = QSpacerItem(20,20,QSizePolicy.Expanding,QSizePolicy.Minimum)
        Layout1.addItem(spacer)
        self.buttonSave = QPushButton(self,"buttonSave")
        self.buttonSave.setProperty("autoDefault",QVariant(QVariant(1,0)))
        self.buttonSave.setProperty("default",QVariant(QVariant(1,0)))
        Layout1.addWidget(self.buttonSave)
        self.buttonCancel = QPushButton(self,"buttonCancel")
        self.buttonCancel.setProperty("autoDefault",QVariant(QVariant(1,0)))
        Layout1.addWidget(self.buttonCancel)
        self.buttonHelp.setProperty("text",QVariant(self.__tr("Help")))
        self.buttonHelp.setProperty("accel",QVariant(self.__tr("F1")))
        self.buttonSave.setProperty("text",QVariant(self.__tr("Save")))
        self.buttonSave.setProperty("accel",QVariant(self.__tr("Alt+S")))
        self.buttonCancel.setProperty("text",QVariant(self.__tr("Cancel")))
        self.buttonCancel.setProperty("accel",QVariant(QString.null))
        PreferencesDialogLayout.addLayout(Layout1)
        self.resize(QSize(528,368).expandedTo(self.minimumSizeHint()))
        self.clearWState(Qt.WState_Polished)
        self.connect(self.buttonSave,SIGNAL("clicked()"),
                                        self.preferences_save)
        self.connect(self.buttonCancel,SIGNAL("clicked()"),
                                        self.main.preferences_discard)

    def __tr(self,s,c = None):
        return qApp.translate("PreferencesDialog",s,c)

    def preferences_save(self):
        out = {}
        for k, ( type, get, edit ) in self.options.items():
            out[k] = get()
        self.main.preferences_save(out)

def findCheckedButton(name, blist):
    print "buttons", name, ', '.join([str(x.text()) for x in blist])
    for b in blist:
        if b.isChecked(): return b.text()
