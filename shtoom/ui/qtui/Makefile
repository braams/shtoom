
all: shtoommain.py  preferencesdialog.py

shtoommain.py: shtoommain.ui
	pyuic shtoommain.ui -o shtoommain.py

preferencesdialog.py: preferencesdialog.ui
	pyuic preferencesdialog.ui -o preferencesdialog.py

clean:
	rm -f *.pyo *.pyc *~
