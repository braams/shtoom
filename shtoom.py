#!/usr/bin/env python

# Copyright (C) 2004 Anthony Baxter

# Hack hack hack.
import sys ; sys.path.append(sys.path.pop(0))

def main():
    from shtoom.opts import parseOptions
    from shtoom.ui.select import findUserInterface
    parseOptions()
    findUserInterface()

if __name__ == "__main__":
    main()
