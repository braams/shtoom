#!/bin/zsh

intltool-extract -t gettext/glade shtoom/ui/gnomeui/shtoom.glade
xgettext -o i18n/glade.pot --keyword="N_" shtoom/ui/gnomeui/shtoom.glade
xgettext -o i18n/python.pot --keyword="__tr" scripts/*.py shtoom/**/*.py
msgcomm --more-than=0 -o i18n/shtoom.pot i18n/python.pot i18n/glade.pot
rm i18n/python.pot i18n/glade.pot
