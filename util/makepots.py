#!/bin/zsh

./util/libglade-xgettext -o glade.pot ./shtoom/ui/gnomeui/shtoom.glade
xgettext -o python.pot --keyword="__tr" **/*.py
msgcomm --more-than=0 -o shtoom.pot python.pot glade.pot
rm python.pot glade.pot
