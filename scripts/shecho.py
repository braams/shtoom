#!/usr/bin/env python

# Copyright (C) 2004 Anthony Baxter

# Hack hack hack.
import sys ; sys.path.append(sys.path.pop(0))

app = None

def main():
    from shtoom.app.echo import EchoServer
    global app

    app = EchoServer()
    app.boot()
    app.start()

if __name__ == "__main__":
    main()
