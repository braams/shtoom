/*
 *  SampleUnit.cpp
 *  ShtoomAudioServer
 *
 *  Created by Bob Ippolito on 11/4/04.
 *  Copyright 2004 __MyCompanyName__. All rights reserved.
 *
 */

#include "SampleUnit.h"

#include <CoreServices/CoreServices.h>
#include <stdio.h>
#include <unistd.h>
#include <AudioUnit/AudioUnit.h>

#include <math.h>


AudioUnit	gOutputUnit;
AudioStreamBasicDescription gStreamFormat;

UInt32 sampleNextPrinted = 0;

void RenderSin (UInt32 				startingFrameCount, 
				UInt32 				inFrames, 
				void*				inBuffer, 
				double 				inSampleRate, 
				double 				amplitude, 
				double 				frequency) 
{
	double j = startingFrameCount;
	double cycleLength = inSampleRate / frequency;
    SInt16* sbuffer = (SInt16*)inBuffer;
    
	// mNumberBuffers is the same as the kNumChannels
	
    UInt32 frame;
	for (frame = 0; frame < inFrames; ++frame) 
	{
		// generate inFrames 32-bit floats
		Float32 nextFloat = sin(j / cycleLength * (M_PI * 2.0)) * amplitude;
        sbuffer[frame] = (SInt16)(nextFloat * 32768. + 0.5);		
		j += 1.0;
		if (j > cycleLength)
			j -= cycleLength;
	}
    	
	if (startingFrameCount >= sampleNextPrinted) {
		printf ("Current Slice: inFrames=%ld, startingFrameCount=%ld\n", inFrames, startingFrameCount);
		sampleNextPrinted += (int)inSampleRate;
	}
}


UInt32 sSinWaveFrameCount;


OSStatus	MyRenderer(void 				*inRefCon, 
                       AudioUnitRenderActionFlags 	*ioActionFlags, 
                       const AudioTimeStamp 		*inTimeStamp, 
                       UInt32 						inBusNumber, 
                       UInt32 						inNumberFrames, 
                       AudioBufferList 			*ioData)

{
	RenderSin (sSinWaveFrameCount, 
               inNumberFrames,  
               ioData->mBuffers[0].mData, 
               gStreamFormat.mSampleRate, 
               0.25, 
               440.);
    
	sSinWaveFrameCount += inNumberFrames;
    
	return noErr;
}

// ________________________________________________________________________________
//
// CreateDefaultAU
//
void	CreateDefaultAU()
{
	OSStatus err = noErr;
    
	// Open the default output unit
	ComponentDescription desc;
	desc.componentType = kAudioUnitType_Output;
	desc.componentSubType = kAudioUnitSubType_DefaultOutput;
	desc.componentManufacturer = kAudioUnitManufacturer_Apple;
	desc.componentFlags = 0;
	desc.componentFlagsMask = 0;
	
	Component comp = FindNextComponent(NULL, &desc);
	if (comp == NULL) { printf ("FindNextComponent\n"); return; }
	
	err = OpenAComponent(comp, &gOutputUnit);
	if (comp == NULL) { printf ("OpenAComponent=%ld\n", err); return; }
    
	// Set up a callback function to generate output to the output unit
    AURenderCallbackStruct input;
	input.inputProc = MyRenderer;
	input.inputProcRefCon = NULL;
    
	err = AudioUnitSetProperty (gOutputUnit, 
								kAudioUnitProperty_SetRenderCallback, 
								kAudioUnitScope_Input,
								0, 
								&input, 
								sizeof(input));
	if (err) { printf ("AudioUnitSetProperty-CB=%ld\n", err); return; }
    
}


// ________________________________________________________________________________
//
// TestDefaultAU
//
void	TestDefaultAU()
{
	OSStatus err = noErr;
    
	// We tell the Output Unit what format we're going to supply data to it
	// this is necessary if you're providing data through an input callback
	// AND you want the DefaultOutputUnit to do any format conversions
	// necessary from your format to the device's format.
    gStreamFormat.mSampleRate = 8000;
    gStreamFormat.mFormatID = kAudioFormatLinearPCM;
    gStreamFormat.mFormatFlags = (kLinearPCMFormatFlagIsSignedInteger 
                                 | kLinearPCMFormatFlagIsBigEndian
                                 | kLinearPCMFormatFlagIsPacked
                                 | kAudioFormatFlagIsNonInterleaved);
    gStreamFormat.mBytesPerPacket = 2;	
    gStreamFormat.mFramesPerPacket = 1;	
    gStreamFormat.mBytesPerFrame = 2;		
    gStreamFormat.mChannelsPerFrame = 1;	
    gStreamFormat.mBitsPerChannel = 16;	
    
	err = AudioUnitSetProperty (gOutputUnit,
                                kAudioUnitProperty_StreamFormat,
                                kAudioUnitScope_Input,
                                0,
                                &gStreamFormat,
                                sizeof(AudioStreamBasicDescription));
	if (err) { printf ("AudioUnitSetProperty-SF=%4.4s, %ld\n", (char*)&err, err); return; }
	
    // Initialize unit
	err = AudioUnitInitialize(gOutputUnit);
	if (err) { printf ("AudioUnitInitialize=%ld\n", err); return; }
    
	Float64 outSampleRate;
	UInt32 size = sizeof(Float64);
	err = AudioUnitGetProperty (gOutputUnit,
                                kAudioUnitProperty_SampleRate,
                                kAudioUnitScope_Output,
                                0,
                                &outSampleRate,
                                &size);
	if (err) { printf ("AudioUnitSetProperty-GF=%4.4s, %ld\n", (char*)&err, err); return; }
    
	// Start the rendering
	// The DefaultOutputUnit will do any format conversions to the format of the default device
	err = AudioOutputUnitStart (gOutputUnit);
	if (err) { printf ("AudioOutputUnitStart=%ld\n", err); return; }
    
    // RUNS FOREVER!!!!
    // we call the CFRunLoopRunInMode to service any notifications that the audio
    // system has to deal with
	usleep (5 * 1000 * 1000); // sleep for 5 seconds
    
    // REALLY after you're finished playing STOP THE AUDIO OUTPUT UNIT!!!!!!	
    // but we never get here because we're running until the process is nuked...	
	verify_noerr (AudioOutputUnitStop (gOutputUnit));
	
    err = AudioUnitUninitialize (gOutputUnit);
	if (err) { printf ("AudioUnitUninitialize=%ld\n", err); return; }
}

void CloseDefaultAU ()
{
	// Clean up
	CloseComponent (gOutputUnit);
}

// ________________________________________________________________________________
//
// TestDefaultAU
//
int main(int argc, const char * argv[])
{
    CreateDefaultAU();
    TestDefaultAU();
    CloseDefaultAU();
    
    return 0;
}
