#!/usr/bin/env python

class SaveRTPPayload:

    #writeMode = 'timestamp'
    writeMode = 'append'

    def __init__(self, outfile):
        if self.writeMode == "append":
            if issubclass(type(outfile), basestring):
                outfile = open(outfile, 'w')
            self.fp = outfile
        else:
            self.out = []
        self.off = None
        self.startTimestamp = None


    def pkt(self, pktlen, data, timestamp):
        src_h, src_l = ord(data[0x22]), ord(data[0x23])
        dst_h, dst_l = ord(data[0x24]), ord(data[0x25])
        if self.startTimestamp is None:
            self.startTimestamp = timestamp
        if self.off is not None:
            offs = timestamp - self.off
            offs = (offs / 0.02) * 100
            if not ( 99 < offs < 101 ):
                warn = "XXXXX"
            else:
                warn = ""
            print "%.4f"%(timestamp-self.startTimestamp),pktlen, "%2.2f%%"%offs, src_h * 256 + src_l, "->", dst_h*256 + dst_l, warn
        else:
            print pktlen, timestamp, src_h*256+src_l, "->", dst_h*256+dst_l
        self.off = timestamp
        # IP/UDP header is 0x2A (42) bytes, RTP header is 0x0C (12) bytes
        # RTP payload starts at 0x36 (54).
        payload = data[0x36:]
        if self.writeMode == "append":
            self.fp.write(payload)

def main():
    import pcap, sys
    p = pcap.pcapObject()
    out = SaveRTPPayload('out.ul')
    p.open_offline(sys.argv[1])
    p.setfilter(sys.argv[2], 0, 0)
    p.loop(100000, out.pkt)


main()
