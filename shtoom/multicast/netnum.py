#
#
# Copyright (c) 2004 Anthony Baxter.
#

def dq2num(addr,pad=0):
    import string
    l = map(string.atoi,string.split(addr,'.'))
    if pad:
        l = l+[0]*(4-len(l))
    return reduce(lambda x,y: (x<<8)|y, l)

def num2dq(num):
    import string
    l = [24, 16, 8, 0]
    a = map(lambda x,num=num:int((num&(255<<x))>>x),l)
    a = map(lambda x:str(((x<0) and (x+256)) or x),a)
    return string.join(a, '.')

class Address:
    def __init__(self,address):
        self.addr = address
        self._binaddr = dq2num(address, pad = 0)


class Network(Address):
    # create with, eg, ("192.102",16)
    def __init__(self,netnumber,prefixlen=32):
        self.net = netnumber
        self.prefixlen = prefixlen
        self._binaddr = dq2num(netnumber, pad = 1)
        self._mask = self.buildNetmask(prefixlen)
        self.mask = self.prettyNetmask()

    def buildNetmask(self,bits):
        nl = [1]*bits + [0]*(32-bits)
        return reduce(lambda x,y: (x<<1)|y, nl)

    def inNet(self,addr):
        binaddr = dq2num(addr)
        if (self._mask & binaddr) == self._binaddr:
            return 1
        else:
            return 0

    def broadcast(self):
        B = 0xffffffff
        b = self._mask ^ B
        #print "%x ^ %x  = %x "%(self._mask, B, b)
        return b | self._binaddr

    def prettyNetmask(self):
        return "%s%s.%s%s.%s%s.%s%s"%tuple("%x"%self._mask)
