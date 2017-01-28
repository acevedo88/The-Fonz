#!/usr/bin/python
#
#The Fonz, a friendly passive scanner for finding out which pin is being used for a TouchTunes (Gen 2 and above) wireless remote.
#TouchTunes remotes TX at 433.92Mhz, uses ASK/OOK and uses a pin (000-255) for "security". 
#This script was meant to be used with RfCat and the Yard Stick One.

#Here's an example of what the transmission looks like (in hex), on/off button with the PIN 000 
#==Preamble==  ==Key==  ==Message== ==?==
#ffff00a2888a2   aaaa   8888aa2aa22  20

#And the on/off button with PIN 255
#==Preamble==  ==Key==  ==Message== ==?==
#ffff00a2888a2 22222222 8888aa2aa22  20

#The message sometimes changes with the key but the key will be same regardless of the button pressed.  
#Here's an example of the on/off button with the pin 001
#==Preamble==  ==Key==  ==Message== ==?==
#ffff00a2888a2  2aaa    a2222a8aa88   88


#Based off of Michael Osman's code. https://greatscottgadgets.com/
#rflib and vstruct pulled from https://github.com/ecc1/rfcat
#Written by NotPike, Twitter @pyfurry


from rflib import *
import datetime


banner = """  _____ _            _____               
 |_   _| |__   ___  |  ___|__  _ __  ____
   | | | '_ \ / _ \ | |_ / _ \| '_ \|_  /
   | | | | | |  __/ |  _| (_) | | | |/ / 
   |_| |_| |_|\___| |_|  \___/|_| |_/___| V0.3

          "A Frindly Passive Scanner"
              Hit <ENTER> to exit\n"""

CliHelp = ''' '''


###the ID Vender and ID Product of the YSO, used to restart if libusb fails
##from usb.core import find as finddev
##dev = finddev(idVendor=0x1d50, idProduct=0x605b)
##dev.reset() 


#The D lol
d = RfCat()


#Values(keys) for each PIN, in order (000-255) when they are transited.
#ex. nukecode[0] ==  PIN 000, nukecode[50] == PIN 050, and nukecode[255] == PIN 255   
nukecodes = ['aaaa', '2aaa', '8aaa', '22aaa', 'a2aa', '28aaa', '88aaa', '222aa', '222aa', '2a2aa',
           '8a2aa', '228aa', 'a22aa', '288aa', '888aa', '2222aa', 'aa2a', '2a8aa', '8a8aa', '22a2a',
           'a28aa', '28a2a', '88a2a', '2228aa', 'a88aa', '2a22a', '8a22a', '2288aa', 'a222a', '2888aa',
           '8888aa', '22222a', 'aa8aa', '2aa2a', '8aa2a', '22a8a', 'a2a2a', '28a8a', '88a8a', '222a2a',
           'a8a2a', '2a28a', '8a28a', '228a2a', 'a228a', '288a2a', '888a2a', '22228a', 'aa22a', '2a88a',
           '8a88a', '22a22', 'a288a', '28a22a', '88a22a', '22288a', 'a888a', '2a222a', '8a222a', '22888a',
           'a2222a', '28888a', '88888a', '222222a', 'aaa2a', '2aa8a', '8aa8a', '22aa2', 'a2a8a', '28aa2',
           '88aa2', '222a8a', 'a8a8a', '2a2a2', '8a2a2', '228a8a', 'a22a2', '288a8a', '888a8a', '2222a2',
           'aa28a', '2a8a2', '8a8a2', '22a28a', 'a28a2', '28a28a', '88a28a', '2228a2', 'a88a2', '2a228a',
           '8a228a', '2288a2', 'a2228a', '2888a2', '8888a2', '222228a', 'aa88a', '2aa22', '8aa22', '22a88a',
           'a2a22', '28a88a', '88a88a', '222a22', 'a8a22', '2a288a', '8a288a', '228a22', 'a2288a', '288a22',
           '888a22', '222288', 'aa222', '2a888a', '8a888a', '22a222', 'a2888a', '28a222', '88a222', '222888a',
           'a8888a', '2a2222', '8a2222', '228888a', 'a22222', '288888a', '888888a', '2222222', 'aaa8', '2aaa2',
           '8aaa2', '22aa8', 'a2aa2', '28aa8', '88aa8', '222aa2', 'a8aa2', '2a2a8', '8a2a8', '228aa2', 'a22a8',
           '288aa2', '888aa2', '2222a8', 'aa2a2', '2a8a8', '8a8a8', '22a2a2', 'a28a8', '28a2a2', '88a2a2', '2228a8',
           'a88a8', '2a22a2', '8a22a2', '2288a8', 'a222a2', '2888a8', '8888a8', '22222a2', 'aa8a2', '2aa28', '8aa28',
           '22a8a2', 'a2a28', '28a8a2', '88a8a2', '222a28', 'a8a28', '2a28a2', '8a28a2', '228a28', 'a228a2', '288a28',
           '888a28', '22228a2', 'aa228', '2a88a2', '8a88a2', '22a228', 'a288a2', '28a228', '88a228', '22288a2',
           'a888a2', '2a2228', '8a2228', '22888a2', 'a22228', '28888a2', '88888a2', '2222228', 'aaa22', '2aa88',
           '8aa88', '22aa22', 'a2a88', '28aa22', '88aa22', '222a88', 'a8a88', '2a2a22', '8a2a22', '228a88', 'a22a22',
           '288a88', '888a88', '2222a22', 'aa288', '2a8a22', '8a8a22', '22a288', 'a28a22', '28a288', '88a288',
           '2228a22', 'a88a22', '2a2288', '8a2288', '2288a22', 'a22288', 'a28a22', '8888a22', '2222288', 'aa888',
           '2aa222', '8aa222', '22a888', 'a2a222', '28a888', '88a888', '222a222', 'a8a222', '2a2888', '8a2888',
           '228a222', 'a22888', '288a222', '888a222', '2222888', 'aa2222', '2a8888', '8a8888', '22a2222', 'a28888',
           '28a2222', '88a2222', '2228888', 'a88888', '2a22222', '8a22222', '2288888', 'a222222', '2888888',
           '8888888', '22222222']


#Both command values for each button
#Two Values for each command, it switches back and forth for each Key used 
commands = {'On_Off': ['8888aa2aa22200','a2222a8aa88880'], 'Pause': ['a22a288a88a200','a88a8a22a22880'],
        'P1': ['888aa8aa222200','a222aa2a888880'], 'P2_Edit_Queue': ['88aaa2a2222200', 'a22aa8a8888880'],
        'P3_Skip': ['22a28aa228a200','88a8a2a88a2880'], 'F1_Restart': ['a2aa88a2222200','a8aaa228888880'],
        'F2_Key': ['28aaa8a2222200','8a2aaa28888880'], 'F3_Mic_A_Mute': ['a22aa22a222200','a88aa88a888880'],
        'F4_Mic_B_Mute': ['288aaa2a222200','8a22aa8a888880'], 'Mic_Vol_Plus_Up_Arrow': ['2222a2aa88a200','8888a8aaa22880'],
        'Mic_Vol_Minus_Down_Arrow': ['2aaaa222222200','8aaaa888888880'], 'A_Left_Arrow': ['2aa2a8888a2200','8aa8aa22228880'],
        'B_Right_Arrow': ['22a8aa888a2200','88aa2aa2228880'], 'OK': ['8aa2a2888a2200','a2a8a8a2228880'],
        'Music_Vol_Zone_1Up': ['228aaa8a222200','88a2aaa2888880'], 'Music_Vol_Zone_1Down': ['8a2aa28a222200','a28aa8a2888880'],
        'Music_Vol_Zone_2Up': ['2a2aa88a222200','8a8aaa22888880'], 'Music_Vol_Zone_2Down': ['a8aa888a222200','aa2aa222888880'],
        'Music_Vol_Zone_3Up': ['22aaaa22222200','88aaaa88888880'], 'Music_Vol_Zone_3Down': ['8aaa8a22222200','a2aaa288888880'],
        '1': ['2222aaaa222200','8888aaaa888880'], '2': ['aa2a8888a22200','aa8aa222288880'], '3': ['2a8aa888a22200','8aa2aa22288880'],
        '4': ['8a8aa288a22200','a2a2a8a2288880'], '5': ['22a2aa88a22200','88a8aaa2288880'], '6': ['a28aa228a22200','a8a2a88a288880'],
        '7': ['28a2aa28a22200','8a28aa8a288880'], '8': ['88a2a8a8a22200','a228aa2a288880'], '9': ['2228aaa8a22200','888a2aaa288880'],
        '0': ['2a22aa22a22200','8a88aa88a88880'], 'Music_Karaoke': ['a88aa222a22200','aa22a888a88880'],
        'Lock_Queue': ['8a22a8a2a22200','a288aa28a88880']} 


#Checks to see the packet receaved is valid
#looks for the preamble FFFF00A2888A2
#FFFF is cut off by d.setMdmSyncWord()
def VerifyPkt(pkt): 
        if ord(pkt[0]) != 0x00:
                return False
        if ord(pkt[1]) != 0xa2:
                return False
        if ord(pkt[2]) != 0x88:
                return False
        if ord(pkt[3]) != 0x8A:
                return False
        return True


#finds what the PIN is in a captured packet, not perfict because it may return mutable pins.
#TODO improve regex pattern so only 1 pin is returned
def PinFind(pkt):
        packet = str(pkt.encode('hex'))
        pin = 0
        pins = [] #
        for nuke in nukecodes:
                PreNuke = '00a2888a2'+nuke #preamble plus the key
                if re.search(PreNuke, packet):
                        if len(str(pin)) == 1:
                                StrPin = "00"+str(pin)
                                pins.append(StrPin)
                                pin +=1
                        elif len(str(pin)) == 2:
                                StrPin = "0"+str(pin)
                                pins.append(StrPin)
                                pin +=1
                        elif len(str(pin)) == 3:
                                pins.append(str(pin))
                                pin +=1
                else:
                        pin +=1

        return pins


#Find's wich command use in the captured packet, 
def CommandFind(pkt):
    packet = str(pkt.encode('hex'))
    for button in commands: #For each key in commands
        value = commands[str(button)] 
        for i in value: #Each value is a list of 2
            if re.search(i, packet):
                return str(button) #Once re returns true, it returns the current key from the loop


#TX's commands to the TouchTunes Juke Box
def SendTX(pin, command):
        preamble = 'ffff00a2888a2'
        TX = preamble+pin+command



                  
#Sets modes for the Yard Stick One and prints results
def scan(d):
        d.setFreq(433.92e6)
        d.setMdmModulation(MOD_ASK_OOK)
        d.setMdmDRate(1766)
        d.setPktPQT(0)
        d.setMdmSyncMode(2)
        d.setMdmSyncWord(0x0000ffff) #FFFF is the beging of the preamble and won't be displayed, rflib assumes you know it's there when you set this variable.
        d.setMdmNumPreamble(0)
        d.setMaxPower()
        d.makePktFLEN(16)

        while not keystop():
                try:
                        pkt, ts = d.RFrecv() #RX packet and timestamp
                        if VerifyPkt(pkt):
                                PinList = PinFind(pkt)
                                if len(PinList) > 1:
                                        pins = PinList[0]+' or '+PinList[1]
                                else:
                                        pins = PinList[0]
                                        
                                command = CommandFind(pkt)
                                time = datetime.datetime.fromtimestamp(ts).strftime('%H:%M:%S')
                                packet = str(pkt.encode('hex'))


                                print "<*> %s: TX:ffff%s PIN:%s  Command: %s"  % (time,packet,pins,command) 

                except ChipconUsbTimeoutException:
                        pass
print(banner)
scan(d)
