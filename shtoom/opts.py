
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
    network.addOption(StringOption('localip','listen on this local ip address'))
    network.addOption(NumberOption('listenport','run the sip listener on this port',
                                    shortopt='p'))
    #network.addOption(StringOption('outbound_proxy','use this outbound proxy to make calls'))
    network.addOption(ChoiceOption('stun_policy','When should STUN be used?', 'rfc1918',
                                    choices=['never','always','rfc1918']))
    network.addOption(BooleanOption('use_upnp','Use UPnP to punch holes in firewalls', False))

    network.addOption(NumberOption('force_rtp_port','force RTP to use this port'))
    opts.addGroup(network)

    identity = OptionGroup('identity', 'Identity Settings')
    identity.addOption(StringOption('email_address','use this email address'))
    identity.addOption(StringOption('username','use this user name'))
    opts.addGroup(identity)

    register = OptionGroup('register', 'Registration')
    register.addOption(StringOption('register_uri',
                        'URI of registration server (e.g. sip:divmod.com:5060)'))
    register.addOption(StringOption('register_user','Username to register'))
    register.addOption(StringOption('register_authuser','Username to use for auth'))
    register.addOption(StringOption('register_authpasswd','Passwd to use for auth'))
    opts.addGroup(register)

    debug = OptionGroup('debug', 'Debugging', gui=False)
    debug.addOption(BooleanOption('stdout','Log to stdout', False))
    debug.addOption(BooleanOption('no_config_file',
                                  "Don't read from or write to config file",
                                  False, shortopt='N'))
    opts.addGroup(debug)
    return opts
