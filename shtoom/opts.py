
# Copyright (C) 2004 Anthony Baxter

def parseOptions():
    import optparse, sys
    import shtoom.prefs, shtoom
    parser = optparse.OptionParser(version='%%prog %s'%shtoom.Version)
    parser.add_option('-i', '--localip', dest='localip',
                      help='use LOCALIP for local ip address',
                      metavar='LOCALIP')
    parser.add_option('-p', '--port', dest='localport', type='int',
                      help='use PORT for SIP listener',
                      metavar='PORT')
    parser.add_option('-u', '--ui', dest='ui',
                      help='use UI interface (qt, tk, ...)',
                      metavar='UI')
    parser.add_option('-a', '--audio', dest='audio',
                      help='use AUDIO interface (oss, fast, ...)',
                      metavar='AUDIO')
    parser.add_option('-e', '--email', dest='email',
                      help='use email address EMAIL',
                      metavar='EMAIL')
    parser.add_option('-n', '--username', dest='username',
                      help='use user name NAME',
                      metavar='NAME')
    parser.add_option('-s', '--stdout', dest='stdout',
                      help='debug to stdout (ALWAYS)',
                      metavar='STDOUT')
    parser.add_option('--audio-in', dest='audio_infile',
                      help='read audio from file INFILE',
                      metavar='INFILE')
    parser.add_option('--audio-out', dest='audio_outfile',
                      help='write audio to file OUTFILE',
                      metavar='OUTFILE')
    parser.add_option('--stun-policy', dest='stun_policy',
                  help='STUN policy (never, always, rfc1918) (default rfc1918)',
                  metavar='STUNPOLICY')
    parser.add_option('--use-upnp', dest='use_upnp',
                      help='Use UPnP (yes, no) (default no)',
                      metavar='USEUPNP')
    (opts, args) = parser.parse_args()
    if opts.localip:
        shtoom.prefs.localip = opts.localip
    if opts.localport:
        shtoom.prefs.localport = opts.localport
    if opts.email:
        shtoom.prefs.email_address = opts.email
    if opts.username:
        shtoom.prefs.username = opts.username
    if opts.ui:
        shtoom.prefs.ui = opts.ui
    if opts.audio:
        shtoom.prefs.audio = opts.audio
    # check both, or neither, are set
    if opts.audio_infile:
        shtoom.prefs.audio_infile = opts.audio_infile
    if opts.audio_outfile:
        shtoom.prefs.audio_outfile = opts.audio_outfile
    if opts.stdout:
        shtoom.prefs.stdout = True
