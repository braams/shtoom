unix {
  UI_DIR = .ui
  MOC_DIR = .moc
  OBJECTS_DIR = .obj
}
FORMS	= shtoommain.ui \
	preferencesdialog.ui
IMAGES	= images/filenew \
	images/fileopen \
	images/filesave \
	images/print \
	images/undo \
	images/redo \
	images/editcut \
	images/editcopy \
	images/editpaste \
	images/searchfind
TEMPLATE	=app
CONFIG	+= qt warn_on release
LANGUAGE	= C++
