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
#import <sys/socket.h>
#import <arpa/inet.h>
#import <netinet/in.h>
#import <fcntl.h>

#define SHTOOM_FREQUENCY 8000
#define SHTOOM_NETBUFFER_LENGTH 4096
#define SHTOOM_PORT 22000
#ifndef SR_ERROR_ALLOWANCE
#define SR_ERROR_ALLOWANCE 1.01 // 1%
#endif

static double _db_to_scalar ( Float32 decibels )
{
	return pow ( 10.0, decibels / 20.0 );
}

@implementation AudioMonitorDocument

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
    /*
    unsigned framesQueued = [outConverter writeFromAudioBufferList:inInputData timestamp:inInputTime];
    printf("queuedFramesToConverter = %d\n", framesQueued);
    NSAutoreleasePool *pool = [[NSAutoreleasePool alloc] init];
    [self performSelectorOnMainThread:@selector(sendDataFromConverter:) withObject:nil waitUntilDone:NO];
    [pool release];
    */
    
    return noErr;
}

- (OSStatus) playbackIOForDevice:(MTCoreAudioDevice *)theDevice timeStamp:(const AudioTimeStamp *)inNow inputData:(const AudioBufferList *)inInputData inputTime:(const AudioTimeStamp *)inInputTime outputData:(AudioBufferList *)outOutputData outputTime:(const AudioTimeStamp *)inOutputTime clientData:(void *)inClientData
{
    unsigned framesRead = [inConverter readToAudioBufferList:outOutputData timestamp:inOutputTime];
    printf("readFramesFromConverter = %d\n", framesRead);
    
    NSAutoreleasePool *pool = [[NSAutoreleasePool alloc] init];
    [self performSelectorOnMainThread:@selector(flushDataForConverter:) withObject:nil waitUntilDone:NO];
    [pool release];

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

- (void) allocNewConverter
{
    Float64 inScale = (SHTOOM_FREQUENCY / [outputDevice nominalSampleRate]);
    unsigned inBufferSize = ceil ( inScale * [outputDevice deviceMaxVariableBufferSizeInFrames] * SR_ERROR_ALLOWANCE );
    if (inBuffer) MTAudioBufferListDispose(inBuffer);
    inBuffer = MTAudioBufferListNew(1, inBufferSize, NO);
    printf("inBufferSize = %d\n", inBufferSize);
    
    AudioStreamBasicDescription shtoomDescription;
    shtoomDescription.mSampleRate = SHTOOM_FREQUENCY;
    shtoomDescription.mFormatID = kAudioFormatLinearPCM;
    shtoomDescription.mFormatFlags = kLinearPCMFormatFlagIsPacked | kLinearPCMFormatFlagIsSignedInteger | kLinearPCMFormatFlagIsBigEndian | kAudioFormatFlagIsNonInterleaved;
    shtoomDescription.mBytesPerFrame = sizeof(SInt16);
    shtoomDescription.mFramesPerPacket = 1;
    shtoomDescription.mBytesPerPacket = sizeof(SInt16);
    shtoomDescription.mChannelsPerFrame = 1;
    shtoomDescription.mBitsPerChannel = 16;
    shtoomDescription.mReserved = 0;
        
	[inConverter release];
	inConverter = [[MTConversionBuffer alloc]
        initWithSourceDescription:shtoomDescription 
                     bufferFrames:inBufferSize 
           destinationDescription:[MTConversionBuffer descriptionForDevice:outputDevice forDirection:kMTCoreAudioDevicePlaybackDirection]
                     bufferFrames:ceil ( [outputDevice deviceMaxVariableBufferSizeInFrames] * SR_ERROR_ALLOWANCE )];

	[inConverter setGain:adjustLeft forOutputChannel:0];
	[inConverter setGain:adjustRight forOutputChannel:1];

    Float64 outScale = (SHTOOM_FREQUENCY / [inputDevice nominalSampleRate]);
    unsigned outBufferSize = ceil ( outScale * [inputDevice deviceMaxVariableBufferSizeInFrames] * SR_ERROR_ALLOWANCE );
    if (outBuffer) MTAudioBufferListDispose(outBuffer);
    outBuffer = MTAudioBufferListNew(1, outBufferSize, NO);
    printf("outBufferSize = %d\n", outBufferSize);
    
    [outConverter release];
	outConverter = [[MTConversionBuffer alloc]
        initWithSourceDescription:[MTConversionBuffer descriptionForDevice:inputDevice forDirection:kMTCoreAudioDeviceRecordDirection]
                     bufferFrames:outBufferSize 
           destinationDescription:shtoomDescription
                     bufferFrames:ceil ( [outputDevice deviceMaxVariableBufferSizeInFrames] * SR_ERROR_ALLOWANCE )];
    
	
	[outConverter setGain:adjustLeft forOutputChannel:0];
	[outConverter setGain:adjustRight forOutputChannel:1];
        
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
            [self startNetworkQueues];
        }
	}
	else
	{
		[inputDevice  deviceStop];
		[outputDevice deviceStop];
        [self stopNetworkQueues];
	}
}

- (void) sendDataFromConverter:(MTConversionBuffer *)converter
{
    @try {
        if (!converter) converter = outConverter;
        [self _sendDataFromConverter:converter];
    }
    @catch (NSException *exception) {
        NSLog(@"sendDataFromConverter: caught %@: %@", [exception name], [exception reason]);
    }
}

- (void) _sendDataFromConverter:(MTConversionBuffer *)converter
{
    AudioBuffer *buffer = outBuffer->mBuffers;
    while (1) {
        unsigned frames = [converter readToAudioBufferList:outBuffer timestamp:NULL];
        if (frames == 0) {
            //printf("no frames!\n");
            break;
        }
        NSMutableData *dataContainer = [NSMutableData dataWithBytes:buffer->mData length:(frames * sizeof(Float32))];
        [sendQueue addObject:dataContainer];
    }
    [self streamReadyToWrite:outputStream];
}

- (void) flushDataForConverter:(MTConversionBuffer *)converter
{
    @try {
        if (!converter) converter = inConverter;
        [self _flushDataForConverter:converter];
    }
    @catch (NSException *exception) {
        NSLog(@"flushDataForConverter: caught %@: %@", [exception name], [exception reason]);
    }
}

- (void) _flushDataForConverter:(MTConversionBuffer *)converter
{
    // empty queue
    if ([receiveQueue count] == 0) return;
    AudioBufferList myList;
    myList.mNumberBuffers = 1;
    AudioBuffer *buffer = myList.mBuffers;
    buffer->mNumberChannels = 1;
    NSMutableData *allData = [NSMutableData dataWithCapacity:SHTOOM_NETBUFFER_LENGTH];
    NSEnumerator *queueEnumerator = [receiveQueue objectEnumerator];
    NSData *data;
    while ((data = [queueEnumerator nextObject]) != nil) {
        [allData appendData:data];
    }
    
    [receiveQueue removeAllObjects];
    unsigned data_length = [allData length];
    unsigned slop_bytes = data_length % sizeof(Float32);

    /*
    static Float32 period = 0.0;
    unsigned i;
    Float32 curPeriod = period;
    Float32 incPeriod = ((M_PI * 2) * 440.0) / 8000.0;
    SInt16 *outBytes = (SInt16 *)[allData mutableBytes];
    for (i=0; i<(data_length / sizeof(SInt16)); i++) {
        outBytes[i] = (SInt16)(SHRT_MAX * sinf(curPeriod));
        curPeriod += incPeriod;
    }
    */
            
    buffer->mDataByteSize = data_length - slop_bytes;
    buffer->mData = (void *)[allData bytes];
    unsigned bytesRead = [converter writeFromAudioBufferList:&myList timestamp:NULL] * sizeof(Float32);
    //period += (incPeriod * bytesRead) / sizeof(SInt16);
    unsigned leftInBuffer = [allData length] - bytesRead;
    printf("bytesRead = %d leftInBuffer = %d slop_bytes=%d\n", bytesRead, [allData length] - bytesRead, slop_bytes);
    if (leftInBuffer > 0) {
        [receiveQueue addObject:[NSData dataWithBytes:[allData bytes]+bytesRead length:leftInBuffer]];
    }
}

- (void) streamReadyToRead:(NSInputStream *)s
{
    if (receiveQueue == nil) return;

    NSMutableData *inDataContainer = [NSMutableData dataWithCapacity:SHTOOM_NETBUFFER_LENGTH];
    [inDataContainer setLength:SHTOOM_NETBUFFER_LENGTH];
    SInt16 *inData = (SInt16 *)[inDataContainer mutableBytes];
    unsigned len = [s read:(uint8_t *)inData maxLength:[inDataContainer length]];
    if (len == 0) return;
    [inDataContainer setLength:len];
    
    [receiveQueue addObject:inDataContainer];
    [self flushDataForConverter:inConverter];
}

- (void) streamReadyToWrite:(NSOutputStream *)s
{
    if (sendQueue == nil) return;
    
    while ([sendQueue count] > 0) {
        NSMutableData *data = [sendQueue objectAtIndex:0];
        int dataLength = [data length];
        int bytesWritten = [s write:(const uint8_t *)[data bytes] maxLength:dataLength];
        if (bytesWritten <= 0) {
            break;
        } else if (bytesWritten < dataLength) {
            [sendQueue replaceObjectAtIndex:0 withObject:[NSData dataWithBytes:[data bytes]+bytesWritten length:dataLength-bytesWritten]];
            break;
        } else {            
            [sendQueue removeObjectAtIndex:0];
        }
    }
}

- (void) startNetworkQueues
{
    [self stopNetworkQueues];
    [NSStream getStreamsToHost:[NSHost hostWithAddress:@"127.0.0.1"] port:SHTOOM_PORT inputStream:&inputStream outputStream:&outputStream];
    [inputStream retain];
    [inputStream setDelegate:self];
    [inputStream scheduleInRunLoop:[NSRunLoop currentRunLoop] forMode:(NSString *)kCFRunLoopCommonModes];
    [inputStream open];
    [outputStream retain];
    [outputStream setDelegate:self];
    [outputStream scheduleInRunLoop:[NSRunLoop currentRunLoop] forMode:(NSString *)kCFRunLoopCommonModes];
    [outputStream open];
}

- (void) stream:(NSStream *)stream handleEvent:(NSStreamEvent)streamEvent
{
    if (streamEvent & NSStreamEventOpenCompleted) {
        if ([stream isEqualTo:outputStream]) sendQueue = [[NSMutableArray alloc] init];
        if ([stream isEqualTo:inputStream])  receiveQueue = [[NSMutableArray alloc] init];
    }
    if (streamEvent & NSStreamEventHasBytesAvailable) {
        [self streamReadyToRead:inputStream];
    }
    if (streamEvent & NSStreamEventHasSpaceAvailable) {
        [self streamReadyToWrite:outputStream];
    }
    if (streamEvent & NSStreamEventErrorOccurred) {
        NSLog(@"stream error: %@", [stream streamError]);
        [self stopNetworkQueues];
    }
    if (streamEvent & NSStreamEventEndEncountered) {
        NSLog(@"stream end encountered");
        [self stopNetworkQueues];
    }
}

- (void) stopNetworkQueues
{
    [inputStream close];
    [inputStream release];
    inputStream = nil;
    [outputStream close];
    [outputStream release];
    outputStream = nil;
    [sendQueue release];
    sendQueue = nil;
    [receiveQueue release];
    receiveQueue = nil;
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
	[inConverter setGain:*whichAdjust forOutputChannel:whichChannel];
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
    if (inAudioConverter) AudioConverterDispose(inAudioConverter);
    if (outAudioConverter) AudioConverterDispose(outAudioConverter);
    if (inBuffer) MTAudioBufferListDispose(inBuffer);
    if (outBuffer) MTAudioBufferListDispose(outBuffer);    
    [self stopNetworkQueues];
	[inputDevice release];
	[outputDevice release];
	[inConverter release];
    [outConverter release];
	
	[super dealloc];
}

@end
