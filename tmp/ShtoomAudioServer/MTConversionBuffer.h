//
//  MTConversionBuffer.h
//  AudioMonitor
//
//  Created by Michael Thornburgh on Wed Jul 09 2003.
//  Copyright (c) 2004 Michael Thornburgh. All rights reserved.
//

#import <Foundation/Foundation.h>
#import <MTCoreAudio/MTCoreAudio.h>
#import <AudioToolbox/AudioToolbox.h>

@interface MTConversionBuffer : NSObject {
	AudioConverterRef converter;
	AudioBufferList * conversionBufferList;
	AudioBufferList * outputBufferList;
	MTAudioBuffer * audioBuffer;
	Float32 * gainArray;
}

- initWithSourceDevice:(MTCoreAudioDevice *)inputDevice destinationDevice:(MTCoreAudioDevice *)outputDevice;
- initWithSourceSampleRate:(Float64)srcRate channels:(UInt32)srcChans bufferFrames:(UInt32)srcFrames destinationSampleRate:(Float64)dstRate channels:(UInt32)dstChans bufferFrames:(UInt32)dstFrames;
- (void) setGain:(Float32)theGain forOutputChannel:(UInt32)theChannel;
- (Float32) gainForOutputChannel:(UInt32)theChannel;
- (void) writeFromAudioBufferList:(const AudioBufferList *)src timestamp:(const AudioTimeStamp *)timestamp;
- (void) readToAudioBufferList:(AudioBufferList *)dst timestamp:(const AudioTimeStamp *)timestamp;
// - (void) setInterpolation:(Boolean)flag forDirection:(MTCoreAudioDirection)theDirection;
// - (Boolean) shouldInterpolateForDirection:(MTCoreAudioDirection)theDirection;

// subclasses may override this method to change the size of the converter's buffer
- (UInt32) numBufferFramesForSourceSampleRate:(Float64)srcRate sourceFrames:(UInt32)srcFrames effectiveDestinationFrames:(UInt32)effDstFrames;

@end
