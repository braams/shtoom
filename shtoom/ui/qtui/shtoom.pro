unix {
  UI_DIR = .ui
  MOC_DIR = .moc
  OBJECTS_DIR = .obj
}
FORMS	= shtoommainwindow.ui
IMAGES	= images/filenew \
	images/fileopen \
	images/filesave \
	images/print \
	images/undo \
	images/redo \
	images/editcut \
	images/editcopy \
	images/editpaste \
	images/filefind.png \
	images/icon-network.png
TEMPLATE	=app
CONFIG	+= qt warn_on release
LANGUAGE	= C++
