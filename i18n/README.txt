To update the base .pot file, from the root (the directory with 'shtoom', 
'scripts' and 'i18n' directories), run 

    % ./i18n/makepots.sh

This will update i18n/shtoom.pot

To create a new language-specific .po file, change to the 'i18n' directory,
and run 

    % msginit -len_AU -i shtoom.pot

(Obviously, replacing en_AU with the new language). This will create 
en_AU.po. Edit this file, add it to svn (or email it to me) and you're
done! If you don't have the msginit &c commands on your system, please
let me know and I'll generate one for you.

If the base translations file (shtoom.pot) is updated, you can merge
in the changes with 

    % msgmerge -U en_AU.po shtoom.pot 

Edit en_AU.po to include the updated entries, and once again, check it
in or send it to me for checkin.


