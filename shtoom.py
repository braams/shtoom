#!/usr/bin/env python



def tryQtInterface():
    try:
        import qt
    except ImportError:
        qt = None
    if qt is not None:
        from shtoom.ui.qtshtoom import main
        main()
        sys.exit()

def main():
    import sys
    tryQtInterface()
    # Other interfaces here
    print "Error: Couldn't load _any_ userinterfaces"

if __name__ == "__main__":
    main()
