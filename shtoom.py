#!/usr/bin/env python

# Copyright (C) 2004 Anthony Baxter

# Hack hack hack.
import sys ; sys.path.append(sys.path.pop(0))

def main():
    from shtoom.opts import parseOptions
    from shtoom.app.phone import Phone

    app = Phone()

    parseOptions(app)

    app.boot()

    app.start()

if __name__ == "__main__":
    main()
