# Copyright (C) 2004,2005 Anthony Baxter

from gettext import gettext as _
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

    network = OptionGroup('network', _('Network Settings'))
    network.add(StringOption('localip',_('listen on this local ip address')))
    network.add(NumberOption('listenport',_('sip listener on this port'),
                                    shortopt='p'))
    network.add(StringOption('outbound_proxy',
                        _('use this outbound proxy to make calls')))
    network.add(ChoiceOption('stun_policy',
                        _('When should STUN be used?'), 'rfc1918',
                                    choices=['never','always','rfc1918']))
    network.add(ChoiceOption('nat',
                _('Use this NAT traversal technique'), 'both',
                                    choices=['both', 'upnp', 'stun', 'none']))

    network.add(NumberOption('force_rtp_port',
                            _('force RTP to use this port')))
    opts.add(network)

    identity = OptionGroup('identity', _('Identity Settings'))
    identity.add(StringOption('email_address', _('use this email address')))
    identity.add(StringOption('username', _('use this user name')))
    opts.add(identity)

    proxy = OptionGroup('proxy', 'SIP Proxy Settings')
    proxy.add(StringOption('outbound_proxy_url',
            _('use this proxy for outbound SIP messages')))
    opts.add(proxy)

    register = OptionGroup('register', _('Registration'))
    register.add(StringOption('register_uri',
                    _('URI of registration server (e.g. sip:divmod.com:5060)')))
    register.add(StringOption('register_user', _('Username to register')))
    register.add(StringOption('register_authuser',
                                        _('Username to use for auth')))
    register.add(PasswordOption('register_authpasswd',
                                        _('Passwd to use for auth')))
    opts.add(register)

    debug = OptionGroup('debug', _('Debugging'), gui=False)
    debug.add(BooleanOption('stdout', _('Log to stdout'), False))
    debug.add(BooleanOption('no_config_file',
                                  _("Don't read from or write to config file"),
                                  False, shortopt='N'))
    opts.add(debug)
    return opts
