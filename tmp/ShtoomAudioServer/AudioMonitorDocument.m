//
//  AudioMonitorDocument.m
//  AudioMonitor
//
//  Created by Michael Thornburgh on Thu Oct 03 2002.
//  Copyright (c) 2003 Michael Thornburgh. All rights reserved.
//

#import "AudioMonitorDocument.h"
#import "MTAudioDeviceBrowser.h"
#import "MTConversionBuffer.h"
#import <math.h>
#import <fcntl.h>

static double _db_to_scalar ( Float32 decibels )
{
	return pow ( 10.0, decibels / 20.0 );
}

#define SHTOOM_BUFFER_SIZE 16384

@implementation AudioMonitorDocument

 - init
{
    self = [super init];
    sockdesc = socket(AF_INET, SOCK_DGRAM, IPPROTO_UDP);
    if (sockdesc == -1) {
        NSLog(@"bad socket!?");
    }
    sa_self.sin_family = sa_other.sin_family = AF_INET;
    sa_self.sin_addr.s_addr = sa_other.sin_addr.s_addr = htonl(INADDR_LOOPBACK);
    sa_self.sin_port = htons(SHTOOM_SERVER_LISTEN);
    sa_other.sin_port = htons(SHTOOM_SERVER_SEND);
    const int optOn = 1;
    if (setsockopt(sockdesc, SOL_SOCKET, SO_REUSEPORT, &optOn, sizeof(optOn)) == -1) {
        NSLog(@"couldn't reuse port");
    }
    if (setsockopt(sockdesc, SOL_SOCKET, SO_REUSEADDR, &optOn, sizeof(optOn)) == -1) {
        NSLog(@"couldn't reuse addr");
    }
    if (fcntl(sockdesc, F_SETFL, O_NONBLOCK) == -1) {
        NSLog(@"couldn't set nonblocking");
    }
    if (bind(sockdesc, (struct sockaddr*)&sa_self, sizeof(sa_self)) == -1) {
        NSLog(@"couldn't bind listening socket?!");
    }

    
    inBuffer.mNumberBuffers = 1;
    inBuffer.mBuffers[0].mNumberChannels = 1;
    inBuffer.mBuffers[0].mDataByteSize = SHTOOM_BUFFER_SIZE;
    inBuffer.mBuffers[0].mData = malloc(SHTOOM_BUFFER_SIZE);
    outBuffer.mNumberBuffers = 1;
    outBuffer.mBuffers[0].mNumberChannels = 1;
    outBuffer.mBuffers[0].mDataByteSize = SHTOOM_BUFFER_SIZE;
    outBuffer.mBuffers[0].mData = malloc(SHTOOM_BUFFER_SIZE);
    return self;
}

- (NSString *)displayName
{
	return @"Audio Monitor";
}

- (NSString *)windowNibName
{
	return @"AudioMonitorDocument";
}

- (void)windowControllerDidLoadNib:(NSWindowController *) aController
{
	[super windowControllerDidLoadNib:aController];
	
	[self setAdjustVolume:adjustLeftSlider];
	[self setAdjustVolume:adjustRightSlider];
	[recordDeviceBrowser setDirection:kMTCoreAudioDeviceRecordDirection];
	[playbackDeviceBrowser setDirection:kMTCoreAudioDevicePlaybackDirection];
	[[aController window] setFrameAutosaveName:@"Audio Monitor"];
}

- (NSData *)dataRepresentationOfType:(NSString *)aType
{
	return nil;
}

- (BOOL)loadDataRepresentation:(NSData *)data ofType:(NSString *)aType
{
	return YES;
}

// ------------------- ioTarget methods ---------------
- (OSStatus) recordIOForDevice:(MTCoreAudioDevice *)theDevice timeStamp:(const AudioTimeStamp *)inNow inputData:(const AudioBufferList *)inInputData inputTime:(const AudioTimeStamp *)inInputTime outputData:(AudioBufferList *)outOutputData outputTime:(const AudioTimeStamp *)inOutputTime clientData:(void *)inClientData
{
    [outconverter writeFromAudioBufferList:inInputData timestamp:inInputTime];
    return noErr;
}

- (OSStatus) playbackIOForDevice:(MTCoreAudioDevice *)theDevice timeStamp:(const AudioTimeStamp *)inNow inputData:(const AudioBufferList *)inInputData inputTime:(const AudioTimeStamp *)inInputTime outputData:(AudioBufferList *)outOutputData outputTime:(const AudioTimeStamp *)inOutputTime clientData:(void *)inClientData
{
	[inconverter readToAudioBufferList:outOutputData timestamp:inOutputTime];
	return noErr;
}
// ----------------------------------


- (void) MTAudioDeviceBrowser:(MTAudioDeviceBrowser *)theBrowser selectedDeviceDidChange:(MTCoreAudioDevice *)newDevice
{
	MTCoreAudioDevice ** whichDevice;
	SEL whichSelector;
	
	if ( theBrowser == recordDeviceBrowser )
	{
		whichDevice = &inputDevice;
		whichSelector = @selector(recordIOForDevice:timeStamp:inputData:inputTime:outputData:outputTime:clientData:);
	}
	else if ( theBrowser == playbackDeviceBrowser )
	{
		whichDevice = &outputDevice;
		whichSelector = @selector(playbackIOForDevice:timeStamp:inputData:inputTime:outputData:outputTime:clientData:);
	}
	else
		return;
	
	[*whichDevice release];
	*whichDevice = newDevice;
	
	[newDevice retain];
	[newDevice setDelegate:self];
	[newDevice setIOTarget:self withSelector:whichSelector withClientData:nil];
	[self playthroughButton:playthroughButton];
}

#ifndef SR_ERROR_ALLOWANCE
#define SR_ERROR_ALLOWANCE 1.01 // 1%
#endif

- (void) allocNewConverter
{
	[inconverter release];
	//inconverter = [[MTConversionBuffer alloc] initWithSourceDevice:inputDevice destinationDevice:outputDevice];
	inconverter = [[MTConversionBuffer alloc]
        initWithSourceSampleRate:8000
                        channels:1 
//                    bufferFrames:ceil( 50 * SR_ERROR_ALLOWANCE )
                    bufferFrames:ceil ( [outputDevice deviceMaxVariableBufferSizeInFrames] * SR_ERROR_ALLOWANCE )
           destinationSampleRate:[outputDevice nominalSampleRate] 
                        channels:[outputDevice channelsForDirection:kMTCoreAudioDevicePlaybackDirection] 
                    bufferFrames:ceil ( [outputDevice deviceMaxVariableBufferSizeInFrames] * SR_ERROR_ALLOWANCE )];
	[inconverter setGain:adjustLeft forOutputChannel:0];
	[inconverter setGain:adjustRight forOutputChannel:1];
	[outconverter release];
	outconverter = [[MTConversionBuffer alloc]
        initWithSourceSampleRate:[inputDevice nominalSampleRate]
                        channels:[inputDevice channelsForDirection:kMTCoreAudioDeviceRecordDirection]
                    bufferFrames:ceil ( [inputDevice deviceMaxVariableBufferSizeInFrames] * SR_ERROR_ALLOWANCE )
           destinationSampleRate:8000
                        channels:1
                    //bufferFrames:ceil ( 50 * SR_ERROR_ALLOWANCE )];
                    bufferFrames:ceil ( [inputDevice deviceMaxVariableBufferSizeInFrames] * SR_ERROR_ALLOWANCE )];
	[outconverter setGain:adjustLeft forOutputChannel:0];
	[outconverter setGain:adjustRight forOutputChannel:1];
}

- (void) pumpNetBuffers:(NSTimer *)aTimer
{
    [outconverter readToAudioBufferList:&outBuffer timestamp:NULL];
    int size = outBuffer.mBuffers[0].mDataByteSize;
    void *data = outBuffer.mBuffers[0].mData;
    void *end = data + size;
    int sentbytes = 1;
    while (sentbytes > 0 && data != end) {
        sentbytes = sendto(sockdesc, data, MIN(320, end - data), 0, (struct sockaddr*)&sa_other, sizeof(sa_other));
        if (sentbytes > 0) {
            data += sentbytes;
        }
    }
    size = inBuffer.mBuffers[0].mDataByteSize;
    data = inBuffer.mBuffers[0].mData;
    int addrlen = sizeof(sa_self);
    int cnt = 0;
    int recvbytes = 1;
    while (recvbytes > 0) {
        recvbytes = recvfrom(sockdesc, data, size, 0, (struct sockaddr*)&sa_self, &addrlen);
        NSLog(@"recvbytes: %d\n", recvbytes);
        cnt += 1;
    }
    NSLog(@"-------------- cnt = %d", cnt);
}

- (void) playthroughButton:(id)sender
{
	if ([sender state])
	{
		[inputDevice  setDevicePaused:YES];  // lock out IO cycles while we change a resource they use
		[outputDevice setDevicePaused:YES];
		[self allocNewConverter];
		[outputDevice setDevicePaused:NO];
		[inputDevice  setDevicePaused:NO];
		
		if ( ! ( [outputDevice deviceStart] && [inputDevice deviceStart] ))
		{
			[sender setState:FALSE];
			[self playthroughButton:sender];
		} else {
            NSLog(@"netTimer created");
            netTimer = [[NSTimer scheduledTimerWithTimeInterval:(1.0/8000.0)*50 target:self selector:@selector(pumpNetBuffers:) userInfo:nil repeats:YES] retain];
        }
	}
	else
	{
		[inputDevice  deviceStop];
		[outputDevice deviceStop];
        [netTimer invalidate];
        [netTimer release];
        netTimer = nil;
	}
}

- (void) setAdjustVolume:(id)sender
{
	double * whichAdjust;
	id whichLabel;
	UInt32 whichChannel;
	
	if (sender == adjustLeftSlider)
	{
		whichLabel = adjustLeftLabel;
		whichAdjust = &adjustLeft;
		whichChannel = 0;
	}
	else
	{
		whichLabel = adjustRightLabel;
		whichAdjust = &adjustRight;
		whichChannel = 1;
	}
	
	[whichLabel setFloatValue:[sender floatValue]];
	*whichAdjust = _db_to_scalar ( [sender floatValue] );
	[inconverter setGain:*whichAdjust forOutputChannel:whichChannel];
}

- (void) audioDeviceDidOverload:(MTCoreAudioDevice *)theDevice
{
	NSLog ( @"overload: %@", [theDevice deviceUID] );
}

- (void) audioDeviceStartDidFail:(MTCoreAudioDevice *)theDevice forReason:(OSStatus)theReason
{
	NSLog ( @"device:%@ start failed, reason:%4.4s\n", [theDevice deviceUID], (char *)&theReason );
}

- (void) audioDeviceBufferSizeInFramesDidChange:sender
{
	[self playthroughButton:playthroughButton];
}

- (void) audioDeviceNominalSampleRateDidChange:sender
{
	[self playthroughButton:playthroughButton];
}

- (void) audioDeviceStreamsListDidChange:theDevice
{
	[self playthroughButton:playthroughButton];
}

- (void) audioDeviceChannelsByStreamDidChange:(MTCoreAudioDevice *)theDevice forDirection:(MTCoreAudioDirection)theDirection
{
	if ((( theDevice == inputDevice ) && ( theDirection == kMTCoreAudioDeviceRecordDirection )) ||
	    (( theDevice == outputDevice ) && ( theDirection == kMTCoreAudioDevicePlaybackDirection )))
	{
		[self playthroughButton:playthroughButton];
	}
}

- (void) dealloc
{
    close(sockdesc);
    free(outBuffer.mBuffers[0].mData);
    free(inBuffer.mBuffers[0].mData);
    [netTimer invalidate];
    [netTimer release];
	[inputDevice release];
	[outputDevice release];
	[inconverter release];
    [outconverter release];
	
	[super dealloc];
}

@end
