
# Copyright (C) 2004 Anthony Baxter

def getLocalUsername():
    try:
        import pwd
    except ImportError:
        # XXX how to get username on Windows?
        raise RuntimeError, "No pwd module - please supply a --username option"
    import os
    username = pwd.getpwuid(os.getuid())[0]
    return username

def buildOptions(app):
    from shtoom.Options import AllOptions, OptionGroup, StringOption, NumberOption, ChoiceOption, BooleanOption
    opts = AllOptions()

    app.appSpecificOptions(opts)

    network = OptionGroup('network', 'Network Settings')
    network.addOption(StringOption('localip','use LOCALIP for local ip address'))
    network.addOption(NumberOption('listenport','use PORT for sip listener'))
    network.addOption(ChoiceOption('stun_policy','STUN policy', 'rfc1918', choices=['never','always','rfc1918']))
    network.addOption(BooleanOption('use_upnp','Use UPnP', False))
    opts.addGroup(network)

    identity = OptionGroup('identity', 'Identity Settings')
    identity.addOption(StringOption('email','use email address EMAIL'))
    identity.addOption(StringOption('username','use user name USERNAME'))
    opts.addGroup(identity)
    
    register = OptionGroup('register', 'Registration')
    register.addOption(StringOption('register_uri','URI of registration server (e.g. sip:divmod.com:5060)'))
    register.addOption(StringOption('register_user','Username to register with'))
    register.addOption(StringOption('register_authuser','Username to auth with'))
    register.addOption(StringOption('register_authpasswd','Username to auth with'))
    opts.addGroup(register)

    debug = OptionGroup('debug', 'Debugging')
    debug.addOption(BooleanOption('stdout','Log to stdout', False))
    opts.addGroup(debug)

    return opts


def parseOptions(app):
    import optparse, sys
    import shtoom
    Opts = app.getOptions()

    parser = optparse.OptionParser(version='%%prog %s'%shtoom.Version)

    Opts.buildOptParse(parser)
    (opts, args) = parser.parse_args()

    Opts.loadOptsFile()
    Opts.handleOptParse(opts, args)
    Opts.saveOptsFile()
    Opts.setOptions(app.getSettings())

def defaultSettings():
    class _settings: 
        pass
    o = _settings()
    o.localip = None
    o.localport = None
    o.username = None
    o.userdetail = None
    o.email_address = None
    o.ui = None
    o.audio = None
    o.audio_infile = None
    o.audio_outfile = None
    o.register_time = 900
    o.register_uri = None
    o.register_authuser = None
    o.register_authpasswd = None
    return o

