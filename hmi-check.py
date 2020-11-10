#!/usr/bin/env python
# -*- coding: utf-8 -*-

import unbuffered
import os, re
from collections import namedtuple

FU = namedtuple('FU',['fuclass','fuid','fil'])
FUs = {
    0 : FU("AudioManager"    , 101, "Main"            ),
    1 : FU("AudioPlayer"     , 245, "Media"           ),
    2 : FU("BTConnection"    , 153, "Main"            ),
    3 : FU("Clock"           , 137, "Clock"           ),
    4 : FU("Configuration"   ,   2, "Configuration"   ),
    5 : FU("Lifecycle"       ,  66, "Lifecycle"       ),
    6 : FU("Miracast"        ,  37, "Projection"      ),
    7 : FU("Phone"           , 150, "Phone"           ),
    8 : FU("Projection"      , 110, "Projection"      ),
    9 : FU("SDLApplications" ,  12, "Projection"      ),
    10: FU("Settings"        ,   1, "Main"            ),
    11: FU("Tuner"           , 102, "Tuner"           ),
    12: FU("VideoPlayer"     ,  13, "Media"           ),
    13: FU("DisplaySettings" ,  21, "DisplaySettings" ), 
    14: FU("ImagePlayer"     ,  14, "Media"           ),
    15: FU("PhoneCalls"      , 152, "Phone"           ),
    16: FU("QuickAccessHub"  ,   5, "Main"            ),
    17: FU("RPAS"            , 111, "VehicleData"     ),
    18: FU("Security"        ,  20, "Security"        ),
    19: FU("VehicleData"     ,   3, "VehicleData"     ),
    20: FU("VehicleVariant"  , 248, "VehicleData"     ),
}

ConnectedCommand = 'dlt-receive -a localhost|grep -e "fu::Lifecycle::doNotifyFUConnectedAction(U32) FU:"'
ConnectedRegex = r".*fu::Lifecycle::doNotifyFUConnectedAction(U32) FU: (\d+).*"

def check_fu_connected():
    connected = set()
    for s in os.popen(ConnectedCommand):
        m = re.match(ConnectedRegex, s.rstrip())
        if m:
             connected.add(int(m.group(1)))

    fils = set()
    for i in FUs.keys():
        if i not in connected:
            print("fuclass {} is not connected to hmi (fil:{})".format(FUs[i].fuclass, FUs[i].fil))
            fils.add(FUs[i].fil)

    for fil in fils:
        print("Initiating core dump service HMI-{}FU".format(fil))
        os.system('killall -s SIGSEGV HMI-{}FU'.format(fil))
