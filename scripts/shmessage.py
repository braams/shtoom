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
    from shtoom.app.message import Message
    global app

    app = Message()
    app.boot()
    app.start()

if __name__ == "__main__":
    main()
