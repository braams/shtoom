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
	unsigned framesInBuffer = [audioBuffer count];
    unsigned framesInCount = ((*ioNumberFrames * inDescription.mBytesPerFrame) / inDescription.mChannelsPerFrame) / sizeof(Float32);
    unsigned framesInConversionBuffer = MTAudioBufferListFrameCount( conversionBufferList );
    
    printf("[%.0f - %.0f] ioNumberFrames = %d at (%d bytes per packet)\n", inDescription.mSampleRate, outDescription.mSampleRate, *ioNumberFrames, inDescription.mBytesPerPacket);
    printf("framesInBuffer = %d framesInCount = %d framesInConversionBuffer = %d\n", framesInBuffer, framesInCount, framesInConversionBuffer);
	unsigned framesToCopy = MIN ( framesInCount, MTAudioBufferListFrameCount ( conversionBufferList ) );
    printf("framesToCopy = %d\n", framesToCopy);
	// link the appropriate amount of data into the proto-AudioBufferList in ioData
	unsigned x;
	for ( x = 0; x < ioData->mNumberBuffers; x++ )
	{
        unsigned channelsThisBuffer;
		channelsThisBuffer = ioData->mBuffers[x].mNumberChannels;
        printf("channelsThisBuffer[%d] = %d\n", x, channelsThisBuffer);
		ioData->mBuffers[x].mDataByteSize = channelsThisBuffer * framesToCopy * sizeof(Float32);
		ioData->mBuffers[x].mData = conversionBufferList->mBuffers[x].mData;
        printf("ioData->mBuffers[x].mData = %08X\n", ioData->mBuffers[x].mData);
	}
	if ( framesInBuffer >= framesToCopy )
	{
		unsigned actuallyRead = [audioBuffer readToAudioBufferList:ioData maxFrames:framesToCopy waitForData:NO];
        printf("actuallyRead = %d\n", actuallyRead);
        if (actuallyRead != framesToCopy) {
            printf("MISMATCH! %d != %d\n", framesToCopy, actuallyRead);
        }
        unsigned numberCopied = (actuallyRead * sizeof(Float32) * ioData->mBuffers[0].mNumberChannels) / inDescription.mBytesPerFrame;
        printf("(actuallyRead * sizeof(Float32) * ioData->mBuffers[0].mNumberChannels) / inDescription.mBytesPerFrame = %d\n", numberCopied);
        *ioNumberFrames = numberCopied;
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

- (UInt32) numBufferFramesForSourceSampleRate:(Float64)srcRate sourceFrames:(UInt32)srcFrames effectiveDestinationFrames:(UInt32)effDstFrames
{
	// shouldn't be smaller than this, to accommodate imprecise/jittery sample rates and ioproc dispatching,
	// the combination of which can cause significant underrun+overrun distortion as the ioproc dispatches
	// come into and go out of phase
	return srcFrames + effDstFrames;
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
//    return [[[[[MTCoreAudioStreamDescription nativeStreamDescription] setSampleRate:[device nominalSampleRate]] setChannelsPerFrame:1] setIsInterleaved:NO] audioStreamBasicDescription];
    AudioStreamBasicDescription desc = [[[device streamDescriptionForChannel:0 forDirection:direction] setChannelsPerFrame:[device channelsForDirection:direction]] audioStreamBasicDescription];
    return desc;
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
    
    printf("[%.0f:%d:%d:%d -> %.0f:%d:%d:%d]\n", srcRate, srcChans, srcDescription.mBytesPerFrame, srcDescription.mBytesPerPacket, dstRate, dstChans, dstDescription.mBytesPerFrame, dstDescription.mBytesPerPacket);
    srcFrames = ((srcFrames * srcDescription.mBytesPerFrame) / srcChans) / sizeof(Float32);
    dstFrames = ((dstFrames * dstDescription.mBytesPerFrame) / dstChans) / sizeof(Float32);
    
	conversionFactor = srcRate / dstRate;
	effectiveDstFrames = ceil ( dstFrames * conversionFactor );
	totalBufferFrames = [self numBufferFramesForSourceSampleRate:srcRate sourceFrames:srcFrames effectiveDestinationFrames:effectiveDstFrames];	
	if ( srcRate != dstRate )
	{
		effectiveDstFrames += SRC_SLOP_FRAMES;
		totalBufferFrames += SRC_SLOP_FRAMES;
	}
	
    BOOL srcInterleaved = !(srcDescription.mFormatFlags & kAudioFormatFlagIsNonInterleaved);
    BOOL dstInterleaved = !(dstDescription.mFormatFlags & kAudioFormatFlagIsNonInterleaved);
    
	audioBuffer = [[MTAudioBuffer alloc] initWithCapacityFrames:totalBufferFrames channels:srcChans interleaved:srcInterleaved];
	if (( audioBuffer )
        && ( conversionBufferList = MTAudioBufferListNew ( srcChans, effectiveDstFrames, srcInterleaved))
        && ( outputBufferList     = MTAudioBufferListNew ( dstChans, dstFrames, dstInterleaved))
        && ( [self _initAudioConverterWithSourceDescription:srcDescription destinationDescription:dstDescription]  )
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
    OSStatus err;
    UInt32 uint32_property_size = sizeof(UInt32);

    UInt32 bytesAvailable = [audioBuffer count] * [audioBuffer channels] * sizeof(Float32);
    //UInt32 bytesAvailable = [audioBuffer count] * sizeof(Float32);
    UInt32 bytesAfterOutput = bytesAvailable;
    
    err = AudioConverterGetProperty(converter, kAudioConverterPropertyCalculateOutputBufferSize, &uint32_property_size, &bytesAfterOutput);
    if ( err != noErr ) {
        char errMsg[5];
        memcpy(errMsg, &err, sizeof(err));
        errMsg[4] = '\0';
        printf("AudioConverterGetProperty err %d ('%s')\n", err, errMsg);
        return 0;
    }
    
    if (bytesAfterOutput == 0) {
        printf("can not generate any output with a buffer size of %d bytes\n", bytesAvailable);
        return 0;
    }
    
    printf("dst frame count = %d mNumberBuffers = %d mBuffers[0].mNumberChannels = %d size = %d\n", MTAudioBufferListFrameCount(dst), dst->mNumberBuffers, dst->mBuffers[0].mNumberChannels, dst->mBuffers[0].mDataByteSize);
    printf("obl frame count = %d mNumberBuffers = %d mBuffers[0].mNumberChannels = %d size = %d\n", MTAudioBufferListFrameCount(outputBufferList), outputBufferList->mNumberBuffers, outputBufferList->mBuffers[0].mNumberChannels, outputBufferList->mBuffers[0].mDataByteSize);
    
    UInt32 maxOutputBytes = MIN ( MTAudioBufferListFrameCount(dst), MTAudioBufferListFrameCount(outputBufferList) ) * outDescription.mBytesPerPacket;

    printf("conversion of %d will yield %d (max = %d)\n", bytesAvailable, bytesAfterOutput, maxOutputBytes);
    
    UInt32 packetsToOutput = MIN( maxOutputBytes, bytesAfterOutput ) / outDescription.mBytesPerPacket;
    
    printf("will be asking for %d packets -> %d bytes at (%d bytes packet)\n", packetsToOutput, packetsToOutput * outDescription.mBytesPerPacket, outDescription.mBytesPerPacket);
    
    // backing up output ABL
    UInt32 outFrameCount = MTAudioBufferListFrameCount(outputBufferList);
    UInt32 numBuffers = outputBufferList->mNumberBuffers;
    AudioBuffer *bufBackup = calloc(numBuffers, sizeof(AudioBuffer));
    memcpy(bufBackup, outputBufferList->mBuffers, numBuffers * sizeof(AudioBuffer));
    
    UInt32 framesRead = packetsToOutput;
    
    err = AudioConverterFillComplexBuffer ( converter, _FillComplexBufferProc, self, &framesRead, outputBufferList, NULL );
	UInt32 floatFramesRead;
    if ( err != noErr )
	{
        char errMsg[5];
        memcpy(errMsg, &err, sizeof(err));
        errMsg[4] = '\0';
        printf("AudioConverterFillComplexBuffer err %d ('%s')\n", err, errMsg);
        floatFramesRead = 0;
    } else {
        /*
         if (outDescription.mFormatFlags & kLinearPCMFormatFlagIsFloat) {
             // XXX requires that outputBufferList is de-interleaved, which it should be
             UInt32 chan;
             for ( chan = 0; chan < outputChannels; chan++ )
             {
                 samples = outputBufferList->mBuffers[chan].mData;
                 vsmul ( samples, 1, &gainArray[chan], samples, 1, framesRead );
             }
         }
         */
        printf("-- real framesRead = %d\n", framesRead);
        floatFramesRead = ((framesRead * outDescription.mBytesPerFrame) / outDescription.mChannelsPerFrame) / sizeof(Float32);
		MTAudioBufferListCopy ( outputBufferList, 0, dst, 0, floatFramesRead );
	}
    UInt32 newFrameCount =  MTAudioBufferListFrameCount(outputBufferList);
    if (newFrameCount != outFrameCount) {
        printf("newFrameCount = %d outFrameCount = %d\n", newFrameCount, outFrameCount);
        memcpy(outputBufferList->mBuffers, bufBackup, numBuffers * sizeof(AudioBuffer));
    }
    free(bufBackup);
    printf("-- floatFramesRead = %d\n", floatFramesRead);
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
