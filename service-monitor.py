#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os
from time import sleep, time
import sys
import signal

service_timeouts = {
    'hmi-mainfu.service'            : 4.5,
    'hmi-phonefu.service'           : 4.5,
    'hmi-displaysettingsfu.service' : 4.5,
}

class Service:
    def __init__(self, name, timeout):
        self.name=name
        self.timeout=timeout
        self.uninit()

    def uninit(self):
        self.activating_time = None
        self.coredumped = False
        self.mainpid = None

    def prop(self, propname):
        return os.popen('systemctl --no-pager show {} --property {} --value'.format(self.name, propname)).read().rstrip()

    def check(self):
        state = self.prop('ActiveState')
        curtime = time()
        if (self.activating_time is None) and state == 'activating':
            print('Activating service {}'.format(self.name))
            self.activating_time = curtime
            self.mainpid = int(self.prop('MainPID'))
        elif (self.activating_time is not None) and state == 'active':
            print('Service {} is active'.format(self.name))
            self.activating_time = None
        elif state == 'inactive' and self.coredumped:
            print('Service {} is inactive'.format(self.name))
            self.uninit()

        if state == 'activating' and (curtime - self.activating_time > self.timeout) and not self.coredumped:
            self.coredumped = True
            self.dump()

    def dump(self):
        print('Initiating {} coredump'.format(self.name))
        os.kill(self.mainpid, signal.SIGSEGV)

services = [Service(s, t) for s, t in service_timeouts.items()]

while True:
    for s in services:
        s.check()
    sys.stdout.flush()
    sleep(.1)
