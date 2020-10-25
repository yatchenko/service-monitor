#!/usr/bin/env python
# -*- coding: utf-8 -*-

import ctypes, os
from time import sleep

service_configs = [
    ('hmi-mainfu.service'  ,  7.0, ['pas-daemon.service']),
    #('hmi-phonefu.service' ,  4.9, ['pas-daemon.service']),
]

class Unbuffered(object):
   def __init__(self, stream):
       self.stream = stream
   def write(self, data):
       self.stream.write(data)
       self.stream.flush()
   def writelines(self, datas):
       self.stream.writelines(datas)
       self.stream.flush()
   def __getattr__(self, attr):
       return getattr(self.stream, attr)

import sys
sys.stdout = Unbuffered(sys.stdout)

## Monotonic time
CLOCK_MONOTONIC_RAW = 4 # see <linux/time.h>

class timespec(ctypes.Structure):
    _fields_ = [
        ('tv_sec', ctypes.c_long),
        ('tv_nsec', ctypes.c_long)
    ]

librt = ctypes.CDLL('librt.so.1', use_errno=True)
clock_gettime = librt.clock_gettime
clock_gettime.argtypes = [ctypes.c_int, ctypes.POINTER(timespec)]

def monotonic():
    t = timespec()
    if clock_gettime(CLOCK_MONOTONIC_RAW , ctypes.pointer(t)) != 0:
        errno_ = ctypes.get_errno()
        raise OSError(errno_, os.strerror(errno_))
    return t.tv_sec + t.tv_nsec * 1.0e-9
##

class Service:
    def __init__(self, name, timeout, add_dumps=None):
        self.name=name
        self.timeout=timeout
        self.add_dumps=add_dumps
        self.set_inactive()

    def set_inactive(self):
        self.activating_time = None
        self.coredumped = False
        self.mainpid = None
        self.state = 'inactive'

    def prop(self, propname):
        return os.popen('systemctl --no-pager show {} --property {} --value'.format(self.name, propname)).read().rstrip()

    def update_state(self):
        state = self.prop('ActiveState')
        if self.state != state:
            self.state = state
            self.on_state_changed()

    def on_state_changed(self):
        if self.state == 'activating':
            print('Activating service {}'.format(self.name))
            self.activating_time = monotonic()
            self.mainpid = int(self.prop('MainPID'))
        elif self.state == 'active':
            print('Service {} is active'.format(self.name))
            self.activating_time = None
        elif self.state == 'inactive':
            print('Service {} is inactive'.format(self.name))
            self.set_inactive()

    def check(self):
        if self.state == 'activating' and (monotonic() - self.activating_time > self.timeout) and not self.coredumped:
            self.coredumped = True
            self.dump()

    def dump(self):
        if self.add_dumps:
            for s in self.add_dumps:
                print('Initiating {} coredump [{}]'.format(s, self.name))
                os.system('systemctl kill -s SIGSEGV {} --kill-who=main'.format(s))
        sleep(2)
        print('Initiating {} coredump'.format(self.name))
        os.system('systemctl kill -s SIGSEGV {} --kill-who=main'.format(self.name))
        #os.kill(self.mainpid, signal.SIGSEGV)

services = [Service(*c) for c in service_configs]

while True:
    for s in services:
        s.update_state()
        s.check()
    sleep(.2)
