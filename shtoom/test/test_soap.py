# Copyright (C) 2004 Anthony Baxter
"""Tests for shtoom.soapsucks
"""

from twisted.trial import unittest

class SoapTests(unittest.TestCase):

    def test_soaprequest(self):
        from shtoom.soapsucks import SOAPRequestFactory, BeautifulSax
        ae = self.assertEquals
        schema = "urn:schemas-upnp-org:service:WANIPConnection:1"
        s = SOAPRequestFactory('http://127.0.0.1:5533/', schema)
        request = s.GetGenericPortMappingEntry(NewPortMappingIndex=12)

        for k, v in request.headers.items():
            if k.lower() == 'soapaction':
                ae(v, '"%s#GetGenericPortMappingEntry"'%schema)
        body = request.get_data()
        bs = BeautifulSax(body)
        meth = bs.fetch('u:GetGenericPortMappingEntry')
        ae(len(meth), 1)
        meth = meth[0]
        ae(meth['xmlns:u'], schema)
        # strip stupid whitespace text nodes
        meth.contents = [ x for x in meth.contents if str(x).strip() ]
        ae(len(meth.contents), 1)
        m = meth.contents[0]
        ae(m.name, 'NewPortMappingIndex')
        ae(len(m.contents), 1)
        ae(str(m.contents[0]),'12')

        request = s.GetTotallyBogusRequest(a='hello',b='goodbye',c=None)
        for k, v in request.headers.items():
            if k.lower() == 'soapaction':
                ae(v, '"%s#GetTotallyBogusRequest"'%schema)
        body = request.get_data()
        bs = BeautifulSax(body)
        meth = bs.fetch('u:GetTotallyBogusRequest')
        ae(len(meth), 1)
        meth = meth[0]
        ae(meth['xmlns:u'], schema)
        # strip stupid whitespace text nodes
        meth.contents = [ x for x in meth.contents if str(x).strip() ]
        ae(len(meth.contents), 3)
        for m in meth.contents:
            # Argument ordering doesn't matter
            if m.name == 'a':
                ae(len(m.contents), 1)
                ae(str(m.contents[0]),'hello')
            elif m.name == 'b':
                ae(len(m.contents), 1)
                ae(str(m.contents[0]),'goodbye')
            elif m.name == 'c':
                ae(len(m.contents), 0)
            else:
                # XXX
                ae('test failed', '%s not one of a,b,c'%(m.name))
        ae(request.get_host(), '127.0.0.1:5533')

    def test_soap_scpd(self):
        from shtoom.soapsucks import SOAPRequestFactory, BeautifulSax
        ae = self.assertEquals
        ar = self.assertRaises
        schema = "urn:schemas-upnp-org:service:WANIPConnection:1"
        soap = SOAPRequestFactory('http://127.0.0.1:5533/', schema)
        soap.setSCPD(canned_scpd)
        request = soap.GetGenericPortMappingEntry(NewPortMappingIndex=12)
        for k, v in request.headers.items():
            if k.lower() == 'soapaction':
                ae(v, '"%s#GetGenericPortMappingEntry"'%schema)
        body = request.get_data()
        bs = BeautifulSax(body)
        meth = bs.fetch('u:GetGenericPortMappingEntry')
        ae(len(meth), 1)
        meth = meth[0]
        ae(meth['xmlns:u'], schema)
        # strip stupid whitespace text nodes
        meth.contents = [ x for x in meth.contents if str(x).strip() ]
        ae(len(meth.contents), 1)
        m = meth.contents[0]
        ae(m.name, 'NewPortMappingIndex')
        ae(len(m.contents), 1)
        ae(str(m.contents[0]),'12')

        ar(NameError, soap.GetNonExistentMethod, )
        ar(TypeError, soap.GetGenericPortMappingEntry, a=1, b=2)
        ar(TypeError, soap.GetGenericPortMappingEntry,
                                                NewPortMappingIndex=1, b=2)
        # XXX Type checking not coded yet
        #ar(ValueError, soap.GetGenericPortMappingEntry,
        #                                     NewPortMappingIndex='abcd')

        # XXX required arg checking not coded yet
        #ar(TypeError, lambda : soap.GetGenericPortMappingEntry())

        # XXX allowed values checking not coded yet
        #ar(ValueError, soap.DeletePortMapping,
        #          NewRemoteHost=None, NewExternalPort=1234, NewProtocol='IP')

        # XXX int bounds checking not coded yet
        #ar(ValueError, soap.DeletePortMapping,
        #          NewRemoteHost=None, NewExternalPort=-1, NewProtocol='UDP')



canned_scpd = """<?xml version="1.0"?>
<scpd xmlns="urn:schemas-upnp-org:service-1-0">
<specVersion>
<major>1</major>
<minor>0</minor>
</specVersion>
<actionList>
<action>
<name>SetConnectionType</name>
<argumentList>
<argument>
<name>NewConnectionType</name>
<direction>in</direction>
<relatedStateVariable>ConnectionType</relatedStateVariable>
</argument>
</argumentList>
</action>
<action>
<name>GetConnectionTypeInfo</name>
<argumentList>
<argument>
<name>NewConnectionType</name>
<direction>out</direction>
<relatedStateVariable>ConnectionType</relatedStateVariable>
</argument>
<argument>
<name>NewPossibleConnectionTypes</name>
<direction>out</direction>
<relatedStateVariable>PossibleConnectionTypes</relatedStateVariable>
</argument>
</argumentList>
</action>
<action>
<name>RequestConnection</name>
</action>
<action>
<name>ForceTermination</name>
</action>
<action>
<name>GetStatusInfo</name>
<argumentList>
<argument>
<name>NewConnectionStatus</name>
<direction>out</direction>
<relatedStateVariable>ConnectionStatus</relatedStateVariable>
</argument>
<argument>
<name>NewLastConnectionError</name>
<direction>out</direction>
<relatedStateVariable>LastConnectionError</relatedStateVariable>
</argument>
<argument>
<name>NewUptime</name>
<direction>out</direction>
<relatedStateVariable>Uptime</relatedStateVariable>
</argument>
</argumentList>
</action>
<action>
<name>GetNATRSIPStatus</name>
<argumentList>
<argument>
<name>NewRSIPAvailable</name>
<direction>out</direction>
<relatedStateVariable>RSIPAvailable</relatedStateVariable>
</argument>
<argument>
<name>NewNATEnabled</name>
<direction>out</direction>
<relatedStateVariable>NATEnabled</relatedStateVariable>
</argument>
</argumentList>
</action>
<action>
<name>GetExternalIPAddress</name>
<argumentList>
<argument>
<name>NewExternalIPAddress</name>
<direction>out</direction>
<relatedStateVariable>ExternalIPAddress</relatedStateVariable>
</argument>
</argumentList>
</action>
<action>
<name>GetGenericPortMappingEntry</name>
<argumentList>
<argument>
<name>NewPortMappingIndex</name>
<direction>in</direction>
<relatedStateVariable>PortMappingNumberOfEntries</relatedStateVariable>
</argument>
<argument>
<name>NewRemoteHost</name>
<direction>out</direction>
<relatedStateVariable>RemoteHost</relatedStateVariable>
</argument>
<argument>
<name>NewExternalPort</name>
<direction>out</direction>
<relatedStateVariable>ExternalPort</relatedStateVariable>
</argument>
<argument>
<name>NewProtocol</name>
<direction>out</direction>
<relatedStateVariable>PortMappingProtocol</relatedStateVariable>
</argument>
<argument>
<name>NewInternalPort</name>
<direction>out</direction>
<relatedStateVariable>InternalPort</relatedStateVariable>
</argument>
<argument>
<name>NewInternalClient</name>
<direction>out</direction>
<relatedStateVariable>InternalClient</relatedStateVariable>
</argument>
<argument>
<name>NewEnabled</name>
<direction>out</direction>
<relatedStateVariable>PortMappingEnabled</relatedStateVariable>
</argument>
<argument>
<name>NewPortMappingDescription</name>
<direction>out</direction>
<relatedStateVariable>PortMappingDescription</relatedStateVariable>
</argument>
<argument>
<name>NewLeaseDuration</name>
<direction>out</direction>
<relatedStateVariable>PortMappingLeaseDuration</relatedStateVariable>
</argument>
</argumentList>
</action>
<action>
<name>GetSpecificPortMappingEntry</name>
<argumentList>
<argument>
<name>NewRemoteHost</name>
<direction>in</direction>
<relatedStateVariable>RemoteHost</relatedStateVariable>
</argument>
<argument>
<name>NewExternalPort</name>
<direction>in</direction>
<relatedStateVariable>ExternalPort</relatedStateVariable>
</argument>
<argument>
<name>NewProtocol</name>
<direction>in</direction>
<relatedStateVariable>PortMappingProtocol</relatedStateVariable>
</argument>
<argument>
<name>NewInternalPort</name>
<direction>out</direction>
<relatedStateVariable>InternalPort</relatedStateVariable>
</argument>
<argument>
<name>NewInternalClient</name>
<direction>out</direction>
<relatedStateVariable>InternalClient</relatedStateVariable>
</argument>
<argument>
<name>NewEnabled</name>
<direction>out</direction>
<relatedStateVariable>PortMappingEnabled</relatedStateVariable>
</argument>
<argument>
<name>NewPortMappingDescription</name>
<direction>out</direction>
<relatedStateVariable>PortMappingDescription</relatedStateVariable>
</argument>
<argument>
<name>NewLeaseDuration</name>
<direction>out</direction>
<relatedStateVariable>PortMappingLeaseDuration</relatedStateVariable>
</argument>
</argumentList>
</action>
<action>
<name>AddPortMapping</name>
<argumentList>
<argument>
<name>NewRemoteHost</name>
<direction>in</direction>
<relatedStateVariable>RemoteHost</relatedStateVariable>
</argument>
<argument>
<name>NewExternalPort</name>
<direction>in</direction>
<relatedStateVariable>ExternalPort</relatedStateVariable>
</argument>
<argument>
<name>NewProtocol</name>
<direction>in</direction>
<relatedStateVariable>PortMappingProtocol</relatedStateVariable>
</argument>
<argument>
<name>NewInternalPort</name>
<direction>in</direction>
<relatedStateVariable>InternalPort</relatedStateVariable>
</argument>
<argument>
<name>NewInternalClient</name>
<direction>in</direction>
<relatedStateVariable>InternalClient</relatedStateVariable>
</argument>
<argument>
<name>NewEnabled</name>
<direction>in</direction>
<relatedStateVariable>PortMappingEnabled</relatedStateVariable>
</argument>
<argument>
<name>NewPortMappingDescription</name>
<direction>in</direction>
<relatedStateVariable>PortMappingDescription</relatedStateVariable>
</argument>
<argument>
<name>NewLeaseDuration</name>
<direction>in</direction>
<relatedStateVariable>PortMappingLeaseDuration</relatedStateVariable>
</argument>
</argumentList>
</action>
<action>
<name>DeletePortMapping</name>
<argumentList>
<argument>
<name>NewRemoteHost</name>
<direction>in</direction>
<relatedStateVariable>RemoteHost</relatedStateVariable>
</argument>
<argument>
<name>NewExternalPort</name>
<direction>in</direction>
<relatedStateVariable>ExternalPort</relatedStateVariable>
</argument>
<argument>
<name>NewProtocol</name>
<direction>in</direction>
<relatedStateVariable>PortMappingProtocol</relatedStateVariable>
</argument>
</argumentList>
</action>
</actionList>
<serviceStateTable>
<stateVariable sendEvents="no">
<name>ConnectionType</name>
<dataType>string</dataType>
</stateVariable>
<stateVariable sendEvents="yes">
<name>PossibleConnectionTypes</name>
<dataType>string</dataType>
<allowedValueList>
<allowedValue>Unconfigured</allowedValue>
<allowedValue>IP_Routed</allowedValue>
<allowedValue>IP_Bridged</allowedValue>
</allowedValueList>
</stateVariable>
<stateVariable sendEvents="yes">
<name>ConnectionStatus</name>
<dataType>string</dataType>
<defaultValue>Unconfigured</defaultValue>
<allowedValueList>
<allowedValue>Unconfigured</allowedValue>
<allowedValue>Connected</allowedValue>
<allowedValue>Disconnected</allowedValue>
</allowedValueList>
</stateVariable>
<stateVariable sendEvents="no">
<name>Uptime</name>
<dataType>ui4</dataType>
</stateVariable>
<stateVariable sendEvents="no">
<name>LastConnectionError</name>
<dataType>string</dataType>
<allowedValueList>
<allowedValue>ERROR_NONE</allowedValue>
<allowedValue>ERROR_UNKNOWN</allowedValue>
</allowedValueList>
</stateVariable>
<stateVariable sendEvents="no">
<name>RSIPAvailable</name>
<dataType>boolean</dataType>
</stateVariable>
<stateVariable sendEvents="no">
<name>NATEnabled</name>
<dataType>boolean</dataType>
</stateVariable>
<stateVariable sendEvents="yes">
<name>ExternalIPAddress</name>
<dataType>string</dataType>
</stateVariable>
<stateVariable sendEvents="yes">
<name>PortMappingNumberOfEntries</name>
<dataType>ui2</dataType>
</stateVariable>
<stateVariable sendEvents="no">
<name>PortMappingEnabled</name>
<dataType>boolean</dataType>
</stateVariable>
<stateVariable sendEvents="no">
<name>PortMappingLeaseDuration</name>
<dataType>ui4</dataType>
</stateVariable>
<stateVariable sendEvents="no">
<name>RemoteHost</name>
<dataType>string</dataType>
</stateVariable>
<stateVariable sendEvents="no">
<name>ExternalPort</name>
<dataType>ui2</dataType>
</stateVariable>
<stateVariable sendEvents="no">
<name>InternalPort</name>
<dataType>ui2</dataType>
</stateVariable>
<stateVariable sendEvents="no">
<name>PortMappingProtocol</name>
<dataType>string</dataType>
<allowedValueList>
<allowedValue>TCP</allowedValue>
<allowedValue>UDP</allowedValue>
</allowedValueList>
</stateVariable>
<stateVariable sendEvents="no">
<name>InternalClient</name>
<dataType>string</dataType>
</stateVariable>
<stateVariable sendEvents="no">
<name>PortMappingDescription</name>
<dataType>string</dataType>
</stateVariable>
</serviceStateTable>
</scpd>
"""
