//
//  AudioMonitorDocument.h
//  AudioMonitor
//
//  Created by Michael Thornburgh on Thu Oct 03 2002.
//  Copyright (c) 2003 Michael Thornburgh. All rights reserved.
//


#import <Cocoa/Cocoa.h>
#import <MTCoreAudio/MTCoreAudio.h>

#import <arpa/inet.h>
#import <netinet/in.h>
#import <stdio.h>
#import <sys/types.h>
#import <sys/socket.h>
#import <unistd.h>

@class MTConversionBuffer;

#define SHTOOM_SERVER_SEND 21000
#define SHTOOM_SERVER_LISTEN 21001

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
	MTConversionBuffer * inconverter;
    MTConversionBuffer * outconverter;

	double adjustLeft;
	double adjustRight;
    
    NSTimer *netTimer;
    AudioBufferList inBuffer;
    AudioBufferList outBuffer;
    struct sockaddr_in sa_self, sa_other;
    int sockdesc;
    
}

- (void) pumpNetBuffers:(NSTimer *)aTimer;
- (void) playthroughButton:(id)sender;
- (void) setAdjustVolume:(id)sender;
@end
