//
//  MTConversionBuffer.m
//  AudioMonitor
//
//  Created by Michael Thornburgh on Wed Jul 09 2003.
//  Copyright (c) 2004 Michael Thornburgh. All rights reserved.
//

#import "MTConversionBuffer.h"
#import <math.h>
#import <string.h>
#import <vecLib/vecLib.h>

#define SRC_SLOP_FRAMES 8
#define SR_ERROR_ALLOWANCE 1.01 // 1%

@interface MTConversionBuffer (MTConversionBufferPrivateMethods)
- (OSStatus) _fillComplexBuffer:(AudioBufferList *)ioData countPointer:(UInt32 *)ioNumberFrames;
@end


static OSStatus _FillComplexBufferProc (
	AudioConverterRef aConveter,
	UInt32 * ioNumberDataPackets,
	AudioBufferList * ioData,
	AudioStreamPacketDescription ** outDataPacketDescription,
	void * inUserData
)
{
	MTConversionBuffer * theBuffer = inUserData;
	
	return [theBuffer _fillComplexBuffer:ioData countPointer:ioNumberDataPackets];
}


@implementation MTConversionBuffer ( MTConversionBufferPrivateMethods )

- (OSStatus) _fillComplexBuffer:(AudioBufferList *)ioData countPointer:(UInt32 *)ioNumberFrames
{
	unsigned x;
	unsigned channelsThisBuffer;
	unsigned framesToCopy;
	unsigned framesInBuffer = [audioBuffer count];
	
	framesToCopy = MIN ( *ioNumberFrames, MTAudioBufferListFrameCount ( conversionBufferList ));
	*ioNumberFrames = framesToCopy;
	// link the appropriate amount of data into the proto-AudioBufferList in ioData
	for ( x = 0; x < ioData->mNumberBuffers; x++ )
	{
		channelsThisBuffer = ioData->mBuffers[x].mNumberChannels;
		ioData->mBuffers[x].mDataByteSize = channelsThisBuffer * framesToCopy * sizeof(Float32);
		ioData->mBuffers[x].mData = conversionBufferList->mBuffers[x].mData;
	}
	if ( framesInBuffer >= framesToCopy )
	{
		[audioBuffer readToAudioBufferList:ioData maxFrames:framesToCopy waitForData:NO];
	}
	else
	{
        // DEBUG_PRINT_JUNK
		printf ( "underrun: ask: %u  queued: %u  provided: 0\n", framesToCopy, framesInBuffer );
        *ioNumberFrames = 0;
        return 'NDTA';
	}
	return noErr;
}

@end


@implementation MTConversionBuffer

- (Boolean) _initGainArray
{
	unsigned chan;
	unsigned numChannels = MTAudioBufferListChannelCount(outputBufferList);
	
	gainArray = malloc ( numChannels * sizeof(Float32));
	if ( NULL == gainArray )
		return FALSE;
	
	for ( chan = 0; chan < numChannels; chan++ )
	{
		gainArray[chan] = 1.0;
	}
	return TRUE;
}

- (Boolean) _initAudioConverterWithSourceSampleRate:(Float64)srcRate channels:(UInt32)srcChans destinationSampleRate:(Float64)dstRate channels:(UInt32)dstChans
{
	UInt32 primeMethod, srcQuality;
	UInt32 * channelMap;
		
	inDescription  = [[[[[MTCoreAudioStreamDescription nativeStreamDescription] setSampleRate:srcRate] setChannelsPerFrame:srcChans] setIsInterleaved:NO] audioStreamBasicDescription];
	outDescription = [[[[[MTCoreAudioStreamDescription nativeStreamDescription] setSampleRate:dstRate] setChannelsPerFrame:dstChans] setIsInterleaved:NO] audioStreamBasicDescription];
	
	if ( noErr != AudioConverterNew ( &inDescription, &outDescription, &converter ))
	{
		converter = NULL; // just in case
		return FALSE;
	}
	
	primeMethod = kConverterPrimeMethod_None;
	srcQuality = kAudioConverterQuality_Max;
	
	(void) AudioConverterSetProperty ( converter, kAudioConverterPrimeMethod, sizeof(UInt32), &primeMethod );
	(void) AudioConverterSetProperty ( converter, kAudioConverterSampleRateConverterQuality, sizeof(UInt32), &srcQuality );
	
	// if the input is mono, try to route to all channels.
	if (( 1 == srcChans ) && ( dstChans > srcChans ))
	{
		// trick.  The Channel is 0, so we just use calloc() to get an array of zeros.  :)
		channelMap = calloc ( dstChans, sizeof(UInt32));
		if ( channelMap )
		{
			(void) AudioConverterSetProperty ( converter, kAudioConverterChannelMap, dstChans * sizeof(UInt32), channelMap );
			free ( channelMap );
		}
	}
	
	return TRUE;
}

- (UInt32) numBufferFramesForSourceSampleRate:(Float64)srcRate sourceFrames:(UInt32)srcFrames effectiveDestinationFrames:(UInt32)effDstFrames
{
	// shouldn't be smaller than this, to accommodate imprecise/jittery sample rates and ioproc dispatching,
	// the combination of which can cause significant underrun+overrun distortion as the ioproc dispatches
	// come into and go out of phase
	return srcFrames + effDstFrames;
}

- initWithSourceSampleRate:(Float64)srcRate channels:(UInt32)srcChans bufferFrames:(UInt32)srcFrames destinationSampleRate:(Float64)dstRate channels:(UInt32)dstChans bufferFrames:(UInt32)dstFrames
{
	double conversionFactor;
	UInt32 effectiveDstFrames;
	UInt32 totalBufferFrames;
	UInt32 conversionChannels;
	
	[super init];

	conversionFactor = srcRate / dstRate;
	effectiveDstFrames = ceil ( dstFrames * conversionFactor );
	totalBufferFrames = [self numBufferFramesForSourceSampleRate:srcRate sourceFrames:srcFrames effectiveDestinationFrames:effectiveDstFrames];	
	if ( srcRate != dstRate )
	{
		effectiveDstFrames += SRC_SLOP_FRAMES;
		totalBufferFrames += SRC_SLOP_FRAMES;
	}
	
	conversionChannels = MIN ( srcChans, dstChans );
	
	audioBuffer = [[MTAudioBuffer alloc] initWithCapacityFrames:totalBufferFrames channels:conversionChannels];
	if (( audioBuffer )
	 && ( conversionBufferList = MTAudioBufferListNew ( conversionChannels, effectiveDstFrames, NO ))
	 && ( outputBufferList     = MTAudioBufferListNew ( dstChans, dstFrames, NO ))
	 && ( [self _initAudioConverterWithSourceSampleRate:srcRate channels:conversionChannels destinationSampleRate:dstRate channels:dstChans]  )
	 && ( [self _initGainArray] ))
	{
		return self;
	}
	else
	{
		[self dealloc];
		return nil;
	}
}

- (Boolean) _initAudioConverterWithSourceDescription:(AudioStreamBasicDescription)inputDescription destinationDescription:(AudioStreamBasicDescription)outputDescription
{
	UInt32 primeMethod, srcQuality;
	UInt32 * channelMap;
    UInt32 srcChans = inputDescription.mChannelsPerFrame;
    UInt32 dstChans = outputDescription.mChannelsPerFrame;

    inDescription = inputDescription;
    outDescription = outputDescription;
    
	if ( noErr != AudioConverterNew ( &inDescription, &outDescription, &converter ))
	{
		converter = NULL; // just in case
		return FALSE;
	}
	
	primeMethod = kConverterPrimeMethod_None;
	srcQuality = kAudioConverterQuality_Max;
	
	(void) AudioConverterSetProperty ( converter, kAudioConverterPrimeMethod, sizeof(UInt32), &primeMethod );
	(void) AudioConverterSetProperty ( converter, kAudioConverterSampleRateConverterQuality, sizeof(UInt32), &srcQuality );
	
	// if the input is mono, try to route to all channels.
	if (( 1 == srcChans ) && ( dstChans > srcChans ))
	{
		// trick.  The Channel is 0, so we just use calloc() to get an array of zeros.  :)
		channelMap = calloc ( dstChans, sizeof(UInt32));
		if ( channelMap )
		{
			(void) AudioConverterSetProperty ( converter, kAudioConverterChannelMap, dstChans * sizeof(UInt32), channelMap );
			free ( channelMap );
		}
	}
	
	return TRUE;
}

+ (AudioStreamBasicDescription)descriptionForDevice:(MTCoreAudioDevice *)device forDirection:(MTCoreAudioDirection)direction
{
    return [[[device streamDescriptionForChannel:0 forDirection:direction] setChannelsPerFrame:[device channelsForDirection:direction]] audioStreamBasicDescription];
}


- initWithSourceDescription:(AudioStreamBasicDescription)srcDescription bufferFrames:(UInt32)srcFrames destinationDescription:(AudioStreamBasicDescription)dstDescription bufferFrames:(UInt32)dstFrames
{
	double conversionFactor;
	UInt32 effectiveDstFrames;
	UInt32 totalBufferFrames;
	UInt32 conversionChannels;
	
	self = [super init];

    UInt32 srcChans = srcDescription.mChannelsPerFrame;
    UInt32 dstChans = dstDescription.mChannelsPerFrame;
    double srcRate = srcDescription.mSampleRate;
    double dstRate = dstDescription.mSampleRate;
    
	conversionFactor = srcRate / dstRate;
	effectiveDstFrames = ceil ( dstFrames * conversionFactor );
	totalBufferFrames = [self numBufferFramesForSourceSampleRate:srcRate sourceFrames:srcFrames effectiveDestinationFrames:effectiveDstFrames];	
	if ( srcRate != dstRate )
	{
		effectiveDstFrames += SRC_SLOP_FRAMES;
		totalBufferFrames += SRC_SLOP_FRAMES;
	}
	
	conversionChannels = MIN ( srcChans, dstChans );
	
	audioBuffer = [[MTAudioBuffer alloc] initWithCapacityFrames:totalBufferFrames channels:conversionChannels];
	if (( audioBuffer )
        && ( conversionBufferList = MTAudioBufferListNew ( conversionChannels, effectiveDstFrames, NO ))
        && ( outputBufferList     = MTAudioBufferListNew ( dstChans, dstFrames, NO ))
        && ( [self _initAudioConverterWithSourceSampleRate:srcRate channels:conversionChannels destinationSampleRate:dstRate channels:dstChans]  )
        && ( [self _initGainArray] ))
	{
		return self;
	}
	else
	{
		[self dealloc];
		return nil;
	}
}

- (Boolean) _verifyDeviceIsCanonicalFormat:(MTCoreAudioDevice *)theDevice inDirection:(MTCoreAudioDirection)theDirection
{
	NSEnumerator * streamEnumerator = [[theDevice streamsForDirection:theDirection] objectEnumerator];
	MTCoreAudioStream * aStream;
	
	while ( aStream = [streamEnumerator nextObject] )
	{
		if ( ! [[aStream streamDescriptionForSide:kMTCoreAudioStreamLogicalSide] isCanonicalFormat] )
		{
			return FALSE;
		}
	}
	
	return TRUE;
}

- initWithSourceDevice:(MTCoreAudioDevice *)inputDevice destinationDevice:(MTCoreAudioDevice *)outputDevice
{
	if ( [self _verifyDeviceIsCanonicalFormat:inputDevice inDirection:kMTCoreAudioDeviceRecordDirection]
	  && [self _verifyDeviceIsCanonicalFormat:outputDevice inDirection:kMTCoreAudioDevicePlaybackDirection] )
	{
		self = [self
			initWithSourceSampleRate:[inputDevice nominalSampleRate]
			channels:                [inputDevice channelsForDirection:kMTCoreAudioDeviceRecordDirection]
			bufferFrames:            ceil ( [inputDevice deviceMaxVariableBufferSizeInFrames] * SR_ERROR_ALLOWANCE )
			destinationSampleRate:   [outputDevice nominalSampleRate]
			channels:                [outputDevice channelsForDirection:kMTCoreAudioDevicePlaybackDirection]
			bufferFrames:            ceil ( [outputDevice deviceMaxVariableBufferSizeInFrames] * SR_ERROR_ALLOWANCE )
		];
		return self;
	}
	else
	{
		[self dealloc];
		return nil;
	}
}

- (void) setGain:(Float32)theGain forOutputChannel:(UInt32)theChannel
{
	if ( theChannel < MTAudioBufferListChannelCount(outputBufferList))
	{
		gainArray[theChannel] = theGain;
	}
}

- (Float32) gainForOutputChannel:(UInt32)theChannel
{
	if ( theChannel < MTAudioBufferListChannelCount(outputBufferList) )
	{
		return gainArray[theChannel];
	}
	else
	{
		return 0.0;
	}
}


- (Float64) _fudgeFactorFromTimeStamp:(const AudioTimeStamp *)timestamp
{
	Float64 rv;
	
	if ( timestamp && ( timestamp->mFlags & kAudioTimeStampRateScalarValid ))
		rv = timestamp->mRateScalar;
	else
		rv = 1.0;
	
	if ( rv > SR_ERROR_ALLOWANCE )
		rv = SR_ERROR_ALLOWANCE;
	else if ( rv < ( 1.0 / SR_ERROR_ALLOWANCE ))
		rv = ( 1.0 / SR_ERROR_ALLOWANCE );
	
	return rv;
}

- (unsigned) writeFromAudioBufferList:(const AudioBufferList *)src timestamp:(const AudioTimeStamp *)timestamp
{
	unsigned framesRequested, framesQueued;
	Float64 rateScalar = [self _fudgeFactorFromTimeStamp:timestamp];
	
	framesRequested = MTAudioBufferListFrameCount ( src );
	framesQueued = [audioBuffer writeFromAudioBufferList:src maxFrames:framesRequested rateScalar:rateScalar waitForRoom:NO];
	if ( framesQueued != framesRequested ) {
        // DEBUG_PRINT_JUNK
		printf ( "overrun: %u frames queued: %u frames factor: %f  queue factor: %f\n", framesRequested - framesQueued, framesQueued, rateScalar, [audioBuffer rateScalar] );
    }
    return framesQueued;
}

- (unsigned) readToAudioBufferList:(AudioBufferList *)dst timestamp:(const AudioTimeStamp *)timestamp
{
    UInt32 dstFrameCount = MTAudioBufferListFrameCount(dst);
    UInt32 outFrameCount = MTAudioBufferListFrameCount(outputBufferList);
	UInt32 framesToRead = MIN ( dstFrameCount, outFrameCount );
	UInt32 chan, outputChannels;
	Float32 * samples;
	UInt32 framesRead;
		
	outputChannels = MTAudioBufferListChannelCount(outputBufferList);
	framesRead = framesToRead;
    
    UInt32 inputSize = [audioBuffer count] * sizeof(Float32);
    UInt32 inputPropSize = sizeof(UInt32);
    OSStatus err;

    err = AudioConverterGetProperty(converter, kAudioConverterPropertyCalculateOutputBufferSize, &inputPropSize, &inputSize);
    if ( err != noErr ) {
        char errMsg[5];
        errMsg[5] = '\0';
        memcpy(errMsg, &err, sizeof(err));
        printf("AudioConverterGetProperty err %d ('%s')\n", err, errMsg);
        return 0;
    }
    framesRead = MIN ( framesToRead, inputSize / sizeof(Float32) );
    printf("framesToRead = %d framesRead = %d dstFrameCount = %d outFrameCount = %d\n", framesToRead, framesRead, dstFrameCount, outFrameCount);
    
    if (framesRead == 0) {
        // printf("readToAudioBufferList -- empty!\n");
        return 0;
    }
    
    UInt32 numBuffers = outputBufferList->mNumberBuffers;
    AudioBuffer *bufBackup = calloc(numBuffers, sizeof(AudioBuffer));
    memcpy(bufBackup, outputBufferList->mBuffers, numBuffers * sizeof(AudioBuffer));
    
    err = AudioConverterFillComplexBuffer ( converter, _FillComplexBufferProc, self, &framesRead, outputBufferList, NULL );
	if ( err == noErr )
	{
		// XXX requires that outputBufferList is de-interleaved, which it should be
        if (outDescription.mFormatFlags & kLinearPCMFormatFlagIsFloat) {
            for ( chan = 0; chan < outputChannels; chan++ )
            {
                samples = outputBufferList->mBuffers[chan].mData;
                vsmul ( samples, 1, &gainArray[chan], samples, 1, framesRead );
            }
        }
		MTAudioBufferListCopy ( outputBufferList, 0, dst, 0, framesRead );
	} else {
        char errMsg[5];
        errMsg[5] = '\0';
        memcpy(errMsg, &err, sizeof(err));
        printf("AudioConverterFillComplexBuffer err %d ('%s')\n", err, errMsg);
    }
    UInt32 newFrameCount =  MTAudioBufferListFrameCount(outputBufferList);
    if (newFrameCount != outFrameCount) {
        printf("newFrameCount = %d\n", newFrameCount);
        memcpy(outputBufferList->mBuffers, bufBackup, numBuffers * sizeof(AudioBuffer));
    }
    free(bufBackup);
    return framesRead;
}

- (void) dealloc
{
	if ( converter )
		AudioConverterDispose ( converter );
	MTAudioBufferListDispose ( conversionBufferList );
	MTAudioBufferListDispose ( outputBufferList );
	[audioBuffer release];
	if ( gainArray )
		free ( gainArray );
	[super dealloc];
}

@end
