To update the base .pot (which contains the translation template), and
any existing '.po' (translation) files, run 

    % ./i18n/makepots.py

This will update i18n/shtoom.pot and any .po files that are already there.

To create a new language-specific .po file, change to the 'i18n' directory,
and run 

    % msginit -len_AU -i shtoom.pot

(Obviously, replacing en_AU with the new language). This will create 
en_AU.po. Edit this file, add it to svn (or email it to me) and you're
done! If you don't have the msginit &c commands on your system, please
let me know and I'll generate one for you.


To install the .mo files, run 

    % ./i18n/installpo.py <targetdir>

Work still to be done:
    Install the .mo files from setup.py
    Determine the right thing to do with windows.
