
all: shtoommainwindow.py

shtoommainwindow.py: shtoommainwindow.ui
	pyuic shtoommainwindow.ui -o shtoommainwindow.py

preferencesdialog.py: preferencesdialog.ui
	pyuic preferencesdialog.ui -o preferencesdialog.py

clean:
	rm -f *.pyo *.pyc *~
