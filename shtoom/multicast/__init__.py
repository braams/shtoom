#
#
# Copyright (c) 2004 Anthony Baxter.
#

import socket
if socket.__dict__.has_key("IP_ADD_MEMBERSHIP"):
    from unixspec import joinGroup,leaveGroup
else:
    raise ImportError,"Don't know how to support multicast on this system"

def ntp2delta(ticks):
    return (ticks - 220898800)
