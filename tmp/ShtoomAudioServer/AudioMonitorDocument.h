//
//  AudioMonitorDocument.h
//  AudioMonitor
//
//  Created by Michael Thornburgh on Thu Oct 03 2002.
//  Copyright (c) 2003 Michael Thornburgh. All rights reserved.
//


#import <Cocoa/Cocoa.h>
#import <MTCoreAudio/MTCoreAudio.h>
#import <CoreAudio/CoreAudio.h>
#import <AudioToolbox/AudioToolbox.h>

@class MTConversionBuffer;

@interface AudioMonitorDocument : NSDocument
{
	id adjustLeftSlider;
	id adjustLeftLabel;
	id adjustRightSlider;
	id adjustRightLabel;
	id playthroughButton;
	id recordDeviceBrowser;
	id playbackDeviceBrowser;
	
	MTCoreAudioDevice * inputDevice;
	MTCoreAudioDevice * outputDevice;
	MTConversionBuffer * inConverter;
    MTConversionBuffer * outConverter;
    
    AudioConverterRef inAudioConverter;
    AudioConverterRef outAudioConverter;

	double adjustLeft;
	double adjustRight;
    
    AudioBufferList *inBuffer;
    AudioBufferList *outBuffer;
    NSInputStream *inputStream;
    NSOutputStream *outputStream;
    NSMutableData *receiveQueue;
    NSMutableArray *sendQueue;
}

- (void) sendDataFromConverter:(MTConversionBuffer *)converter;
- (void) _sendDataFromConverter:(MTConversionBuffer *)converter;
- (void) flushDataForConverter:(MTConversionBuffer *)converter;
- (void) _flushDataForConverter:(MTConversionBuffer *)converter;
- (void) startNetworkQueues;
- (void) stopNetworkQueues;
- (void) streamReadyToRead:(NSInputStream *)s;
- (void) streamReadyToWrite:(NSOutputStream *)s;
- (void) playthroughButton:(id)sender;
- (void) setAdjustVolume:(id)sender;

@end
