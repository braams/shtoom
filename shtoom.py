#!/usr/bin/env python

# Copyright (C) 2004 Anthony Baxter

# Hack hack hack.
import sys ; sys.path.append(sys.path.pop(0))

app = None

def main():
    from twisted.python import threadable
    threadable.init(1)

    from shtoom.app.phone import Phone
    global app

    app = Phone()
    app.boot()

    app.start()

if __name__ == "__main__":
    main()
