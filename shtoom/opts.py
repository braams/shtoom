
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
    from shtoom.Options import AllOptions, OptionGroup, StringOption, PasswordOption, NumberOption, ChoiceOption, BooleanOption
    opts = AllOptions()

    app.appSpecificOptions(opts)

    network = OptionGroup('network', 'Network Settings')
    network.add(StringOption('localip','listen on this local ip address'))
    network.add(NumberOption('listenport','run the sip listener on this port',
                                    shortopt='p'))
    network.add(StringOption('outbound_proxy','use this outbound proxy to make calls'))
    network.add(ChoiceOption('stun_policy','When should STUN be used?', 'rfc1918',
                                    choices=['never','always','rfc1918']))
    network.add(BooleanOption('use_upnp','Use UPnP to punch holes in firewalls', False))

    network.add(NumberOption('force_rtp_port','force RTP to use this port'))
    opts.add(network)

    identity = OptionGroup('identity', 'Identity Settings')
    identity.add(StringOption('email_address','use this email address'))
    identity.add(StringOption('username','use this user name'))
    opts.add(identity)

    proxy = OptionGroup('proxy', 'SIP Proxy Settings')
    proxy.add(StringOption('outbound_proxy_url','use this proxy for outbound SIP messages'))
    opts.add(proxy)

    register = OptionGroup('register', 'Registration')
    register.add(StringOption('register_uri',
                        'URI of registration server (e.g. sip:divmod.com:5060)'))
    register.add(StringOption('register_user','Username to register'))
    register.add(StringOption('register_authuser','Username to use for auth'))
    register.add(PasswordOption('register_authpasswd','Passwd to use for auth'))
    opts.add(register)

    debug = OptionGroup('debug', 'Debugging', gui=False)
    debug.add(BooleanOption('stdout','Log to stdout', False))
    debug.add(BooleanOption('no_config_file',
                                  "Don't read from or write to config file",
                                  False, shortopt='N'))
    opts.add(debug)
    return opts
