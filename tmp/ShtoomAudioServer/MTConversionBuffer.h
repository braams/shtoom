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
#import <CoreAudio/CoreAudioTypes.h>

@interface MTConversionBuffer : NSObject {
	AudioConverterRef converter;
	AudioBufferList * conversionBufferList;
	AudioBufferList * outputBufferList;
	MTAudioBuffer * audioBuffer;
	Float32 * gainArray;
    AudioStreamBasicDescription inDescription;
    AudioStreamBasicDescription outDescription;    
}

+ (AudioStreamBasicDescription)descriptionForDevice:(MTCoreAudioDevice *)device forDirection:(MTCoreAudioDirection)direction;
- initWithSourceDescription:(AudioStreamBasicDescription)srcDescription bufferFrames:(UInt32)srcFrames destinationDescription:(AudioStreamBasicDescription)dstDescription bufferFrames:(UInt32)dstFrames;
- (void) setGain:(Float32)theGain forOutputChannel:(UInt32)theChannel;
- (Float32) gainForOutputChannel:(UInt32)theChannel;
- (unsigned) writeFromAudioBufferList:(const AudioBufferList *)src timestamp:(const AudioTimeStamp *)timestamp;
- (unsigned) readToAudioBufferList:(AudioBufferList *)dst timestamp:(const AudioTimeStamp *)timestamp;

// subclasses may override this method to change the size of the converter's buffer
- (UInt32) numBufferFramesForSourceSampleRate:(Float64)srcRate sourceFrames:(UInt32)srcFrames effectiveDestinationFrames:(UInt32)effDstFrames;

@end
