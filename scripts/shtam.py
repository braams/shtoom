#!/usr/bin/env python

# Copyright (C) 2004 Anthony Baxter

# Hack hack hack.
import sys ; sys.path.append(sys.path.pop(0))

app = None

def main():
    from shtoom.app.answer import AnsweringMachine
    global app

    app = AnsweringMachine()
    app.boot()
    app.start()

if __name__ == "__main__":
    main()
