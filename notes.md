# Notes

## SSL

Using proper SSL (2048 but private key) was wildly slow, like 4 seconds of TLS Setup slow
Using a 512 bit private key brings it down to 750-900 ms

## I2C

Assuming this is being built for the rp2040 (Can see if changes are needed to support 2350 later)

Currently this will not have support for software i2c(bit-banged) meaning two channels are available

Have an option to select how many channels will be used

## SHT4X 

Should have configuration for the different precision modes, not going to worry about the heater

Can only have one per channel without adding an i2c multiplexer

## OLED screen

Resolution and channel need to be set

## Thermistor

There are 4 available ADC channels on the rp2040 (as with i2c I can see if that changes for the 2350)

Up to 4 thermistors can be used

## PWM Fan Control

Current plan gives 4 level shifted channels meaning up to 4 independently controlled channels

## Configuration options

1.  How many i2c channels
2.  Which i2c pins for which channel - Maybe not worth adding if the intention is to develop a pcb
3.  i2c frequency and timeout - Not sure if I want this changeable
4.  Network hostname
5.  Static IP address - Not sure if that is useful
6.  SHT4X mode
7.  SHT4x number
8.  SHT4x i2c channel
9.  OLED resolution
10. OLED i2c channel
11. Number of thermistors
12. Thermistor ADC Pin - per thermistor
13. Thermistor config - per thermistor
    1. nominal temp
    2. b coefficient
    3. nominal resistance
    4. external (reference) resistance
14. Number of fans
15. Pin of fan - per fan
16. Fan temperature reference - per fan
17. Fan curve definition - per fan
    1. Zero/low RPM Mode
    2. Minimum temp
    3. Maximum temp
    4. Fan curve shape

## Webpage stuff

HTML/ website stuff is probably not optimized
Originally I was loading the entire HTML/CSS/JS etc file into memory and writing it
This would fairly frequently throw memory errors so changing this to stream all but very small HTML
as small ~.5Kb chunks