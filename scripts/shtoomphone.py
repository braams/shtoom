#!/usr/bin/env python

# Copyright (C) 2004 Anthony Baxter

# Hack hack hack.
import sys, os
f = sys.path.pop(0)
if f.endswith('scripts') and os.path.isdir(os.path.join(os.path.dirname(f),
                                                        'shtoom')):
    sys.path.insert(0, os.path.dirname(f))
else:
    sys.path.append(f)

app = None

def main():
    from twisted.python import threadable
    threadable.init(1)

    from shtoom.app.phone import Phone
    global app

    app = Phone()
    app.boot(args=sys.argv[1:])

    app.start()

if __name__ == "__main__":
    from shtoom import i18n
    i18n.install()
    main()
